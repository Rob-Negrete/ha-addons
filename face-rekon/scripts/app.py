import base64
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

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
    prefix="/api",
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
    def get(self) -> Dict[str, bool]:
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
    def post(self) -> Tuple[Dict[str, Any], int]:
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
            # Always process all faces in the image with face crops
            results = clasificador.identify_all_faces(tmp_path)

            # Save unknown faces using the new multi-face function
            unknown_faces = [
                result for result in results if result["status"] == "unknown"
            ]
            if unknown_faces:
                # Use the new save_multiple_faces function for better handling
                saved_face_ids = clasificador.save_multiple_faces(tmp_path, event_id)
                print(f"Saved {len(saved_face_ids)} unknown faces for event {event_id}")

            return {
                "status": "success" if results else "no_faces_detected",
                "faces_count": len(results),
                "faces": results,
                "event_id": event_id,
                "processing_method": "face_extraction_crops",
            }

        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            os.remove(tmp_path)


@ns.route("/")
class UnclassifiedFaces(Resource):
    @api.marshal_list_with(models["face_model"])
    @api.doc("get_unclassified_faces")
    def get(self) -> List[Dict[str, Any]]:
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
    def get(self, face_id: str) -> Optional[Dict[str, Any]]:
        """Get specific face information

        Retrieves detailed information about a specific face by its ID.
        """
        face = clasificador.get_face(face_id)
        return face

    @api.expect(models["face_update_model"], validate=True)
    @api.marshal_with(models["update_response_model"])
    @api.response(500, "Internal Server Error", models["error_model"])
    @api.doc("update_face", params={"face_id": "Unique face identifier"})
    def patch(self, face_id: str) -> Dict[str, str]:
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
def home() -> Any:
    """Serve the main UI page"""
    import os

    # Get absolute path to ensure it works regardless of working directory
    ui_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ui"))
    return send_from_directory(ui_dir, "index.html")


@app.route("/assets/<path:filename>", methods=["GET"])
def serve_assets(filename: str) -> Any:
    """Serve static UI assets (CSS, JS, images)"""
    import os

    ui_assets_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "ui", "assets")
    )
    return send_from_directory(ui_assets_dir, filename)


@app.route("/loadSnapshot", methods=["GET"])
def loadSnapshot() -> Any:
    """Serve the main UI page"""
    import os

    # Get absolute path to ensure it works regardless of working directory
    ui_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ui"))
    return send_from_directory(ui_dir, "loadSnapshot.html")


@app.route("/images/<string:face_id>", methods=["GET"])
def serve_face_image(face_id: str) -> Any:
    """Serve face thumbnail images by face ID

    Returns face thumbnail as JPEG image from base64 data stored in TinyDB.
    Provides proper HTTP headers for caching and content type.

    Args:
        face_id: Unique face identifier (UUID format)

    Returns:
        200: Image data with proper headers
        404: Face ID not found
        400: Invalid face ID format
    """
    import base64
    import re

    from flask import Response

    # Validate face_id format (basic UUID validation)
    if not face_id or not isinstance(face_id, str):
        return {"error": "Invalid face ID"}, 400

    # Basic UUID format check
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )
    if not uuid_pattern.match(face_id):
        return {"error": "Invalid face ID format"}, 400

    try:
        # Get face data from database
        face_data = clasificador.get_face(face_id)

        if not face_data or len(face_data) == 0:
            return {"error": "Face not found"}, 404

        # Get the first result (get_face returns a list)
        face = face_data[0] if isinstance(face_data, list) else face_data

        # Check if thumbnail exists
        if "thumbnail" not in face or not face["thumbnail"]:
            return {"error": "No thumbnail available"}, 404

        # Decode base64 thumbnail
        try:
            image_data = base64.b64decode(face["thumbnail"])
        except Exception:
            return {"error": "Invalid image data"}, 400

        # Create response with proper headers
        response = Response(
            image_data,
            mimetype="image/jpeg",
            headers={
                "Content-Type": "image/jpeg",
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "Content-Length": str(len(image_data)),
            },
        )

        return response

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
