FROM python:3.10-slim

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        && rm -rf /var/lib/apt/lists/*

# Crear estructura del add-on
WORKDIR /app

# Copiar archivos
COPY run.sh /run.sh
COPY scripts/ /app/scripts/
# COPY data/ /app/data/
RUN mkdir -p /app/data/


# Permisos de ejecución
RUN chmod +x /run.sh

# Instalar dependencias de Python
RUN pip install --no-cache-dir \
    insightface==0.7.3 \
    pillow \
    numpy \
    opencv-python-headless \
    tinydb \
    faiss-cpu==1.10.0 \
    onnxruntime \
    flask

# Ejecutar script de reconocimiento
CMD ["/run.sh"]