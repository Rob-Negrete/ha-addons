import base64
import io
import logging
import os
import sys
import time
import uuid
from typing import Any, Dict, List, Optional

import cv2
import faiss
import numpy as np
from insightface.app import FaceAnalysis
from PIL import Image
from tinydb import Query, TinyDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Configuración de rutas (con soporte para variables de entorno para testing)
BASE_PATH = os.environ.get(
    "FACE_REKON_BASE_PATH", "/config/face-rekon/faces"
)  # noqa: E501
UNKNOWN_PATH = os.environ.get(
    "FACE_REKON_UNKNOWN_PATH", "/config/face-rekon/unknowns"
)  # noqa: E501
DB_PATH = os.environ.get(
    "FACE_REKON_DB_PATH", "/config/face-rekon/db/tinydb.json"
)  # noqa: E501
FAISS_INDEX_PATH = os.environ.get(
    "FACE_REKON_FAISS_INDEX_PATH", "/config/face-rekon/db/faiss_index.index"
)
MAPPING_PATH = os.environ.get(
    "FACE_REKON_MAPPING_PATH", "/config/face-rekon/db/faiss_id_map.npy"
)
THUMBNAIL_SIZE = (160, 160)

# Face quality thresholds
MIN_FACE_SIZE = int(
    os.environ.get("FACE_REKON_MIN_FACE_SIZE", "50")
)  # Minimum face width/height in pixels
MIN_BLUR_THRESHOLD = float(
    os.environ.get("FACE_REKON_MIN_BLUR_THRESHOLD", "50.0")
)  # Laplacian variance threshold
MIN_DETECTION_CONFIDENCE = float(
    os.environ.get("FACE_REKON_MIN_DETECTION_CONFIDENCE", "0.5")
)  # InsightFace confidence
MIN_QUALITY_SCORE = float(
    os.environ.get("FACE_REKON_MIN_QUALITY_SCORE", "0.3")
)  # Overall quality threshold (0.0-1.0)

# Inicializar InsightFace
logger.info("🚀 Initializing InsightFace...")
try:
    app = FaceAnalysis(allowed_modules=["detection", "recognition"])
    logger.info("✅ FaceAnalysis instance created")
    app.prepare(ctx_id=0, det_size=(640, 640))
    logger.info("✅ InsightFace prepared successfully")
except Exception as e:
    logger.error(f"❌ InsightFace initialization failed: {e}")
    logger.exception("InsightFace initialization exception:")
    raise

# TinyDB
db = TinyDB(DB_PATH)
Face = Query()

# Cargar o crear índice FAISS
dimension = 512
if os.path.exists(FAISS_INDEX_PATH):
    index = faiss.read_index(FAISS_INDEX_PATH)
    id_map = np.load(MAPPING_PATH).tolist()
else:
    index = faiss.IndexFlatL2(dimension)
    id_map = []


# Extraer vector facial
def extract_face_embedding(image_path: str) -> Optional[np.ndarray]:
    # Carga la imagen desde disco
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print(f"No se pudo leer la imagen: {image_path}")
        return None

    # Convierte BGR (OpenCV) a RGB (InsightFace)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Llama a InsightFace con el array
    faces = app.get(img_rgb)
    if faces:
        return faces[0].embedding
    return None


# Extraer todos los vectores faciales de una imagen
def extract_all_face_embeddings(image_path: str) -> List[np.ndarray]:
    # Carga la imagen desde disco
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print(f"No se pudo leer la imagen: {image_path}")
        return []

    # Convierte BGR (OpenCV) a RGB (InsightFace)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Llama a InsightFace con el array
    faces = app.get(img_rgb)
    return [face.embedding for face in faces] if faces else []


# Calcular calidad de la imagen (detectar blur)
def calculate_blur_score(image_crop: np.ndarray) -> float:
    """Calculate blur score using Laplacian variance

    Args:
        image_crop: RGB image array

    Returns:
        Blur score (higher = less blurry, lower = more blurry)
    """
    # Convert to grayscale for blur detection
    gray = cv2.cvtColor(image_crop, cv2.COLOR_RGB2GRAY)

    # Calculate Laplacian variance
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    return float(laplacian_var)


