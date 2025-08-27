import os
import cv2
import numpy as np
import base64
from PIL import Image
import time
import io
import uuid
from insightface.app import FaceAnalysis
from tinydb import TinyDB, Query
import faiss

# Configuración de rutas
BASE_PATH = "/config/face-rekon/faces"
UNKNOWN_PATH = "/config/face-rekon/unknowns"
DB_PATH = "/config/face-rekon/db/tinydb.json"
FAISS_INDEX_PATH = "/config/face-rekon/db/faiss_index.index"
MAPPING_PATH = "/config/face-rekon/db/faiss_id_map.npy"
THUMBNAIL_SIZE = (160, 160)

# Inicializar InsightFace
app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
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

# Crear thumbnail base64
def generate_thumbnail(image_path):
    img = Image.open(image_path)
    img.thumbnail(THUMBNAIL_SIZE)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Guardar rostro desconocido
def save_unknown_face(image_path):
    embedding = extract_face_embedding(image_path)
    if embedding is None:
        print("No se detectó rostro.")
        return

    thumbnail = generate_thumbnail(image_path)
    timestamp = int(time.time())
    face_id = str(uuid.uuid4())

    # Insertar en TinyDB
    db.insert({
        "face_id": face_id,
        "timestamp": timestamp,
        "image_path": image_path,
        "embedding": embedding.tolist(),
        "thumbnail": thumbnail,
        "name": None,
        "relationship": "unknown",
        "confidence": "unknown"
    })

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

    D, I = index.search(np.array([embedding], dtype=np.float32), 1)
    if D[0][0] < 0.5:
        face_id = id_map[I[0][0]]
        matched = db.get(Face.face_id == face_id)
        if matched:
            print(f"Identificado: {matched.get('name', matched['face_id'])}")
            return matched
    print("Rostro no identificado.")
    return None

# Obtener rostros desconocidos
def get_unclassified_faces():
    return [face["face_id", "thumbnail", "image_path", "name",] for face in db.all() if face.get("name") is None]

if __name__ == "__main__":
    new_image_path = "/config/face-rekon/images/new_face.jpg"
    result = identify_face(new_image_path)
    if not result:
        save_unknown_face(new_image_path)

