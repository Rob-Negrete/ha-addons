"""
Simplified API integration tests for the new Qdrant architecture.
Tests essential API endpoints without relying on deprecated TinyDB code.
"""
import json

import pytest


@pytest.mark.integration
class TestAPIIntegration:
    """Essential API integration tests"""

    def test_ping_endpoint(self, flask_test_client):
        """Test that the ping endpoint works"""
        # Try different potential paths
        paths_to_try = ["/face-rekon/ping", "/api/face-rekon/ping", "/ping"]

        for path in paths_to_try:
            response = flask_test_client.get(path)
            if response.status_code == 200:
                data = json.loads(response.data)
                if "pong" in data and data["pong"] is True:
                    # Found the working endpoint
                    assert True
                    return

        # If we get here, none of the paths worked - fail with useful info
        response = flask_test_client.get("/face-rekon/ping")
        assert False, (
            f"Ping endpoint not found. "
            f"Last response: {response.status_code}, {response.data}"
        )

    def test_face_recognition_endpoint_basic(self, flask_test_client, test_images):
        """Test basic face recognition endpoint functionality"""
        # Use a simple test image
        test_image = test_images["red_square"]
        request_data = {
            "image_base64": test_image["base64"],
            "event_id": "api_integration_test",
        }

        # Try different potential paths
        paths_to_try = [
            "/face-rekon/recognize",
            "/api/face-rekon/recognize",
            "/recognize",
        ]

        for path in paths_to_try:
            response = flask_test_client.post(
                path, data=json.dumps(request_data), content_type="application/json"
            )
            if response.status_code == 200:
                result = json.loads(response.data)
                if "status" in result and result["status"] in [
                    "success",
                    "no_faces_detected",
                ]:
                    assert True
                    return

        # If we get here, none worked
        response = flask_test_client.post(
            "/face-rekon/recognize",
            data=json.dumps(request_data),
            content_type="application/json",
        )
        assert False, (
            f"Recognize endpoint not found. "
            f"Last response: {response.status_code}, {response.data}"
        )

    def test_get_unclassified_faces_endpoint(self, flask_test_client):
        """Test getting unclassified faces endpoint"""
        # Try different potential paths
        paths_to_try = ["/face-rekon/", "/api/face-rekon/", "/"]

        for path in paths_to_try:
            response = flask_test_client.get(path)
            if response.status_code == 200:
                try:
                    data = json.loads(response.data)
                    if isinstance(data, list):
                        assert True
                        return
                except Exception:
                    continue

        # If we get here, none worked
        response = flask_test_client.get("/face-rekon/")
        assert False, (
            f"Unclassified faces endpoint not found. "
            f"Last response: {response.status_code}, {response.data}"
        )
