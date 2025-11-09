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
        jq \
        && rm -rf /var/lib/apt/lists/*

# Crear estructura del add-on
WORKDIR /app

# Instalar dependencias de Python ANTES de copiar código para mejor caching
# Esto evita reinstalar todo cuando solo cambia el código
# Layer 1: PyTorch + numpy (must be together, ~800MB)
RUN pip install --no-cache-dir \
    'numpy<2.0.0' \
    torch==1.13.1 \
    torchvision==0.14.1

# Layer 2: Core processing libraries
RUN pip install --no-cache-dir \
    onnxruntime \
    opencv-python-headless \
    pillow

# Layer 3: ML y procesamiento de imágenes
RUN pip install --no-cache-dir \
    insightface==0.7.3 \
    basicsr==1.4.2 \
    realesrgan==0.3.0

# Layer 4: Flask y almacenamiento (ligero, ~20MB)
RUN pip install --no-cache-dir \
    flask \
    flask-cors \
    flask-restx \
    qdrant-client==1.7.0

# Layer 5: Force numpy<2.0 (some ML packages try to upgrade it)
RUN pip install --no-cache-dir --force-reinstall --no-deps 'numpy<2.0.0'

# Ahora copiar archivos de aplicación (al final para aprovechar cache)
COPY run.sh /run.sh
COPY scripts/ /app/scripts/
COPY ui/ /app/ui/
RUN mkdir -p /app/data/

# Permisos de ejecución
RUN chmod +x /run.sh

# Ejecutar script de reconocimiento
CMD ["/run.sh"]
