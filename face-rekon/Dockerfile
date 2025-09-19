FROM python:3.10-slim

# Instalar dependencias del sistema incluyendo Qdrant
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        wget \
        curl \
        supervisor \
        && rm -rf /var/lib/apt/lists/*

# Instalar Qdrant basado en la arquitectura
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        QDRANT_ARCH="x86_64-unknown-linux-musl"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        QDRANT_ARCH="aarch64-unknown-linux-musl"; \
    elif [ "$ARCH" = "armv7l" ]; then \
        QDRANT_ARCH="armv7-unknown-linux-musleabihf"; \
    else \
        QDRANT_ARCH="x86_64-unknown-linux-musl"; \
    fi && \
    wget -O /usr/local/bin/qdrant https://github.com/qdrant/qdrant/releases/download/v1.7.4/qdrant-${QDRANT_ARCH} \
    && chmod +x /usr/local/bin/qdrant

# Crear estructura del add-on
WORKDIR /app

# Copiar archivos
COPY run.sh /run.sh
COPY scripts/ /app/scripts/
COPY ui/ /app/ui/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY qdrant-config.yaml /app/qdrant-config.yaml
# COPY data/ /app/data/
RUN mkdir -p /app/data/ /var/log /config/face-rekon/qdrant


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
    flask \
    flask-cors \
    flask-restx \
    qdrant-client==1.7.0

# Ejecutar supervisor para manejar ambos servicios
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
