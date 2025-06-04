from flask import Flask, request, jsonify
import os
import uuid
import clasificador

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"pong": True})

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Guardar imagen temporal
    tmp_dir = "/tmp/face-rekon"
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4().hex}.jpg")
    image.save(tmp_path)

    try:
        result = clasificador.identify_face(tmp_path)
        if result:
            return jsonify({
                "status": "identified",
                "name": result.get("name", result.get("face_id")),
                "confidence": result.get("confidence", "N/A")
            })
        else:
            clasificador.save_unknown_face(tmp_path)
            return jsonify({"status": "unknown"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(tmp_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
