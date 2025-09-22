import base64
import logging
import os
import sys
import uuid
from typing import Any, Dict, List, Optional, Tuple

import clasificador
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_restx import Api, Namespace, Resource
from models import create_models

# Configure logging to stdout for Home Assistant
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

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
        Returns information about all detected faces including recognition
        status.
        Unknown faces are automatically saved for later classification.
        """
        logger.info("🎯 Received face recognition request")

        try:
            data = request.get_json()
            if not data or "image_base64" not in data:
                logger.error("❌ Missing image_base64 in request")
                return {"error": "Missing image_base64"}, 400

            event_id = data.get("event_id", "unknown")
            logger.info(f"📝 Processing event_id: {event_id}")

            image_base64 = data["image_base64"]
            logger.info(
                f"📊 Received image data length: {len(image_base64)} characters"
            )  # noqa: E501

            # Handle data URI format (e.g., "data:image/jpeg;base64,..."
            # or "image/jpg;data:...")
            if "data:" in image_base64:
                image_base64 = image_base64.split(",", 1)[
                    1
                ]  # Remove "data:image/jpeg;base64," prefix
                logger.info("🔧 Removed data URI prefix")
            elif ";data:" in image_base64:
                image_base64 = image_base64.split(";data:", 1)[
                    1
                ]  # Remove "image/jpg;data:" prefix
                logger.info("🔧 Removed custom data prefix")

            # Decode base64 image
            try:
                image_data = base64.b64decode(image_base64)
                logger.info(f"✅ Decoded image data: {len(image_data)} bytes")

                # Check if decoded data looks like JSON error response
                if len(image_data) < 100:  # Typical error responses are small
                    try:
                        # Try to decode as JSON to detect error responses
                        import json

                        json_data = json.loads(image_data.decode("utf-8"))
                        if isinstance(json_data, dict) and not json_data.get(
                            "success", True
                        ):
                            logger.warning(
                                f"🚫 Detected JSON error response: {json_data}"
                            )
                            return {
                                "error": "Invalid image data - received error response",  # noqa: E501
                                "details": json_data.get(
                                    "message", "Unknown error"
                                ),  # noqa: E501
                            }, 400
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Not JSON, continue with image processing
                        pass

            except Exception as e:
                logger.error(f"❌ Failed to decode base64 image: {e}")
                return {"error": "Invalid base64 image data"}, 400

            # Save image to temporary file
            tmp_dir = "/app/data/tmp"
            os.makedirs(tmp_dir, exist_ok=True)

            # Detect image format from header
            if image_data.startswith(b"RIFF") and b"WEBP" in image_data[:12]:
                extension = ".webp"
                logger.info("🖼️ Detected WEBP format")
            elif image_data.startswith(b"\xFF\xD8\xFF"):
                extension = ".jpg"
                logger.info("🖼️ Detected JPEG format")
            elif image_data.startswith(b"\x89PNG"):
                extension = ".png"
                logger.info("🖼️ Detected PNG format")
            else:
                extension = ".jpg"  # Default fallback
                logger.warning("⚠️ Unknown image format, defaulting to .jpg")

            tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4().hex}{extension}")

            with open(tmp_path, "wb") as f:
                f.write(image_data)
            logger.info(f"💾 Saved image to: {tmp_path}")

        except Exception as e:
            logger.error(f"❌ Error in request preprocessing: {e}")
            return {"error": f"Request processing failed: {str(e)}"}, 500

        try:
            # Always process all faces in the image with face crops
            logger.info(f"🔍 Starting face recognition on: {tmp_path}")
            logger.info(f"📊 File exists: {os.path.exists(tmp_path)}")
            logger.info(f"📊 File size: {os.path.getsize(tmp_path)} bytes")

            results = clasificador.identify_all_faces(tmp_path)
            logger.info(
                f"🎉 Face recognition completed. Found {len(results)} faces"
            )  # noqa: E501
            logger.info(f"📊 Results details: {results}")

            # Save unknown and suggestion faces using optimized storage
            faces_to_save = [
                result
                for result in results
                if result["status"] in ["unknown", "suggestion"]
            ]
            if faces_to_save:
                if clasificador.USE_OPTIMIZED_STORAGE:
                    logger.info(
                        f"💾 Saving {len(faces_to_save)} faces (unknown/suggestions) "
                        "with optimized storage"
                    )
                    # Use optimized storage (file-based, no embedding duplication)
                    saved_face_ids = clasificador.save_multiple_faces_optimized(
                        tmp_path, event_id
                    )
                    logger.info(
                        f"✅ Optimized storage complete: {len(saved_face_ids)} faces "
                        f"for event {event_id} (97% size reduction)"
                    )
                else:
                    logger.info(
                        f"💾 Saving {len(faces_to_save)} faces (unknown/suggestions) "
                        "with legacy storage"
                    )
                    # Use legacy storage for backward compatibility
                    saved_face_ids = clasificador.save_multiple_faces(
                        tmp_path, event_id
                    )
                    logger.info(
                        f"✅ Legacy storage complete: {len(saved_face_ids)} faces "
                        f"for event {event_id}"
                    )

            response = {
                "status": "success" if results else "no_faces_detected",
                "faces_count": len(results),
                "faces": results,
                "event_id": event_id,
                "processing_method": "face_extraction_crops",
            }
            logger.info(
                f"📤 Returning response: {response['status']}, "
                f"{response['faces_count']} faces"
            )
            return response

        except Exception as e:
            logger.error(f"❌ Error in face recognition: {e}")
            logger.exception("Full exception details:")
            error_response = {
                "error": str(e),
                "event_id": event_id,
                "status": "error",
                "faces_count": 0,
                "faces": [],
            }
            logger.error(f"🚨 Returning error response: {error_response}")
            return error_response, 500
        finally:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    logger.info(f"🗑️ Cleaned up temporary file: {tmp_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to clean up temp file: {e}")


@ns.route("/")
class UnclassifiedFaces(Resource):
    @api.marshal_list_with(models["face_model"])
    @api.doc("get_unclassified_faces")
    def get(self) -> List[Dict[str, Any]]:
        """Get list of unclassified faces

        Returns all faces that have been detected but not yet assigned to a
        person.
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
    ui_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "ui")
    )  # noqa: E501
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
    ui_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "ui")
    )  # noqa: E501
    return send_from_directory(ui_dir, "loadSnapshot.html")


