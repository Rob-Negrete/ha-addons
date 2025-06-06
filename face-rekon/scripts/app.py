from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import clasificador
import base64

app = Flask(__name__)
CORS(app)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"pong": True})

@app.route('/recognize', methods=['POST'])
def recognize():
    data = request.get_json()
    if not data or 'image_base64' not in data:
        return jsonify({"error": "Missing image_base64"}), 400

    image_data = base64.b64decode(data['image_base64'])

    tmp_dir = "/tmp/face-rekon"
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4().hex}.jpg")

    with open(tmp_path, "wb") as f:
        f.write(image_data)

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
