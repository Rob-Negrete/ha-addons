#!/bin/bash
echo "Iniciando Face Rekon..."
mkdir -p /config/face-rekon/db
mkdir -p /config/face-rekon/images
mkdir -p /config/face-rekon/faces
mkdir -p /config/face-rekon/unknowns

# Read configuration from Home Assistant add-on options
CONFIG_PATH="/data/options.json"

if [ -f "$CONFIG_PATH" ]; then
    echo "Loading configuration from $CONFIG_PATH"

    # Export detection thresholds if provided
    MIN_DETECTION_CONF=$(jq -r '.min_detection_confidence // 0.7' "$CONFIG_PATH")
    MIN_QUALITY=$(jq -r '.min_quality_score // 0.5' "$CONFIG_PATH")
    MIN_FACE_SIZE=$(jq -r '.min_face_size // 50' "$CONFIG_PATH")
    SIMILARITY_THRESH=$(jq -r '.similarity_threshold // 0.35' "$CONFIG_PATH")

    export FACE_REKON_MIN_DETECTION_CONFIDENCE="$MIN_DETECTION_CONF"
    export FACE_REKON_MIN_QUALITY_SCORE="$MIN_QUALITY"
    export FACE_REKON_MIN_FACE_SIZE="$MIN_FACE_SIZE"
    export FACE_REKON_SIMILARITY_THRESHOLD="$SIMILARITY_THRESH"

    echo "Detection confidence threshold: $MIN_DETECTION_CONF"
    echo "Quality score threshold: $MIN_QUALITY"
    echo "Minimum face size: $MIN_FACE_SIZE"
    echo "Similarity threshold: $SIMILARITY_THRESH"
fi

python3 /app/scripts/app.py

# Mantener el contenedor activo para diagnóstico (puedes quitarlo si lo deseas)
tail -f /dev/null
