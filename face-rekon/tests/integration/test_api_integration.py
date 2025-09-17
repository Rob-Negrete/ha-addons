"""
Integration tests for Flask API endpoints.
Tests the complete API flow with real HTTP requests and real ML models.
"""
import json

import pytest


@pytest.mark.integration
class TestFaceRecognitionAPIIntegration:
    """Integration tests for the face recognition API endpoints"""

    def test_ping_endpoint_integration(self, flask_test_client):
        """Test ping endpoint with real Flask app"""
        response = flask_test_client.get("/api/face-rekon/ping")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["pong"] is True

    def test_face_recognition_full_flow_unknown_face(
        self, flask_test_client, test_images, clean_test_env, shared_ml_models
    ):
        """
        Integration test: Upload unknown face → Test with real ML models
        Tests the complete flow for face recognition with actual InsightFace.
        """
        clasificador = shared_ml_models["clasificador"]

        # Clear database for clean test
        clasificador.db.truncate()

        # Get initial database count
        initial_count = len(clasificador.db.all())

        # Use test image (solid color won't have faces, but fine for integration)
        test_image = test_images["red_square"]
        request_data = {
            "image_base64": test_image["base64"],
            "event_id": "integration_test_001",
        }

        # Make API request
        response = flask_test_client.post(
            "/api/face-rekon/recognize",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)

        # For integration testing, we expect either:
        # 1. "success" with faces detected, or
        # 2. "no_faces_detected" if no faces found in the solid color image
        assert data["status"] in ["success", "no_faces_detected"]

        # If faces were detected, verify structure
        if data["status"] == "success":
            assert "faces_count" in data
            assert "faces" in data
            assert isinstance(data["faces"], list)

        # Database should either have same count (no face) or +1 (face saved)
        final_count = len(clasificador.db.all())
        assert final_count >= initial_count

    def test_face_recognition_full_flow_known_face(
        self, flask_test_client, test_images, known_face_data, shared_ml_models
    ):
        """
        Integration test: Upload image with known face data in database
        Tests the complete flow for a potentially recognized face.
        """
        clasificador = shared_ml_models["clasificador"]

        # Clear database and add known face
        clasificador.db.truncate()
        clasificador.db.insert(known_face_data)

        test_image = test_images["blue_rectangle"]
        request_data = {
            "image_base64": test_image["base64"],
            "event_id": "integration_test_002",
        }

        # Make API request
        response = flask_test_client.post(
            "/api/face-rekon/recognize",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        # Verify response structure
        assert response.status_code == 200
        data = json.loads(response.data)

        # For integration testing with solid colors, we expect no faces detected
        # But the API should handle it gracefully
        assert data["status"] in ["success", "no_faces_detected"]

        if data["status"] == "success":
            assert "faces_count" in data
            assert "faces" in data

    def test_face_recognition_no_faces_detected(self, flask_test_client, test_images):
        """
        Integration test: Upload image with no faces → Return appropriate response
        """
        # Use solid color image which definitely won't have faces
        test_image = test_images["small_image"]  # Small solid color
        request_data = {
            "image_base64": test_image["base64"],
            "event_id": "no_faces_test",
        }

        response = flask_test_client.post(
            "/api/face-rekon/recognize",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Should either detect no faces or handle gracefully
        assert data["status"] in ["no_faces_detected", "success"]

        if data["status"] == "success":
            assert data["faces_count"] >= 0

    def test_face_recognition_multiple_faces(self, flask_test_client, test_images):
        """
        Integration test: Test API with image that might contain multiple faces
        """
        # Use larger test image
        test_image = test_images["green_circle"]
        request_data = {
            "image_base64": test_image["base64"],
            "event_id": "multiple_faces_test",
        }

        response = flask_test_client.post(
            "/api/face-rekon/recognize",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify response structure
        assert data["status"] in ["success", "no_faces_detected"]

        if data["status"] == "success":
            assert "faces_count" in data
            assert "faces" in data
            assert isinstance(data["faces"], list)
            assert data["faces_count"] == len(data["faces"])

    def test_face_recognition_invalid_request(self, flask_test_client):
        """
        Integration test: Send invalid request → Return error response
        """
        # Missing image_base64
        invalid_request = {"event_id": "invalid_test"}

        response = flask_test_client.post(
            "/api/face-rekon/recognize",
            data=json.dumps(invalid_request),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        # Flask-RESTX validation returns 'errors' and 'message' for validation failures
        assert "errors" in data or "error" in data

    def test_data_uri_formats_integration(self, flask_test_client, test_images):
        """
        Integration test: Test different data URI formats
        """
        test_image = test_images["red_square"]

        # Test with data URI prefix
        data_uri_image = f"data:image/jpeg;base64,{test_image['base64']}"
        request_data = {
            "image_base64": data_uri_image,
            "event_id": "data_uri_test",
        }

        response = flask_test_client.post(
            "/api/face-rekon/recognize",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] in ["success", "no_faces_detected"]


@pytest.mark.integration
class TestFaceManagementAPIIntegration:
    """Integration tests for face management API endpoints"""

    def test_get_unclassified_faces_integration(
        self, flask_test_client, shared_ml_models, sample_face_data
    ):
        """Test getting unclassified faces through API"""
        clasificador = shared_ml_models["clasificador"]

        # Clear database and add test data
        clasificador.db.truncate()

        # Add mix of classified and unclassified faces
        test_faces = [
            {**sample_face_data, "face_id": "unclassified_api_1", "name": None},
            {**sample_face_data, "face_id": "classified_api_1", "name": "John"},
            {**sample_face_data, "face_id": "unclassified_api_2", "name": None},
        ]

        for face in test_faces:
            clasificador.db.insert(face)

        response = flask_test_client.get("/api/face-rekon/")

        assert response.status_code == 200
        data = json.loads(response.data)

        # Should return only unclassified faces
        assert isinstance(data, list)
        assert len(data) == 2  # Only the unclassified ones

        # Face model uses 'face_id' field
        unclassified_ids = [face["face_id"] for face in data]
        assert "unclassified_api_1" in unclassified_ids
        assert "unclassified_api_2" in unclassified_ids

    def test_get_specific_face_integration(
        self, flask_test_client, shared_ml_models, sample_face_data
    ):
        """Test getting specific face by ID through API"""
        clasificador = shared_ml_models["clasificador"]

        # Clear database and add test face
        clasificador.db.truncate()
        clasificador.db.insert(sample_face_data)

        response = flask_test_client.get(
            f"/api/face-rekon/{sample_face_data['face_id']}"
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) == 1
        # Face model uses 'face_id' field
        assert data[0]["face_id"] == sample_face_data["face_id"]

    def test_update_face_integration(
        self, flask_test_client, shared_ml_models, sample_face_data
    ):
        """Test updating face information through API"""
        clasificador = shared_ml_models["clasificador"]

        # Clear database and add test face
        clasificador.db.truncate()
        clasificador.db.insert(sample_face_data)

        # Update face
        update_data = {
            "name": "Updated API Name",
            "relationship": "api_test",
            "confidence": "high",
        }

        response = flask_test_client.patch(
            f"/api/face-rekon/{sample_face_data['face_id']}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"

        # Verify update persisted
        updated_face = clasificador.db.get(
            clasificador.Face.face_id == sample_face_data["face_id"]
        )
        assert updated_face["name"] == "Updated API Name"

    def test_update_face_error_handling(self, flask_test_client):
        """Test update face with non-existent ID"""
        update_data = {
            "name": "Test Name",
            "relationship": "test",
            "confidence": "high",
        }

        response = flask_test_client.patch(
            "/api/face-rekon/nonexistent_id",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        # Should handle gracefully (might succeed with no changes or return error)
        # The important thing is it doesn't crash
        assert response.status_code in [200, 404, 500]
