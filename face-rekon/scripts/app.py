from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong"}), 200

# Aquí podrías agregar más endpoints para reconocimiento facial, etc.

if __name__ == "__main__":
    # Escuchar en 0.0.0.0 para aceptar conexiones externas dentro del contenedor
    app.run(host="0.0.0.0", port=5000)
