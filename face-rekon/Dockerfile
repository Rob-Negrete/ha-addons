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

# Instalar Qdrant (solo soportado en x86_64 por ahora)
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        wget -O /tmp/qdrant.tar.gz https://github.com/qdrant/qdrant/releases/download/v1.7.4/qdrant-x86_64-unknown-linux-gnu.tar.gz && \
        tar -xzf /tmp/qdrant.tar.gz -C /tmp && \
        mv /tmp/qdrant /usr/local/bin/qdrant && \
        chmod +x /usr/local/bin/qdrant && \
        rm -f /tmp/qdrant.tar.gz; \
    else \
        echo "Warning: Qdrant binary not available for $ARCH, will fall back to FAISS only"; \
        echo '#!/bin/bash\necho "Qdrant not available for this architecture, using FAISS fallback"\nexit 1' > /usr/local/bin/qdrant && \
        chmod +x /usr/local/bin/qdrant; \
    fi

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
