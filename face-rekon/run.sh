#!/bin/bash
echo "Iniciando Face Rekon..."
mkdir -p /config/face-rekon/db
mkdir -p /config/face-rekon/images
mkdir -p /config/face-rekon/faces
mkdir -p /config/face-rekon/unknowns

python3 /app/scripts/app.py

# Mantener el contenedor activo para diagnóstico (puedes quitarlo si lo deseas)
tail -f /dev/null