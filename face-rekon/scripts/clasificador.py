import base64
import io
import os
import time
import uuid

import cv2
import faiss
import numpy as np
from insightface.app import FaceAnalysis
from PIL import Image
from tinydb import Query, TinyDB

# Configuración de rutas (con soporte para variables de entorno para testing)
BASE_PATH = os.environ.get("FACE_REKON_BASE_PATH", "/config/face-rekon/faces")
UNKNOWN_PATH = os.environ.get("FACE_REKON_UNKNOWN_PATH", "/config/face-rekon/unknowns")
DB_PATH = os.environ.get("FACE_REKON_DB_PATH", "/config/face-rekon/db/tinydb.json")
FAISS_INDEX_PATH = os.environ.get(
    "FACE_REKON_FAISS_INDEX_PATH", "/config/face-rekon/db/faiss_index.index"
)
MAPPING_PATH = os.environ.get(
    "FACE_REKON_MAPPING_PATH", "/config/face-rekon/db/faiss_id_map.npy"
)
THUMBNAIL_SIZE = (160, 160)

# Inicializar InsightFace
app = FaceAnalysis(allowed_modules=["detection", "recognition"])
app.prepare(ctx_id=0, det_size=(640, 640))

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
def extract_face_embedding(image_path):
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
def extract_all_face_embeddings(image_path):
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


# Crear thumbnail base64
def generate_thumbnail(image_path):
    img = Image.open(image_path)
    img.thumbnail(THUMBNAIL_SIZE)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# Guardar rostro desconocido
def save_unknown_face(image_path, event_id):
    embedding = extract_face_embedding(image_path)
    if embedding is None:
        print("No se detectó rostro.")
        return

    thumbnail = generate_thumbnail(image_path)
    timestamp = int(time.time())
    face_id = str(uuid.uuid4())

    # Insertar en TinyDB
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
        }
    )

    # Insertar en FAISS e ID map
    index.add(np.array([embedding], dtype=np.float32))
    id_map.append(face_id)

    # Guardar índice y map
    faiss.write_index(index, FAISS_INDEX_PATH)
    np.save(MAPPING_PATH, np.array(id_map))

    print("Rostro guardado con ID:", face_id)


# Identificar rostro
def identify_face(image_path):
    embedding = extract_face_embedding(image_path)
    if embedding is None:
        print("No se detectó rostro.")
        return None

    distances, indices = index.search(np.array([embedding], dtype=np.float32), 1)
    if distances[0][0] < 0.5:
        face_id = id_map[indices[0][0]]
        matched = db.get(Face.face_id == face_id)
        if matched:
            print(f"Identificado: {matched.get('name', matched['face_id'])}")
            return matched
    print("Rostro no identificado.")
    return None


# Identificar todos los rostros en una imagen
def identify_all_faces(image_path):
    embeddings = extract_all_face_embeddings(image_path)
    if not embeddings:
        print("No se detectaron rostros.")
        return []

    results = []
    for i, embedding in enumerate(embeddings):
        distances, indices = index.search(np.array([embedding], dtype=np.float32), 1)
        if distances[0][0] < 0.5:
            face_id = id_map[indices[0][0]]
            matched = db.get(Face.face_id == face_id)
            if matched:
                results.append(
                    {
                        "face_index": i,
                        "status": "identified",
                        "face_data": matched,
                        "confidence": float(1.0 - distances[0][0]),
                    }
                )
                name = matched.get('name', matched['face_id'])
                print(f"Rostro {i}: Identificado como {name}")
            else:
                results.append(
                    {
                        "face_index": i,
                        "status": "unknown",
                        "face_data": None,
                        "confidence": 0.0,
                    }
                )
                print(f"Rostro {i}: No identificado")
        else:
            results.append(
                {
                    "face_index": i,
                    "status": "unknown",
                    "face_data": None,
                    "confidence": 0.0,
                }
            )
            print(f"Rostro {i}: No identificado")

    return results


# Obtener rostros desconocidos
def get_unclassified_faces():
    unclassified = [
        {
            "face_id": face["face_id"],
            "event_id": face.get("event_id", None),
            "image_path": face.get("image_path", None),
            "thumbnail": face.get("thumbnail", None),
            "name": face.get("name", None),
            "relationship": "unknown",
            "confidence": "unknown",
        }
        for face in db.all()
        if not face.get("name")
    ]

    return unclassified


# Guardar rostro ya identificado
def update_face(face_id, data):
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
def get_face(face_id):
    """Get a face"""
    return db.search(Face.face_id == face_id)


if __name__ == "__main__":
    new_image_path = "/config/face-rekon/images/new_face.jpg"
    result = identify_face(new_image_path)
    if not result:
        save_unknown_face(new_image_path)
