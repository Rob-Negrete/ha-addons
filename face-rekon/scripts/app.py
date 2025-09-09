import base64
import os
import uuid

import clasificador
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_restx import Api, Namespace, Resource
from models import create_models

app = Flask(__name__)
CORS(app)

# Initialize Flask-RESTX API
api = Api(
    app,
    version="1.0",
    title="Face Recognition API",
    description="Home Assistant Face Recognition Add-on API",
    doc="/swagger/",
)

# Create namespace for face recognition endpoints
ns = Namespace(
    "face-rekon", description="Face recognition operations", path="/face-rekon"
)

# Create API models
models = create_models(api)

# Register the namespace
api.add_namespace(ns)


@ns.route("/ping")
class Ping(Resource):
    @api.marshal_with(models["ping_model"])
    @api.doc("ping")
    def get(self):
        """Health check endpoint
        Returns a simple pong response to verify the service is running.
        """
        return {"pong": True}


@ns.route("/recognize")
class Recognize(Resource):
    @api.expect(models["recognize_request_model"], validate=True)
    @api.marshal_with(models["recognize_response_model"])
    @api.response(400, "Bad Request", models["error_model"])
    @api.response(500, "Internal Server Error", models["error_model"])
    @api.doc("recognize_faces")
    def post(self):
        """Recognize faces from uploaded image

        Processes a base64-encoded image to detect and identify faces.
        Returns information about all detected faces including recognition status.
        Unknown faces are automatically saved for later classification.
        """
        data = request.get_json()
        if not data or "image_base64" not in data:
            return {"error": "Missing image_base64"}, 400

        image_base64 = data["image_base64"]

        # Handle data URI format (e.g., "data:image/jpeg;base64,..."
        # or "image/jpg;data:...")
        if "data:" in image_base64:
            image_base64 = image_base64.split(",", 1)[
                1
            ]  # Remove "data:image/jpeg;base64," prefix
        elif ";data:" in image_base64:
            image_base64 = image_base64.split(";data:", 1)[
                1
            ]  # Remove "image/jpg;data:" prefix

        image_data = base64.b64decode(image_base64)

        tmp_dir = "/app/data/tmp"
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4().hex}.jpeg")

        with open(tmp_path, "wb") as f:
            f.write(image_data)

        event_id = data["event_id"]

        try:
            # Always process all faces in the image
            results = clasificador.identify_all_faces(tmp_path)

            # Save unknown faces for later classification
            has_unknown = any(result["status"] == "unknown" for result in results)
            if has_unknown:
                clasificador.save_unknown_face(tmp_path, event_id)

            return {
                "status": "success" if results else "no_faces_detected",
                "faces_count": len(results),
                "faces": results,
            }

        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            os.remove(tmp_path)


@ns.route("/")
class UnclassifiedFaces(Resource):
    @api.marshal_list_with(models["face_model"])
    @api.doc("get_unclassified_faces")
    def get(self):
        """Get list of unclassified faces

        Returns all faces that have been detected but not yet assigned to a person.
        These faces can be classified using the PATCH endpoint.
        """
        unclassified_faces = clasificador.get_unclassified_faces()
        return unclassified_faces


@ns.route("/<string:face_id>")
class Face(Resource):
    @api.marshal_with(models["face_model"])
    @api.doc("get_face", params={"face_id": "Unique face identifier"})
    def get(self, face_id):
        """Get specific face information

        Retrieves detailed information about a specific face by its ID.
        """
        face = clasificador.get_face(face_id)
        return face

    @api.expect(models["face_update_model"], validate=True)
    @api.marshal_with(models["update_response_model"])
    @api.response(500, "Internal Server Error", models["error_model"])
    @api.doc("update_face", params={"face_id": "Unique face identifier"})
    def patch(self, face_id):
        """Update face information

        Assigns a name and additional information to an unclassified face.
        This moves the face from unknown to known status.
        """
        data = request.get_json()

        try:
            clasificador.update_face(face_id, data)
            return {
                "status": "success",
                "message": f"Face {face_id} updated successfully.",
            }
        except Exception as e:
            return {"error": str(e)}, 500


@app.route("/", methods=["GET"])
def home():
    return send_from_directory("./", "index.html")


@app.route("/snapshot", methods=["GET"])
def snapshot():
    return send_from_directory("./", "snapshot.jpg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