@app.route("/debug/test-webp", methods=["POST"])
def debug_test_webp() -> Any:
    """Debug endpoint to test WEBP processing without decorators"""
    import traceback

    try:
        logger.info("🔍 Debug WEBP test endpoint called")

        # Get raw JSON data
        data = request.get_json()
        if not data:
            return {"error": "No JSON data"}, 400

        if "image_base64" not in data:
            return {"error": "Missing image_base64"}, 400

        image_base64 = data["image_base64"]

        logger.info(f"📊 Received base64 length: {len(image_base64)}")

        # Decode base64
        try:
            image_data = base64.b64decode(image_base64)
            logger.info(f"✅ Base64 decoded: {len(image_data)} bytes")
        except Exception as e:
            logger.error(f"❌ Base64 decode failed: {e}")
            return {"error": f"Base64 decode failed: {str(e)}"}, 400

        # Check format
        if image_data.startswith(b"RIFF") and b"WEBP" in image_data[:12]:
            extension = ".webp"
            logger.info("🖼️ Format: WEBP")
        elif image_data.startswith(b"\xFF\xD8\xFF"):
            extension = ".jpg"
            logger.info("🖼️ Format: JPEG")
        else:
            extension = ".png"
            logger.info("🖼️ Format: Other/PNG")

        # Save temporarily
        tmp_dir = "/app/data/tmp"
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(
            tmp_dir, f"debug-{uuid.uuid4().hex}{extension}"
        )  # noqa: E501

        with open(tmp_path, "wb") as f:
            f.write(image_data)
        logger.info(f"💾 Saved to: {tmp_path}")

        # Test face recognition
        try:
            results = clasificador.identify_all_faces(tmp_path)
            logger.info(f"🎉 Face recognition OK: {len(results)} faces")

            return {
                "status": "success",
                "message": "Debug test completed successfully",
                "faces_count": len(results),
                "faces": results,
                "format": extension,
                "file_size": len(image_data),
            }

        except Exception as e:
            logger.error(f"❌ Face recognition failed: {e}")
            logger.exception("Face recognition exception:")
            return {
                "status": "error",
                "message": f"Face recognition failed: {str(e)}",
                "format": extension,
                "file_size": len(image_data),
                "traceback": traceback.format_exc(),
            }

        finally:
            # Cleanup
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    logger.info(f"🗑️ Cleaned up: {tmp_path}")
            except Exception:
                pass

    except Exception as e:
        logger.error(f"❌ Debug endpoint failed: {e}")
        logger.exception("Debug endpoint exception:")
        return {
            "status": "error",
            "message": f"Debug endpoint failed: {str(e)}",
            "traceback": traceback.format_exc(),
        }


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
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    if not uuid_pattern.match(face_id):
        return {"error": "Invalid face ID format"}, 400

    try:
        # Get face data with thumbnail loaded (supports both storage formats)
        face = clasificador.get_face_with_thumbnail(face_id)

        if not face:
            return {"error": "Face not found"}, 404

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
    # Disable debug mode in production to prevent Flask reloader conflicts
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5001, debug=debug_mode)
