from typing import Any, Dict

from flask_restx import Api, fields


def create_models(api: Api) -> Dict[str, Any]:
    """Create and return API models for Flask-RESTX documentation"""

    ping_model = api.model(
        "PingResponse",
        {"pong": fields.Boolean(description="Pong response", example=True)},
    )

    recognize_request_model = api.model(
        "RecognizeRequest",
        {
            "image_base64": fields.String(
                required=True, description="Base64 encoded image data"
            ),
            "event_id": fields.String(
                required=True, description="Event identifier for tracking"
            ),
        },
    )

    face_result_model = api.model(
        "FaceResult",
        {
            "status": fields.String(
                description="Recognition status (known/unknown)",
                example="known",  # noqa: E501
            ),
            "name": fields.String(
                description="Person name if recognized", example="John Doe"
            ),
            "confidence": fields.Float(
                description="Recognition confidence score", example=0.85
            ),
            "face_id": fields.String(description="Unique face identifier"),
        },
    )

    recognize_response_model = api.model(
        "RecognizeResponse",
        {
            "status": fields.String(
                description="Overall processing status", example="success"
            ),
            "faces_count": fields.Integer(
                description="Number of faces detected", example=1
            ),
            "faces": fields.List(
                fields.Nested(face_result_model),
                description="List of detected faces",  # noqa: E501
            ),
            "event_id": fields.String(
                description="Event identifier for tracking",
                example="event-123",  # noqa: E501
            ),
            "processing_method": fields.String(
                description="Processing method used",
                example="face_extraction_crops",  # noqa: E501
            ),
            "error": fields.String(
                description="Error message if processing failed",
                required=False,  # noqa: E501
            ),
        },
    )

    face_model = api.model(
        "Face",
        {
            "face_id": fields.String(description="Face ID"),
            "name": fields.String(description="Person name"),
            "timestamp": fields.String(description="When face was detected"),
            "event_id": fields.String(description="Associated event ID"),
            "image_path": fields.String(description="Path to face image"),
            "thumbnail": fields.String(description="Path to thumbnail image"),
            "relationship": fields.String(description="Relationship to owner"),
            "confidence": fields.String(description="Confidence level"),
        },
    )

    face_update_model = api.model(
        "FaceUpdate",
        {
            "name": fields.String(description="Person name to assign to face"),
            "notes": fields.String(
                description="Additional notes about the person"
            ),  # noqa: E501
        },
    )

    update_response_model = api.model(
        "UpdateResponse",
        {
            "status": fields.String(
                description="Update status", example="success"
            ),  # noqa: E501
            "message": fields.String(description="Status message"),
        },
    )

    error_model = api.model(
        "Error", {"error": fields.String(description="Error message")}
    )

    return {
        "ping_model": ping_model,
        "recognize_request_model": recognize_request_model,
        "face_result_model": face_result_model,
        "recognize_response_model": recognize_response_model,
        "face_model": face_model,
        "face_update_model": face_update_model,
        "update_response_model": update_response_model,
        "error_model": error_model,
    }