# Evaluar calidad general del rostro
def assess_face_quality(
    image_array: np.ndarray, bbox: List[int], det_score: float = 1.0
) -> Dict[str, float]:
    """Assess the overall quality of a detected face

    Args:
        image_array: RGB image array
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        det_score: Detection confidence from InsightFace

    Returns:
        Dictionary with quality metrics:
        - size_score: Face size quality (0.0-1.0)
        - blur_score: Image sharpness score (0.0-1.0)
        - detection_score: InsightFace confidence (0.0-1.0)
        - overall_score: Combined quality score (0.0-1.0)
    """
    x1, y1, x2, y2 = bbox
    height, width = image_array.shape[:2]

    # 1. Size Score - Larger faces are usually better quality
    face_width = x2 - x1
    face_height = y2 - y1
    face_area = face_width * face_height
    image_area = width * height

    # Face should be at least 2% of image area for good quality
    size_ratio = face_area / image_area
    size_score = min(
        1.0, size_ratio / 0.02
    )  # Normalize to 0.02 = perfect score  # noqa: E501

    # Also check minimum absolute size
    min_dimension = min(face_width, face_height)
    if min_dimension < MIN_FACE_SIZE:
        size_score *= min_dimension / MIN_FACE_SIZE

    # 2. Blur Score - Extract face crop and check sharpness
    # Add padding for better blur assessment
    padding = 10
    x1_padded = max(0, x1 - padding)
    y1_padded = max(0, y1 - padding)
    x2_padded = min(width, x2 + padding)
    y2_padded = min(height, y2 + padding)

    face_crop = image_array[y1_padded:y2_padded, x1_padded:x2_padded]

    if face_crop.size > 0:
        blur_variance = calculate_blur_score(face_crop)
        # Normalize blur score (50.0 = threshold for "acceptable" sharpness)
        blur_score = min(1.0, blur_variance / MIN_BLUR_THRESHOLD)
    else:
        blur_score = 0.0

    # 3. Detection Score - Use InsightFace confidence directly
    detection_score = float(det_score)

    # 4. Overall Score - Weighted combination
    # Size: 30%, Blur: 40%, Detection: 30%
    overall_score = (
        (size_score * 0.3) + (blur_score * 0.4) + (detection_score * 0.3)
    )  # noqa: E501

    return {
        "size_score": round(size_score, 3),
        "blur_score": round(blur_score, 3),
        "detection_score": round(detection_score, 3),
        "overall_score": round(overall_score, 3),
    }


# Extraer crops individuales de rostros con metadatos
def load_image_robust(image_path: str):
    """Load image using multiple methods to support all formats including WEBP"""  # noqa: E501
    import logging

    logger = logging.getLogger(__name__)

    # Try OpenCV first (fastest)
    try:
        img_bgr = cv2.imread(image_path)
        if img_bgr is not None:
            logger.info(f"✅ Loaded image with OpenCV: {image_path}")
            return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    except Exception as e:
        logger.warning(f"⚠️ OpenCV failed to load {image_path}: {e}")

    # Try PIL/Pillow as fallback (supports WEBP)
    try:
        import numpy as np
        from PIL import Image

        pil_image = Image.open(image_path)
        # Convert to RGB if not already
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Convert PIL to numpy array
        img_rgb = np.array(pil_image)
        logger.info(f"✅ Loaded image with PIL: {image_path}")
        return img_rgb

    except Exception as e:
        logger.error(f"❌ PIL failed to load {image_path}: {e}")
        return None


