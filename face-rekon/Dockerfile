FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0t64 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        jq \
        && rm -rf /var/lib/apt/lists/*

# Crear estructura del add-on
WORKDIR /app

# Instalar dependencias de Python en capas para evitar exceder espacio en disco
# Layer 1: PyTorch + core libs (must install torch FIRST to establish numpy<2.0)
RUN pip install --no-cache-dir \
    'numpy<2.0.0' \
    torch \
    torchvision

# Layer 2: ML processing libraries (reuse torch from Layer 1)
RUN pip install --no-cache-dir \
    onnxruntime \
    pillow \
    opencv-python-headless \
    insightface==0.7.3

# Layer 3: Enhanced image processing + Flask (lightweight ~500MB)
# Note: realesrgan pulls in basicsr, facexlib, gfpgan
RUN pip install --no-cache-dir \
    realesrgan==0.3.0 \
    flask \
    flask-cors \
    flask-restx \
    qdrant-client==1.7.0

# Ahora copiar archivos de aplicación (al final para aprovechar cache)
COPY run.sh /run.sh
COPY scripts/ /app/scripts/
COPY ui/ /app/ui/
RUN mkdir -p /app/data/

# Permisos de ejecución
RUN chmod +x /run.sh

# Ejecutar script de reconocimiento
CMD ["/run.sh"]
