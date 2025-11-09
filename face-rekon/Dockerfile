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

# Instalar dependencias de Python ANTES de copiar código
# 2-layer approach to reduce disk space pressure per layer
# Layer 1: Core dependencies with numpy constraint (~2GB)
RUN pip install --no-cache-dir \
    'numpy<2.0.0' \
    onnxruntime \
    pillow \
    opencv-python-headless

# Layer 2: ML libraries + Flask (~1.5GB)
# Note: realesrgan pulls in basicsr, facexlib, gfpgan as dependencies
RUN pip install --no-cache-dir \
    insightface==0.7.3 \
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
