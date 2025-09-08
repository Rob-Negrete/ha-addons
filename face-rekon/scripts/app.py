from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import clasificador
import base64

app = Flask(__name__)
CORS(app)

@app.route('/face-rekon/ping', methods=['GET'])
def ping():
    """Return a pong response"""
    return jsonify({'pong': True})

@app.route('/face-rekon/recognize', methods=['POST'])
def recognize():
    """Recognize faces from the given image data"""
    data = request.get_json()
    if not data or 'image_base64' not in data:
        return jsonify({'error': 'Missing image_base64'}), 400

    image_base64 = data['image_base64']
    
    # Handle data URI format (e.g., "data:image/jpeg;base64,..." or "image/jpg;data:...")
    if 'data:' in image_base64:
        image_base64 = image_base64.split(',', 1)[1]  # Remove "data:image/jpeg;base64," prefix
    elif ';data:' in image_base64:
        image_base64 = image_base64.split(';data:', 1)[1]  # Remove "image/jpg;data:" prefix    
    
    image_data = base64.b64decode(image_base64)
    # print("image_data", image_data)

    tmp_dir = "/app/data/tmp"
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4().hex}.jpeg")

    with open(tmp_path, "wb") as f:
        f.write(image_data)

    event_id = data['event_id']

    try:
        # Always process all faces in the image
        results = clasificador.identify_all_faces(tmp_path)
        
        # Save unknown faces for later classification
        has_unknown = any(result['status'] == 'unknown' for result in results)
        if has_unknown:
            clasificador.save_unknown_face(tmp_path, event_id)
        
        return jsonify({
            'status': 'success' if results else 'no_faces_detected',
            'faces_count': len(results),
            'faces': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(tmp_path)

@app.route('/face-rekon', methods=['GET'])
def get_unclassified():
    """Return a list of unclassified faces"""
    unclassified_faces = clasificador.get_unclassified_faces()
    return unclassified_faces

@app.route('/face-rekon/<string:face_id>', methods=['GET'])
def get_face(face_id):
    """Return a face"""
    face = clasificador.get_face(face_id)
    return face


@app.route('/face-rekon/<string:face_id>', methods=['PATCH'])
def update_face(face_id):
    """Update a face's details"""
    data = request.get_json()  # This will contain the JSON payload from your PUT request
    
    try:
        clasificador.update_face(face_id, data)
        return jsonify({"status": "success", "message": f"Face  {face_id} updated successfully."})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return send_from_directory("./","index.html")

@app.route('/snapshot', methods=['GET'])
def snapshot():
    return send_from_directory("./","snapshot.jpg")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)