def extract_face_crops(
    image_path: str, filter_quality: bool = True
) -> List[Dict[str, Any]]:
    """Extract individual face crops from image with metadata and quality filtering  # noqa: E501

    Args:
        image_path: Path to the image file
        filter_quality: Whether to filter out low-quality faces (default: True)

    Returns:
        List of dictionaries containing face crop data:
        - face_index: Face number within image (0, 1, 2...)
        - face_bbox: Bounding box coordinates [x1, y1, x2, y2]
        - face_crop: Base64-encoded cropped face image
        - embedding: Face embedding vector
        - quality_metrics: Quality assessment scores
    """
    import logging

    logger = logging.getLogger(__name__)

    # Load image with robust method that supports WEBP
    img_rgb = load_image_robust(image_path)
    if img_rgb is None:
        logger.error(f"❌ Failed to load image: {image_path}")
        print(f"No se pudo leer la imagen: {image_path}")
        return []

    logger.info(f"🖼️ Image loaded successfully: {img_rgb.shape}")
    print(f"Imagen cargada: {img_rgb.shape}")

    # Llama a InsightFace con el array
    logger.info(f"🔍 Running InsightFace detection on image: {img_rgb.shape}")
    logger.info(
        f"📊 Image dtype: {img_rgb.dtype}, min: {img_rgb.min()}, max: {img_rgb.max()}"  # noqa: E501
    )

    try:
        faces = app.get(img_rgb)
        logger.info(f"👥 InsightFace detected {len(faces)} faces")
        logger.info(
            f"📊 Faces details: {[getattr(f, 'bbox', 'no bbox') for f in faces]}"  # noqa: E501
        )
    except Exception as e:
        logger.error(f"❌ InsightFace detection failed: {e}")
        logger.exception("InsightFace exception details:")
        return []
    if not faces:
        logger.warning("⚠️ No faces detected by InsightFace")
        return []

    face_crops = []
    faces_processed = 0
    faces_filtered = 0

    for i, face in enumerate(faces):
        # Obtener bounding box y convertir a enteros
        bbox = [int(coord) for coord in face.bbox]

        # Obtener score de detección si está disponible
        det_score = getattr(face, "det_score", 1.0)

        # Evaluar calidad del rostro
        quality_metrics = assess_face_quality(img_rgb, bbox, det_score)

        faces_processed += 1

        # Filtrar por calidad si está habilitado
        if (
            filter_quality and quality_metrics["overall_score"] < MIN_QUALITY_SCORE
        ):  # noqa: E501
            faces_filtered += 1
            print(
                f"Rostro {i} filtrado por baja calidad: "
                f"score={quality_metrics['overall_score']:.3f} "
                f"(blur={quality_metrics['blur_score']:.3f}, "
                f"size={quality_metrics['size_score']:.3f})"
            )
            continue

        # Generar thumbnail del crop facial
        face_thumbnail = generate_face_thumbnail(img_rgb, bbox)

        face_crops.append(
            {
                "face_index": i,
                "face_bbox": bbox,
                "face_crop": face_thumbnail,
                "embedding": face.embedding,
                "quality_metrics": quality_metrics,
            }
        )

    if faces_filtered > 0:
        print(
            f"Procesados {faces_processed} rostros, "
            f"filtrados {faces_filtered} por baja calidad"
        )

    return face_crops


# Generar thumbnail de un crop facial específico
def generate_face_thumbnail(
    image_array: np.ndarray, bbox: List[int], padding: int = 20
) -> str:
    """Generate base64 thumbnail from face crop with padding

    Args:
        image_array: RGB image array from OpenCV/PIL
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        padding: Pixels to add around face crop (default: 20)

    Returns:
        Base64-encoded JPEG thumbnail string
    """
    x1, y1, x2, y2 = bbox
    height, width = image_array.shape[:2]

    # Agregar padding con límites de imagen
    x1_padded = max(0, x1 - padding)
    y1_padded = max(0, y1 - padding)
    x2_padded = min(width, x2 + padding)
    y2_padded = min(height, y2 + padding)

    # Extraer crop facial
    face_crop = image_array[y1_padded:y2_padded, x1_padded:x2_padded]

    # Convertir a PIL Image
    pil_image = Image.fromarray(face_crop)

    # Redimensionar manteniendo aspecto y crear cuadrado
    pil_image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

    # Crear imagen cuadrada con fondo negro
    square_image = Image.new("RGB", THUMBNAIL_SIZE, (0, 0, 0))

    # Centrar la imagen redimensionada
    offset_x = (THUMBNAIL_SIZE[0] - pil_image.width) // 2
    offset_y = (THUMBNAIL_SIZE[1] - pil_image.height) // 2
    square_image.paste(pil_image, (offset_x, offset_y))

    # Convertir a base64
    buffered = io.BytesIO()
    square_image.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# Crear thumbnail base64
def generate_thumbnail(image_path: str) -> str:
    img = Image.open(image_path)
    img.thumbnail(THUMBNAIL_SIZE)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# Guardar rostro desconocido (legacy function - maintains backward compatibility)  # noqa: E501
def save_unknown_face(image_path: str, event_id: str) -> None:
    embedding = extract_face_embedding(image_path)
    if embedding is None:
        print("No se detectó rostro.")
        return

    thumbnail = generate_thumbnail(image_path)
    timestamp = int(time.time())
    face_id = str(uuid.uuid4())

    # Insertar en TinyDB with legacy schema
    db.insert(
        {
            "face_id": face_id,
            "event_id": event_id,
            "timestamp": timestamp,
            "image_path": image_path,
            "embedding": embedding.tolist(),
            "thumbnail": thumbnail,
            "name": None,
            "relationship": "unknown",
            "confidence": "unknown",
            # New fields for backward compatibility
            "face_bbox": None,
            "face_index": 0,
        }
    )

    # Insertar en FAISS e ID map
    index.add(np.array([embedding], dtype=np.float32))
    id_map.append(face_id)

    # Guardar índice y map
    faiss.write_index(index, FAISS_INDEX_PATH)
    np.save(MAPPING_PATH, np.array(id_map))

    print("Rostro guardado con ID:", face_id)


