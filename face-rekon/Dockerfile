FROM python:3.11-slim

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y build-essential libgl1 libglib2.0-0 && \
    pip install --no-cache-dir pillow tinydb faiss-cpu insightface==0.7.3

WORKDIR /app

COPY run.sh /run.sh
COPY scripts/ /app/scripts/
COPY data/ /app/data/

RUN chmod +x /run.sh

CMD ["/run.sh"]
