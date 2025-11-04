FROM python:3.10-slim

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0t64 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        && rm -rf /var/lib/apt/lists/*

# Crear estructura del add-on
WORKDIR /app

# Copiar archivos
COPY run.sh /run.sh
COPY scripts/ /app/scripts/
COPY ui/ /app/ui/
# COPY data/ /app/data/
RUN mkdir -p /app/data/


# Permisos de ejecución
RUN chmod +x /run.sh

# Instalar dependencias de Python
RUN pip install --no-cache-dir \
    'numpy<2.0.0' \
    insightface==0.7.3 \
    pillow \
    opencv-python-headless \
    onnxruntime \
    flask \
    flask-cors \
    flask-restx \
    qdrant-client==1.7.0 \
    torch==1.13.1 \
    torchvision==0.14.1 \
    gfpgan==1.3.8 \
    realesrgan==0.3.0 \
    basicsr==1.4.2

# Ejecutar script de reconocimiento
CMD ["/run.sh"]
