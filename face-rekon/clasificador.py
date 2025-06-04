import os
import cv2
import numpy as np
import base64
from PIL import Image
import time
import pickle
from insightface import App
from tinydb import TinyDB, Query
import faiss
import io

# Configuración de rutas
BASE_PATH = "/config/face-rekon/faces"
UNKNOWN_PATH = "/config/face-rekon/unknowns"
DB_PATH = "/config/face-rekon/db/tinydb.json"
THUMBNAIL_SIZE = (160, 160)  # Tamaño del thumbnail

# Inicializar InsightFace para detección de rostros
app = App()
app.prepare(ctx_id=0)

# Inicializar la base de datos TinyDB
db = TinyDB(DB_PATH)
Face = Query()

# Crear el índice FAISS para las comparaciones de rostros
dimension = 512  # Tamaño del vector de InsightFace
index = faiss.IndexFlatL2(dimension)  # Usamos el índice básico de faiss
if os.path.exists('/config/face-rekon/db/faiss_index.index'):
    faiss.read_index('/config/face-rekon/db/faiss_index.index')  # Cargar el índice previamente guardado

# Función para extraer el vector del rostro usando InsightFace
def extract_face_embedding(image_path):
    img = cv2.imread(image_path)
    faces = app.get(image_path)
    if faces:
        return faces[0].embedding
    return None

# Función para generar un thumbnail y convertirlo a base64
def generate_thumbnail(image_path):
    img = Image.open(image_path)
    img.thumbnail(THUMBNAIL_SIZE)
    
    # Convertir a base64
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    thumbnail_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return thumbnail_base64

# Función para guardar el rostro desconocido en TinyDB y FAISS
def save_unknown_face(image_path):
    # Extraer el embedding del rostro
    embedding = extract_face_embedding(image_path)
    if embedding is None:
        print("No se pudo detectar un rostro en la imagen.")
        return

    # Generar el thumbnail y convertirlo a base64
    thumbnail_base64 = generate_thumbnail(image_path)

    # Guardar los metadatos en TinyDB
    timestamp = int(time.time())
    face_data = {
        'timestamp': timestamp,
        'image_path': image_path,
        'embedding': embedding.tolist(),
        'thumbnail': thumbnail_base64,
    }
    db.insert(face_data)

    # Insertar el rostro en FAISS
    faiss_index = np.array([embedding], dtype=np.float32)
    index.add(faiss_index)

    # Guardar el índice FAISS para la persistencia
    faiss.write_index(index, '/config/face-rekon/db/faiss_index.index')

    print(f"Rostro desconocido guardado en el índice FAISS y en la base de datos TinyDB.")

# Función para identificar rostros conocidos
def identify_face(image_path):
    embedding = extract_face_embedding(image_path)
    if embedding is None:
        print("No se pudo detectar un rostro en la imagen.")
        return None

    # Buscar en FAISS
    faiss_index = np.array([embedding], dtype=np.float32)
    D, I = index.search(faiss_index, 1)  # Buscar el rostro más cercano
    if D[0][0] < 0.5:  # Umbral de similitud (ajustable)
        # Obtener el rostro más cercano de TinyDB
        matched_face = db.get(Face.embedding == embedding.tolist())
        if matched_face:
            person_name = matched_face['timestamp']
            print(f"Rostro identificado: {person_name}")
            return person_name
    print("Rostro no identificado.")
    return None

# Ejemplo de uso
new_image_path = "/config/face-rekon/images/new_face.jpg"

# Intentar identificar al rostro
person_name = identify_face(new_image_path)
if not person_name:
    # Si no se ha identificado, guardar el rostro como desconocido
    save_unknown_face(new_image_path)