# Guardar múltiples rostros desconocidos de una imagen
def save_multiple_faces(image_path: str, event_id: str) -> List[str]:
    """Save each detected face as separate database entry

    Args:
        image_path: Path to the image file
        event_id: Event identifier from Frigate

    Returns:
        List of face_ids for the saved faces
    """
    face_crops = extract_face_crops(image_path)
    if not face_crops:
        print("No se detectaron rostros.")
        return []

    saved_face_ids = []
    timestamp = int(time.time())

    for face_data in face_crops:
        face_id = str(uuid.uuid4())

        # Insertar en TinyDB with enhanced schema
        db.insert(
            {
                "face_id": face_id,
                "event_id": event_id,
                "timestamp": timestamp,
                "image_path": image_path,
                "embedding": face_data["embedding"].tolist(),
                "thumbnail": face_data[
                    "face_crop"
                ],  # Now contains cropped face  # noqa: E501
                "name": None,
                "relationship": "unknown",
                "confidence": "unknown",
                # New fields for face extraction
                "face_bbox": face_data["face_bbox"],
                "face_index": face_data["face_index"],
                # Quality metrics
                "quality_metrics": face_data.get("quality_metrics", {}),
            }
        )

        # Insertar en FAISS e ID map
        index.add(np.array([face_data["embedding"]], dtype=np.float32))
        id_map.append(face_id)
        saved_face_ids.append(face_id)

        print(f"Rostro {face_data['face_index']} guardado con ID: {face_id}")

    # Guardar índice y map una sola vez
    faiss.write_index(index, FAISS_INDEX_PATH)
    np.save(MAPPING_PATH, np.array(id_map))

    print(
        f"Total de {len(saved_face_ids)} rostros guardados para evento {event_id}"
    )  # noqa: E501
    return saved_face_ids


# Identificar rostro
def identify_face(image_path: str) -> Optional[Dict[str, Any]]:
    embedding = extract_face_embedding(image_path)
    if embedding is None:
        print("No se detectó rostro.")
        return None

    distances, indices = index.search(
        np.array([embedding], dtype=np.float32), 1
    )  # noqa: E501
    if distances[0][0] < 0.5:
        face_id = id_map[indices[0][0]]
        matched = db.get(Face.face_id == face_id)
        if matched:
            print(f"Identificado: {matched.get('name', matched['face_id'])}")
            return matched
    print("Rostro no identificado.")
    return None


# Identificar todos los rostros en una imagen
def identify_all_faces(image_path: str) -> List[Dict[str, Any]]:
    """Identify all faces in an image with enhanced face crop information

    Args:
        image_path: Path to the image file

    Returns:
        List of dictionaries containing identification results with face crops:
        - face_index: Face number within image (0, 1, 2...)
        - status: "identified" or "unknown"
        - face_data: Matched face database entry (if identified)
        - confidence: Recognition confidence (0.0-1.0)
        - face_bbox: Bounding box coordinates [x1, y1, x2, y2]
        - face_crop: Base64-encoded cropped face image
    """
    # Get face crops with full metadata
    face_crops = extract_face_crops(image_path)
    if not face_crops:
        print("No se detectaron rostros.")
        return []

    results = []
    for face_data in face_crops:
        embedding = face_data["embedding"]
        face_index = face_data["face_index"]

        # Search for matches in FAISS index
        distances, indices = index.search(
            np.array([embedding], dtype=np.float32), 1
        )  # noqa: E501
        if distances[0][0] < 0.5:
            face_id = id_map[indices[0][0]]
            matched = db.get(Face.face_id == face_id)
            if matched:
                results.append(
                    {
                        "face_index": face_index,
                        "status": "identified",
                        "face_data": matched,
                        "confidence": float(1.0 - distances[0][0]),
                        "face_bbox": face_data["face_bbox"],
                        "face_crop": face_data["face_crop"],
                        "quality_metrics": face_data.get(
                            "quality_metrics", {}
                        ),  # noqa: E501
                    }
                )
                matched_face = matched.get("name", matched["face_id"])
                quality_score = face_data.get("quality_metrics", {}).get(
                    "overall_score", "N/A"
                )
                print(
                    f"Rostro {face_index}: Identificado como {matched_face} "
                    f"(calidad: {quality_score})"
                )
            else:
                results.append(
                    {
                        "face_index": face_index,
                        "status": "unknown",
                        "face_data": None,
                        "confidence": 0.0,
                        "face_bbox": face_data["face_bbox"],
                        "face_crop": face_data["face_crop"],
                        "quality_metrics": face_data.get(
                            "quality_metrics", {}
                        ),  # noqa: E501
                    }
                )
                quality_score = face_data.get("quality_metrics", {}).get(
                    "overall_score", "N/A"
                )
                print(
                    f"Rostro {face_index}: No identificado (calidad: {quality_score})"  # noqa: E501
                )
        else:
            results.append(
                {
                    "face_index": face_index,
                    "status": "unknown",
                    "face_data": None,
                    "confidence": 0.0,
                    "face_bbox": face_data["face_bbox"],
                    "face_crop": face_data["face_crop"],
                    "quality_metrics": face_data.get("quality_metrics", {}),
                }
            )
            quality_score = face_data.get("quality_metrics", {}).get(
                "overall_score", "N/A"
            )
            print(
                f"Rostro {face_index}: No identificado (calidad: {quality_score})"
            )  # noqa: E501

    return results


