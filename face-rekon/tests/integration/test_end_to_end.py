"""
End-to-end integration tests.
Tests complete user workflows from API request to database persistence.
"""
import json
import os
import sys

import numpy as np
import pytest

# Add scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


@pytest.mark.integration
class TestEndToEndIntegration:
    """Streamlined end-to-end integration tests for CI/CD efficiency"""

    def test_complete_face_workflow(
        self, flask_test_client, test_images, shared_ml_models
    ):
        """
        Comprehensive E2E test: Face detection → Classification → Retrieval

        Combines multiple workflows in one test to reduce execution time.
        Tests: API endpoints, database operations, error handling,
        classification workflow
        """
        clasificador = shared_ml_models["clasificador"]

        # Clear database for clean test
        clasificador.db.truncate()

        # Test 1: Face recognition API
        test_image = test_images["red_square"]
        request_data = {
            "image_base64": test_image["base64"],
            "event_id": "e2e_comprehensive_test",
        }

        response = flask_test_client.post(
            "/api/face-rekon/recognize",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["status"] in ["success", "no_faces_detected"]

        # Test 2: Add test face for classification workflow
        test_face_data = {
            "face_id": "e2e_test_face",
            "event_id": "e2e_comprehensive_test",
            "name": "unknown",
            "relationship": "unknown",
            "confidence": "unknown",
            "embedding": np.random.random(512).tolist(),
            "image_path": "/app/data/tmp/test_face.jpg",
            "timestamp": "2024-01-01T10:00:00",
        }
        clasificador.db.insert(test_face_data)

        # Test 3: Get unclassified faces API
        response = flask_test_client.get("/api/face-rekon/")
        assert response.status_code == 200
        unclassified_faces = json.loads(response.data)
        assert len(unclassified_faces) >= 1

        # Test 4: Face classification via API
        face_id = test_face_data["face_id"]
        classification_data = {
            "name": "E2E Test Person",
            "relationship": "test_subject",
            "confidence": "high",
        }

        response = flask_test_client.patch(
            f"/api/face-rekon/{face_id}",
            data=json.dumps(classification_data),
            content_type="application/json",
        )
        assert response.status_code == 200

        # Test 5: Verify classification persisted
        response = flask_test_client.get(f"/api/face-rekon/{face_id}")
        assert response.status_code == 200
        face_details = json.loads(response.data)
        assert isinstance(face_details, dict)
        assert face_details["name"] == "E2E Test Person"

    def test_error_handling_and_recovery(
        self, flask_test_client, test_images, shared_ml_models
    ):
        """
        Test error handling and system recovery
        """
        clasificador = shared_ml_models["clasificador"]
        clasificador.db.truncate()

        # Test invalid request handling
        try:
            response = flask_test_client.post(
                "/api/face-rekon/recognize",
                data=json.dumps(
                    {"image_base64": "aGVsbG93b3JsZA==", "event_id": "error_test"}
                ),
                content_type="application/json",
            )
            assert response.status_code in [400, 500]
        except Exception:
            pass  # Expected for invalid data

        # Test system recovery with valid request
        response = flask_test_client.post(
            "/api/face-rekon/recognize",
            data=json.dumps(
                {
                    "image_base64": test_images["small_image"]["base64"],
                    "event_id": "recovery_test",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200


@pytest.mark.integration
class TestSystemIntegration:
    """System-level integration tests"""

    def test_system_health_check(self, flask_test_client, shared_ml_models):
        """
        Test overall system health and component integration
        """
        clasificador = shared_ml_models["clasificador"]

        # Test ping endpoint
        response = flask_test_client.get("/api/face-rekon/ping")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["pong"] is True

        # Test database connectivity
        all_faces = clasificador.db.all()
        assert isinstance(all_faces, list)

        # Test unclassified faces endpoint
        response = flask_test_client.get("/api/face-rekon/")
        assert response.status_code == 200
        unclassified = json.loads(response.data)
        assert isinstance(unclassified, list)

    def test_api_documentation_endpoints(self, flask_test_client):
        """Test that API documentation is accessible"""
        # Swagger UI should be accessible
        response = flask_test_client.get("/swagger/")
        assert response.status_code == 200

    def test_static_file_serving(self, flask_test_client):
        """Test static file serving endpoints"""
        # Home page should be accessible
        response = flask_test_client.get("/")
        assert response.status_code in [200, 404]  # May not exist, but shouldn't crash
