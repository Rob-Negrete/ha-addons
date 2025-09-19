import base64
import io
import logging
import os
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

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

# Qdrant vector database support
try:
    from qdrant_adapter import get_qdrant_adapter

    QDRANT_AVAILABLE = True
    logger.info("✅ Qdrant adapter available")
except ImportError as e:
    QDRANT_AVAILABLE = False
    logger.warning(f"⚠️ Qdrant adapter not available: {e}")

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
THUMBNAIL_PATH = os.environ.get(
    "FACE_REKON_THUMBNAIL_PATH", "/config/face-rekon/thumbnails"
)  # noqa: E501

# Storage optimization configuration
USE_OPTIMIZED_STORAGE = (
    os.environ.get("FACE_REKON_USE_OPTIMIZED_STORAGE", "true").lower() == "true"
)

# Database backend selection
USE_QDRANT = (
    os.environ.get("FACE_REKON_USE_QDRANT", "true").lower() == "true"
    and QDRANT_AVAILABLE
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

# Face recognition similarity threshold (lower = more permissive matching)
FACE_SIMILARITY_THRESHOLD = float(
    os.environ.get("FACE_REKON_SIMILARITY_THRESHOLD", "0.35")
)  # Distance threshold for face matching (0.0-1.0, default: 0.35)

# Time-based deduplication window (seconds)
DEDUPLICATION_WINDOW = int(
    os.environ.get("FACE_REKON_DEDUPLICATION_WINDOW", "60")
)  # Skip saving faces detected within this window

# Borderline match threshold for smart grouping suggestions
BORDERLINE_THRESHOLD = float(
    os.environ.get("FACE_REKON_BORDERLINE_THRESHOLD", "0.50")
)  # Suggest grouping between SIMILARITY and BORDERLINE thresholds

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


# TinyDB with robust error handling and recovery
def initialize_database_with_recovery():
    """Initialize TinyDB with corruption recovery mechanism"""
    global db, Face

    # Ensure database directory exists (with fallback for testing environments)
    db_dir = os.path.dirname(DB_PATH)
    try:
        os.makedirs(db_dir, exist_ok=True)
    except (OSError, PermissionError) as e:
        # In testing/CI environments, /config may be read-only
        logger.warning(f"⚠️ Could not create database directory {db_dir}: {e}")
        if not os.path.exists(DB_PATH):
            # For tests, just skip database initialization but still create Face query
            logger.info("📝 Skipping database initialization for testing environment")
            # Initialize Face query object for testing
            Face = Query()
            return

    try:
        # Try to initialize normally
        logger.info(f"🔍 Initializing database: {DB_PATH}")
        db = TinyDB(DB_PATH)

        # Test if database is readable by attempting to read all records
        _ = db.all()
        logger.info("✅ Database initialized successfully")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.info("🔧 Attempting database recovery...")

        # Create backup of corrupted file
        backup_path = f"{DB_PATH}.corrupted.{int(time.time())}"
        try:
            if os.path.exists(DB_PATH):
                import shutil

                shutil.copy2(DB_PATH, backup_path)
                logger.info(
                    f"📦 Backed up corrupted database to: {backup_path}"
                )  # noqa: E501
        except Exception as backup_error:
            logger.warning(
                f"⚠️ Failed to backup corrupted database: {backup_error}"
            )  # noqa: E501

        # Try to recover data from corrupted JSON
        recovered_data = recover_database_data(DB_PATH)

        # Remove corrupted file and create fresh database
        try:
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
                logger.info("🗑️ Removed corrupted database file")
        except Exception as remove_error:
            logger.warning(
                f"⚠️ Failed to remove corrupted file: {remove_error}"
            )  # noqa: E501

        # Initialize fresh database
        db = TinyDB(DB_PATH)
        logger.info("🆕 Created fresh database")

        # Restore recovered data if any
        if recovered_data:
            logger.info(
                f"🔄 Restoring {len(recovered_data)} recovered records..."
            )  # noqa: E501
            for record in recovered_data:
                try:
                    db.insert(record)
                except Exception as insert_error:
                    logger.warning(
                        f"⚠️ Failed to restore record: {insert_error}"
                    )  # noqa: E501
            logger.info("✅ Database recovery completed")
        else:
            logger.warning(
                "⚠️ No data could be recovered - starting with empty database"
            )

    Face = Query()


def recover_database_data(db_path: str) -> list:
    """Attempt to recover data from corrupted JSON database"""
    recovered_records = []

    if not os.path.exists(db_path):
        return recovered_records

    try:
        logger.info("🔍 Attempting to recover data from corrupted database...")

        # Read the raw file content
        with open(db_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Try to find the last valid JSON structure
        # Look for complete record patterns
        import re

        # Look for individual face records that might be valid
        # Pattern matches face records with required fields
        # face_pattern = (
        #     r'"face_id":\s*"[^"]+"|"event_id":\s*"[^"]+"|"embedding":\s*\[[^\]]+\]'
        # )
        # Try to extract the _default table if it exists and is valid
        default_match = re.search(
            r'"_default":\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', content
        )
        if default_match:
            logger.info("🔍 Found _default table structure")

            # Try to parse individual records within _default
            records_content = default_match.group(1)

            # Look for complete record entries (numbered keys with full record objects)  # noqa: E501
            record_pattern = r'"(\d+)":\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'  # noqa: E501
            record_matches = re.finditer(record_pattern, records_content)

            for match in record_matches:
                try:
                    record_json = "{" + match.group(2) + "}"
                    # Try to parse this individual record
                    import json

                    record_data = json.loads(record_json)

                    # Validate that it has required fields
                    if all(
                        field in record_data
                        for field in ["face_id", "event_id", "embedding"]
                    ):
                        recovered_records.append(record_data)
                        logger.info(
                            f"✅ Recovered record: {record_data.get('face_id', 'unknown')}"  # noqa: E501
                        )

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse potential record: {e}")
                    continue

        # If no structured recovery worked, try simpler pattern matching
        if not recovered_records:
            logger.info("🔍 Trying simple pattern-based recovery...")

            # Look for face_id patterns and try to extract surrounding data
            face_id_matches = re.finditer(r'"face_id":\s*"([^"]+)"', content)
            for match in face_id_matches:
                face_id = match.group(1)
                # Look around this face_id for a complete record
                start_pos = max(0, match.start() - 1000)
                end_pos = min(len(content), match.end() + 1000)
                surrounding_content = content[start_pos:end_pos]

                # Try to find record boundaries
                record_start = surrounding_content.rfind(
                    "{", 0, match.start() - start_pos
                )
                record_end = surrounding_content.find(  # noqa: E501
                    "}", match.end() - start_pos
                )

                if record_start != -1 and record_end != -1:
                    try:
                        potential_record = surrounding_content[
                            record_start : record_end + 1  # noqa: E203
                        ]
                        import json

                        record_data = json.loads(potential_record)

                        if (
                            "face_id" in record_data
                            and record_data["face_id"] == face_id
                        ):
                            recovered_records.append(record_data)
                            logger.info(
                                f"✅ Pattern-recovered record: {face_id}"
                            )  # noqa: E501

                    except Exception:
                        continue

        logger.info(
            f"🎯 Recovery completed: {len(recovered_records)} records recovered"
        )  # noqa: E501

    except Exception as e:
        logger.error(f"❌ Data recovery failed: {e}")

    return recovered_records


# Initialize database with recovery
initialize_database_with_recovery()


# Safe database operations to prevent corruption
def safe_db_insert(record_data: dict) -> bool:
    """Safely insert a record into the database with error handling"""
    max_retries = 3
    retry_delay = 0.1

    for attempt in range(max_retries):
        try:
            # Validate record has required fields
            required_fields = ["face_id", "event_id", "embedding"]
            if not all(field in record_data for field in required_fields):
                logger.error(
                    f"❌ Record missing required fields: {required_fields}"
                )  # noqa: E501
                return False

            # Insert the record
            doc_id = db.insert(record_data)
            logger.info(
                f"✅ Successfully inserted record {record_data.get('face_id')} with doc_id {doc_id}"  # noqa: E501
            )
            return True

        except Exception as e:
            logger.warning(f"⚠️ Insert attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error(
                    f"❌ Failed to insert record after {max_retries} attempts"
                )  # noqa: E501

                # If all retries failed, try to recover database
                logger.info(
                    "🔧 Triggering database recovery due to insert failure..."
                )  # noqa: E501
                try:
                    initialize_database_with_recovery()
                    # Try one more time with fresh database
                    doc_id = db.insert(record_data)
                    logger.info("✅ Insert succeeded after database recovery")
                    return True
                except Exception as recovery_error:
                    logger.error(
                        f"❌ Insert failed even after recovery: {recovery_error}"  # noqa: E501
                    )

    return False


def safe_db_all() -> list:
    """Safely retrieve all records from database with error handling"""
    try:
        return db.all()
    except Exception as e:
        logger.error(f"❌ Failed to read all records: {e}")
        logger.info("🔧 Triggering database recovery due to read failure...")

        try:
            initialize_database_with_recovery()
            return db.all()
        except Exception as recovery_error:
            logger.error(
                f"❌ Read failed even after recovery: {recovery_error}"
            )  # noqa: E501
            return []


def safe_db_search(query) -> list:
    """Safely search database with error handling"""
    try:
        return db.search(query)
    except Exception as e:
        logger.error(f"❌ Failed to search database: {e}")
        logger.info("🔧 Triggering database recovery due to search failure...")

        try:
            initialize_database_with_recovery()
            return db.search(query)
        except Exception as recovery_error:
            logger.error(
                f"❌ Search failed even after recovery: {recovery_error}"
            )  # noqa: E501
            return []


def safe_db_get(query):
    """Safely get a single record from database with error handling"""
    try:
        return db.get(query)
    except Exception as e:
        logger.error(f"❌ Failed to get record from database: {e}")
        logger.info("🔧 Triggering database recovery due to get failure...")

        try:
            initialize_database_with_recovery()
            return db.get(query)
        except Exception as recovery_error:
            logger.error(f"❌ Get failed even after recovery: {recovery_error}")
            return None


# Database backend initialization
dimension = 512
index = None
id_map = []
qdrant_adapter = None


def initialize_vector_database():
    """Initialize vector database backend (Qdrant or FAISS)."""
    global index, id_map, qdrant_adapter

    if USE_QDRANT:
        logger.info("🚀 Initializing Qdrant vector database")
        try:
            qdrant_adapter = get_qdrant_adapter()
            logger.info("✅ Qdrant adapter initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Qdrant: {e}")
            logger.info("🔄 Falling back to FAISS + TinyDB")
            _initialize_faiss()
    else:
        logger.info("🚀 Initializing FAISS + TinyDB")
        _initialize_faiss()


def _initialize_faiss():
    """Initialize FAISS index and mapping."""
    global index, id_map

    # Cargar o crear índice FAISS
    if os.path.exists(FAISS_INDEX_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
        id_map = np.load(MAPPING_PATH).tolist()
        logger.info(f"📂 Loaded FAISS index with {len(id_map)} faces")
    else:
        index = faiss.IndexFlatL2(dimension)
        id_map = []
        logger.info("🆕 Created new FAISS index")


# Initialize vector database
initialize_vector_database()


# Unified database interface functions
def db_save_face(face_data: Dict[str, Any], embedding: np.ndarray) -> str:
    """Save face with metadata and embedding using active backend."""
    if USE_QDRANT and qdrant_adapter:
        return qdrant_adapter.save_face(face_data, embedding)
    else:
        # FAISS + TinyDB fallback
        return _save_face_faiss(face_data, embedding)


def db_search_similar(
    embedding: np.ndarray, limit: int = 1
) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Search for similar faces using active backend."""
    if USE_QDRANT and qdrant_adapter:
        return qdrant_adapter.search_similar_faces(embedding, limit)
    else:
        # FAISS + TinyDB fallback
        return _search_similar_faiss(embedding, limit)


def db_get_face(face_id: str) -> Optional[Dict[str, Any]]:
    """Get face metadata by ID using active backend."""
    if USE_QDRANT and qdrant_adapter:
        return qdrant_adapter.get_face(face_id)
    else:
        # TinyDB fallback
        return safe_db_get(Face.face_id == face_id)


def db_update_face(face_id: str, updates: Dict[str, Any]) -> bool:
    """Update face metadata using active backend."""
    if USE_QDRANT and qdrant_adapter:
        return qdrant_adapter.update_face(face_id, updates)
    else:
        # TinyDB fallback
        return _update_face_tinydb(face_id, updates)


def db_get_unclassified_faces() -> List[Dict[str, Any]]:
    """Get unclassified faces using active backend."""
    if USE_QDRANT and qdrant_adapter:
        return qdrant_adapter.get_unclassified_faces()
    else:
        # TinyDB fallback
        return _get_unclassified_faces_tinydb()


def db_check_recent_detection(event_id: str) -> bool:
    """Check for recent detections using active backend."""
    if USE_QDRANT and qdrant_adapter:
        return qdrant_adapter.check_recent_detection(event_id)
    else:
        # TinyDB fallback
        return _check_recent_detection_tinydb(event_id)


# FAISS + TinyDB implementation functions
def _save_face_faiss(face_data: Dict[str, Any], embedding: np.ndarray) -> str:
    """Save face using FAISS + TinyDB."""
    face_id = face_data.get("face_id", str(uuid.uuid4()))

    # Add to FAISS index
    index.add(np.array([embedding], dtype=np.float32))
    id_map.append(face_id)

    # Save metadata to TinyDB
    if safe_db_insert(face_data):
        # Save FAISS index and mapping
        faiss.write_index(index, FAISS_INDEX_PATH)
        np.save(MAPPING_PATH, np.array(id_map))
        return face_id
    else:
        # Rollback FAISS changes if TinyDB fails
        if len(id_map) > 0:
            id_map.pop()
            # Note: FAISS doesn't support removing last vector easily
        raise Exception("Failed to save to TinyDB")


def _search_similar_faiss(
    embedding: np.ndarray, limit: int = 1
) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Search similar faces using FAISS."""
    distances, indices = index.search(np.array([embedding], dtype=np.float32), limit)

    results = []
    for i in range(len(distances[0])):
        if indices[0][i] != -1:  # Valid result
            distance = distances[0][i]
            face_id = id_map[indices[0][i]]
            metadata = safe_db_get(Face.face_id == face_id)
            if metadata:
                results.append((face_id, distance, metadata))

    return results


def _update_face_tinydb(face_id: str, updates: Dict[str, Any]) -> bool:
    """Update face in TinyDB."""
    try:
        db.update(updates, Face.face_id == face_id)
        return True
    except Exception as e:
        logger.error(f"❌ Failed to update face {face_id}: {e}")
        return False


def _get_unclassified_faces_tinydb() -> List[Dict[str, Any]]:
    """Get unclassified faces from TinyDB."""
    unclassified = []
    for face in safe_db_all():
        if face.get("name") == "unknown":
            # Add thumbnail if using optimized storage
            if USE_OPTIMIZED_STORAGE and face.get("thumbnail_path"):
                face["thumbnail"] = get_thumbnail_from_file(face["thumbnail_path"])
            unclassified.append(face)
    return unclassified


def _check_recent_detection_tinydb(event_id: str) -> bool:
    """Check recent detection using TinyDB."""
    if not DEDUPLICATION_WINDOW or DEDUPLICATION_WINDOW <= 0:
        return False

    current_time = int(time.time())
    recent_records = safe_db_search(
        (Face.event_id == event_id)
        & (Face.timestamp > current_time - DEDUPLICATION_WINDOW)
    )
    return len(recent_records) > 0


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
            filter_quality
            and quality_metrics["overall_score"] < MIN_QUALITY_SCORE  # noqa: E501
        ):
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


# OPTIMIZED STORAGE FUNCTIONS
def save_thumbnail_to_file(thumbnail_base64: str, face_id: str) -> str:
    """Save base64 thumbnail as JPEG file and return file path.

    Args:
        thumbnail_base64: Base64 encoded JPEG data
        face_id: Unique face identifier

    Returns:
        Path to saved thumbnail file
    """
    # Determine thumbnail directory
    thumbnail_dir = THUMBNAIL_PATH

    # Ensure thumbnail directory exists
    try:
        os.makedirs(thumbnail_dir, exist_ok=True)
    except (OSError, PermissionError) as e:
        logger.warning(f"⚠️ Could not create thumbnail directory {thumbnail_dir}: {e}")
        # Fallback to temp directory for testing environments
        thumbnail_dir = os.path.join("/tmp", "face_rekon_thumbnails")
        os.makedirs(thumbnail_dir, exist_ok=True)
        logger.info(f"📁 Using fallback thumbnail path: {thumbnail_dir}")

    # Create thumbnail file path
    thumbnail_file = f"{face_id}.jpg"
    thumbnail_path = os.path.join(thumbnail_dir, thumbnail_file)

    # Decode and save thumbnail
    try:
        thumbnail_data = base64.b64decode(thumbnail_base64)
        with open(thumbnail_path, "wb") as f:
            f.write(thumbnail_data)

        logger.info(f"💾 Saved thumbnail: {thumbnail_path}")
        return thumbnail_path

    except Exception as e:
        logger.error(f"❌ Failed to save thumbnail {face_id}: {e}")
        return ""


def get_thumbnail_from_file(thumbnail_path: str) -> Optional[str]:
    """Load thumbnail from file and return as base64.

    Args:
        thumbnail_path: Path to thumbnail file

    Returns:
        Base64 encoded JPEG data or None if file not found
    """
    if not thumbnail_path or not os.path.exists(thumbnail_path):
        return None

    try:
        with open(thumbnail_path, "rb") as f:
            thumbnail_data = f.read()
        return base64.b64encode(thumbnail_data).decode("utf-8")

    except Exception as e:
        logger.error(f"❌ Failed to load thumbnail {thumbnail_path}: {e}")
        return None


def create_optimized_face_record(
    face_data: Dict[str, Any],
    event_id: str,
    face_id: str,
    timestamp: int,
    faiss_index: int,
) -> Dict[str, Any]:
    """Create optimized TinyDB record with file references.

    Args:
        face_data: Face data from extract_face_crops
        event_id: Event identifier
        face_id: Unique face identifier
        timestamp: Unix timestamp
        faiss_index: Position in FAISS index

    Returns:
        Optimized database record (~0.5KB vs ~20KB)
    """
    # Save thumbnail to file
    thumbnail_path = save_thumbnail_to_file(face_data["face_crop"], face_id)

    # Create optimized record (metadata only)
    record = {
        "face_id": face_id,
        "event_id": event_id,
        "timestamp": timestamp,
        "name": None,
        "thumbnail_path": thumbnail_path,  # FILE REFERENCE
        "faiss_index": faiss_index,  # INDEX REFERENCE
        "face_bbox": face_data["face_bbox"],
        "face_index": face_data["face_index"],
        "quality_metrics": face_data.get("quality_metrics", {}),
        "relationship": "unknown",
        "confidence": "unknown",
        # Storage optimization metadata
        "storage_version": "optimized_v1",
        "created_with": "file_based_storage",
    }

    # Remove embedding duplication (stored only in FAISS)
    # Remove base64 thumbnail (stored as file)

    return record


def should_skip_recent_detection(event_id: str) -> bool:
    """Check if we should skip saving faces due to recent detection from same event.

    Args:
        event_id: Event identifier to check

    Returns:
        True if we should skip saving (recent detection found), False otherwise
    """
    if not DEDUPLICATION_WINDOW or DEDUPLICATION_WINDOW <= 0:
        return False

    try:
        # Get recent records from same event within time window
        current_time = int(time.time())
        recent_records = safe_db_search(
            (Face.event_id == event_id)
            & (Face.timestamp > current_time - DEDUPLICATION_WINDOW)
        )

        if recent_records:
            logger.info(
                f"🚫 Skipping face save - found {len(recent_records)} recent "
                f"detections for event {event_id} within {DEDUPLICATION_WINDOW}s"
            )
            return True

    except Exception as e:
        logger.warning(f"⚠️ Error checking recent detections: {e}")

    return False


def save_multiple_faces_optimized(image_path: str, event_id: str) -> List[str]:
    """Save faces using optimized storage with time-based deduplication.

    Args:
        image_path: Path to the image file
        event_id: Event identifier from Frigate

    Returns:
        List of face_ids for the saved faces

    Features:
        - Time-based deduplication (skip if recent detection from same event)
        - Configurable similarity threshold (default: 0.35 vs old 0.5)
        - Storage optimization (97% size reduction)
        - File-based thumbnails and FAISS-only embeddings
    """
    # Check for recent detections (customer's duplicate issue)
    if db_check_recent_detection(event_id):
        logger.info(f"🕒 Skipping save due to recent detection from event {event_id}")
        return []
    face_crops = extract_face_crops(image_path)
    if not face_crops:
        logger.info("🔍 No faces detected in image")
        return []

    saved_face_ids = []
    timestamp = int(time.time())

    logger.info(f"💾 Starting optimized storage for {len(face_crops)} faces")

    for face_data in face_crops:
        face_id = str(uuid.uuid4())

        # Create face record with metadata
        if USE_QDRANT and qdrant_adapter:
            # For Qdrant, create a complete face record
            record_data = {
                "face_id": face_id,
                "event_id": event_id,
                "timestamp": timestamp,
                "name": "unknown",
                "face_bbox": face_data.get("face_bbox", []),
                "quality_metrics": face_data.get("quality_metrics", {}),
                "confidence": 0.0,
                "notes": "",
            }

            # Save thumbnail to file for consistency
            if "face_crop" in face_data:
                thumbnail_path = save_thumbnail_to_file(face_data["face_crop"], face_id)
                record_data["thumbnail_path"] = thumbnail_path

        else:
            # For FAISS+TinyDB, use optimized storage format
            current_faiss_index = index.ntotal if index else 0
            record_data = create_optimized_face_record(
                face_data, event_id, face_id, timestamp, current_faiss_index
            )

        # Save using unified database interface
        try:
            saved_face_id = db_save_face(record_data, face_data["embedding"])
            saved_face_ids.append(saved_face_id)
            logger.info(
                f"✅ Saved face {face_data['face_index']} with ID: {saved_face_id}"
            )
        except Exception as e:
            logger.error(f"❌ Failed to save face {face_id}: {e}")
            continue

    logger.info(
        f"🎉 Optimized storage completed: {len(saved_face_ids)} faces "
        f"for event {event_id}"
    )
    return saved_face_ids


# Guardar rostro desconocido (legacy function - maintains backward compatibility)  # noqa: E501
def save_unknown_face(image_path: str, event_id: str) -> None:
    embedding = extract_face_embedding(image_path)
    if embedding is None:
        print("No se detectó rostro.")
        return

    thumbnail = generate_thumbnail(image_path)
    timestamp = int(time.time())
    face_id = str(uuid.uuid4())

    # Insertar en TinyDB with legacy schema using safe operation
    record_data = {
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

    # Use safe insert to prevent corruption
    if not safe_db_insert(record_data):
        logger.error(f"❌ Failed to save legacy face {face_id} to database")
        return

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

        # Create face record for legacy storage
        record_data = {
            "face_id": face_id,
            "event_id": event_id,
            "timestamp": timestamp,
            "image_path": image_path,
            "name": "unknown",
            "relationship": "unknown",
            "confidence": "unknown",
            "face_bbox": face_data["face_bbox"],
            "face_index": face_data["face_index"],
            "quality_metrics": face_data.get("quality_metrics", {}),
        }

        # Handle storage based on backend
        if USE_QDRANT and qdrant_adapter:
            # Save thumbnail to file for Qdrant
            if "face_crop" in face_data:
                thumbnail_path = save_thumbnail_to_file(face_data["face_crop"], face_id)
                record_data["thumbnail_path"] = thumbnail_path
        else:
            # Include embedding and thumbnail for TinyDB
            record_data["embedding"] = face_data["embedding"].tolist()
            record_data["thumbnail"] = face_data["face_crop"]

        # Save using unified database interface
        try:
            saved_face_id = db_save_face(record_data, face_data["embedding"])
            saved_face_ids.append(saved_face_id)
            print(f"Rostro {face_data['face_index']} guardado con ID: {saved_face_id}")
        except Exception as e:
            logger.error(f"❌ Failed to save face {face_id}: {e}")
            continue

    print(
        f"Total de {len(saved_face_ids)} rostros guardados para evento {event_id}"  # noqa: E501
    )  # noqa: E501
    return saved_face_ids


# Identificar rostro
def identify_face(image_path: str) -> Optional[Dict[str, Any]]:
    embedding = extract_face_embedding(image_path)
    if embedding is None:
        print("No se detectó rostro.")
        return None

    # Use unified database interface
    similar_faces = db_search_similar(embedding, limit=1)
    if similar_faces:
        face_id, distance, matched = similar_faces[0]
        if distance < FACE_SIMILARITY_THRESHOLD:
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

        # Search for matches using unified database interface
        similar_faces = db_search_similar(embedding, limit=1)

        if similar_faces:
            face_id, distance, matched = similar_faces[0]
        else:
            distance = float("inf")
            matched = None

        if distance < FACE_SIMILARITY_THRESHOLD:
            # Strong match - automatically identify
            if matched:
                results.append(
                    {
                        "face_index": face_index,
                        "status": "identified",
                        "face_data": matched,
                        "confidence": float(1.0 - distance),
                        "face_bbox": face_data["face_bbox"],
                        "face_crop": face_data["face_crop"],
                        "quality_metrics": face_data.get(
                            "quality_metrics", {}
                        ),  # noqa: E501
                    }
                )
        elif distance < BORDERLINE_THRESHOLD:
            # Borderline match - suggest for manual review
            if matched:
                results.append(
                    {
                        "face_index": face_index,
                        "status": "suggestion",
                        "face_data": matched,
                        "confidence": float(1.0 - distance),
                        "face_bbox": face_data["face_bbox"],
                        "face_crop": face_data["face_crop"],
                        "quality_metrics": face_data.get(
                            "quality_metrics", {}
                        ),  # noqa: E501
                        "message": (
                            f"Possible match with {matched.get('name', 'Unknown')} "
                            f"(confidence: {(1.0 - distance)*100:.1f}%). "
                            f"Review and confirm if this is the same person."
                        ),
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
                # Suggestion without database match - treat as unknown
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
                    f"Rostro {face_index}: Sugerencia, pero sin datos en BD "
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
                    "quality_metrics": face_data.get("quality_metrics", {}),
                }
            )
            quality_score = face_data.get("quality_metrics", {}).get(
                "overall_score", "N/A"
            )
            print(
                f"Rostro {face_index}: No identificado (calidad: {quality_score})"  # noqa: E501
            )  # noqa: E501

    return results


# Obtener rostros desconocidos
def get_unclassified_faces() -> List[Dict[str, Any]]:
    """Get unclassified faces with thumbnails loaded (supports both storage formats)."""
    # Use unified database interface
    unclassified_faces = db_get_unclassified_faces()

    # Convert to expected format for API compatibility
    unclassified = []
    for face in unclassified_faces:
        # Note: db_get_unclassified_faces already filters to unclassified faces
        # so we don't need to filter again

        # Prepare basic face data
        face_data = {
            "face_id": face["face_id"],
            "event_id": face.get("event_id", None),
            "image_path": face.get("image_path", None),
            "relationship": "unknown",
            "confidence": "unknown",
            "name": face.get("name", None),
        }

        # Handle thumbnail loading based on storage format
        if "thumbnail_path" in face and face["thumbnail_path"]:
            # Optimized storage: load thumbnail from file
            thumbnail_base64 = get_thumbnail_from_file(face["thumbnail_path"])
            face_data["thumbnail"] = thumbnail_base64
        else:
            # Legacy storage: thumbnail already in database
            face_data["thumbnail"] = face.get("thumbnail", None)

        unclassified.append(face_data)

    return unclassified


# Guardar rostro ya identificado
def update_face(face_id: str, data: Dict[str, str]) -> None:
    """Update a face's details"""
    updates = {
        "name": data["name"],
        "relationship": data["relationship"],
        "confidence": data["confidence"],
    }
    # Use unified database interface
    db_update_face(face_id, updates)


# Obtiene un rostro por su id
def get_face(face_id: str) -> Optional[Dict[str, Any]]:
    """Get a face"""
    # Use unified database interface
    return db_get_face(face_id)


def get_face_with_thumbnail(face_id: str) -> Optional[Dict[str, Any]]:
    """Get face with thumbnail loaded from file (optimized storage).

    Args:
        face_id: Unique face identifier

    Returns:
        Face record with thumbnail loaded from file, or None if not found
    """
    faces = safe_db_search(Face.face_id == face_id)
    if not faces:
        return None

    face = faces[0] if isinstance(faces, list) else faces

    # Handle both legacy and optimized storage formats
    if "thumbnail_path" in face and face["thumbnail_path"]:
        # Optimized storage: load thumbnail from file
        thumbnail_base64 = get_thumbnail_from_file(face["thumbnail_path"])
        if thumbnail_base64:
            face["thumbnail"] = thumbnail_base64
        else:
            logger.warning(f"⚠️ Thumbnail file not found: {face['thumbnail_path']}")
            face["thumbnail"] = None
    elif "thumbnail" not in face or not face["thumbnail"]:
        # No thumbnail available
        face["thumbnail"] = None

    return face


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
            f"  Score de detección: {quality.get('detection_score', 'N/A'):.3f}"  # noqa: E501
        )  # noqa: E501

        if quality.get("overall_score", 0) < MIN_QUALITY_SCORE:
            print(
                f"  ❌ FILTRADO: Calidad inferior al umbral ({MIN_QUALITY_SCORE})"  # noqa: E501
            )  # noqa: E501
        else:
            print(
                f"  ✅ ACEPTADO: Calidad superior al umbral ({MIN_QUALITY_SCORE})"  # noqa: E501
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