# Obtener rostros desconocidos
def get_unclassified_faces() -> List[Dict[str, Any]]:
    unclassified = [
        {
            "face_id": face["face_id"],
            "event_id": face.get("event_id", None),
            "image_path": face.get("image_path", None),
            "thumbnail": face.get("thumbnail", None),
            "relationship": "unknown",
            "confidence": "unknown",
            "name": face.get("name", None),
        }
        for face in db.all()
        if not face.get("name")
    ]

    return unclassified


# Guardar rostro ya identificado
def update_face(face_id: str, data: Dict[str, str]) -> None:
    """Update a face's details"""
    db.update(
        {
            "name": data["name"],
            "relationship": data["relationship"],
            "confidence": data["confidence"],
        },
        Face.face_id == face_id,
    )


# Obtiene un rostro por su id
def get_face(face_id: str) -> Optional[Dict[str, Any]]:
    """Get a face"""
    return db.search(Face.face_id == face_id)


# Función para testing y debug de calidad facial
def test_face_quality(image_path: str) -> None:
    """Test face quality assessment on an image for debugging

    Args:
        image_path: Path to the image file
    """
    print(f"\n=== Analizando calidad facial en: {image_path} ===")

    # Extraer rostros sin filtro para ver todos
    all_faces = extract_face_crops(image_path, filter_quality=False)
    print(f"Total de rostros detectados: {len(all_faces)}")

    for i, face_data in enumerate(all_faces):
        quality = face_data.get("quality_metrics", {})
        bbox = face_data["face_bbox"]

        print(f"\nRostro {i}:")
        print(f"  Bounding box: {bbox}")
        print(f"  Tamaño: {bbox[2]-bbox[0]}x{bbox[3]-bbox[1]} pixels")
        print(f"  Calidad general: {quality.get('overall_score', 'N/A'):.3f}")
        print(f"  Score de tamaño: {quality.get('size_score', 'N/A'):.3f}")
        print(f"  Score de nitidez: {quality.get('blur_score', 'N/A'):.3f}")
        print(
            f"  Score de detección: {quality.get('detection_score', 'N/A'):.3f}"
        )  # noqa: E501

        if quality.get("overall_score", 0) < MIN_QUALITY_SCORE:
            print(
                f"  ❌ FILTRADO: Calidad inferior al umbral ({MIN_QUALITY_SCORE})"
            )  # noqa: E501
        else:
            print(
                f"  ✅ ACEPTADO: Calidad superior al umbral ({MIN_QUALITY_SCORE})"
            )  # noqa: E501

    # Ahora extraer con filtro habilitado
    print("\n--- Extracción con filtro de calidad habilitado ---")
    filtered_faces = extract_face_crops(image_path, filter_quality=True)
    print(f"Rostros aceptados después del filtro: {len(filtered_faces)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Modo de testing de calidad
        test_image = (
            sys.argv[2]
            if len(sys.argv) > 2
            else "/config/face-rekon/images/new_face.jpg"
        )
        test_face_quality(test_image)
    else:
        # Modo normal
        new_image_path = "/config/face-rekon/images/new_face.jpg"
        result = identify_face(new_image_path)
        if not result:
            save_unknown_face(new_image_path, "main_event")
