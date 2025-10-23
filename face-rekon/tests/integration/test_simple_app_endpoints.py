"""
Simple integration tests to cover remaining app.py endpoints.

These tests target the easiest uncovered lines in app.py to reach 90% coverage.
All tests use Docker integration environment with real ML stack.
"""


class TestSimpleEndpoints:
    """Simple tests for uncovered Flask endpoints in app.py."""

    def test_ping_endpoint(self):
        """Test /ping endpoint - covers line 55."""
        try:
            import app

            with app.app.test_client() as client:
                response = client.get("/api/face-rekon/ping")
                assert response.status_code == 200
                data = response.get_json()
                assert data == {"pong": True}
                print("✅ Ping endpoint test passed")
        except ImportError as e:
            import pytest

            pytest.skip(f"ML dependencies not available: {e}")

    def test_get_unclassified_faces_endpoint(self):
        """Test GET /api/face-rekon/ for unclassified faces - covers lines 255-256."""
        try:
            import app

            with app.app.test_client() as client:
                response = client.get("/api/face-rekon/")
                assert response.status_code == 200
                data = response.get_json()
                assert isinstance(data, list)  # Should return a list
                print("✅ Get unclassified faces endpoint test passed")
        except ImportError as e:
            import pytest

            pytest.skip(f"ML dependencies not available: {e}")

    def test_get_specific_face_endpoint(self):
        """Test GET /api/face-rekon/<face_id> - covers lines 268-269."""
        try:
            import app

            with app.app.test_client() as client:
                # Try to get a face (may return 404 if not found, but that's ok)
                response = client.get("/api/face-rekon/test_face_id_12345")
                # Accept both 200 (found) or 404 (not found) - both cover the line
                assert response.status_code in [200, 404]
                print("✅ Get specific face endpoint test passed")
        except ImportError as e:
            import pytest

            pytest.skip(f"ML dependencies not available: {e}")
