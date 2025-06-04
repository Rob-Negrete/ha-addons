#!/bin/bash
echo "Iniciando Face Rekon..."
python3 /app/scripts/clasificador.py
tail -f /dev/null
