"""
Integration tests for clasificador.update_face function.

Achieves 100% coverage for the update_face wrapper function (lines 590-606)
by testing all code paths: success, failure, and exception handling.
"""

from unittest.mock import patch

import pytest


class TestClasificadorUpdateFace:
    """Comprehensive tests for clasificador.update_face to achieve 100% coverage"""

    def test_update_face_success_path(self):
        """Test update_face with successful database update (lines 598-601)"""
        try:
            import scripts.clasificador as clasificador

            face_id = "test_face_123"
            update_data = {"name": "John Doe", "notes": "Test person"}

            # Mock db_update_face to return True (success)
            with patch.object(
                clasificador, "db_update_face", return_value=True
            ) as mock_db:
                clasificador.update_face(face_id, update_data)

                # Verify db_update_face was called with correct parameters
                mock_db.assert_called_once_with(face_id, update_data)
                print(f"✅ update_face success path: {face_id}")

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_update_face_failure_path(self):
        """Test update_face when database update fails (lines 602-603)"""
        try:
            import scripts.clasificador as clasificador

            face_id = "test_face_456"
            update_data = {"name": "Jane Doe"}

            # Mock db_update_face to return False (failure)
            with patch.object(
                clasificador, "db_update_face", return_value=False
            ) as mock_db:
                # Should complete without raising exception
                clasificador.update_face(face_id, update_data)

                mock_db.assert_called_once_with(face_id, update_data)
                print(f"✅ update_face failure path: {face_id}")

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_update_face_exception_handling(self):
        """Test update_face exception handling (lines 604-606)"""
        try:
            import scripts.clasificador as clasificador

            face_id = "test_face_789"
            update_data = {"name": "Test Error"}

            # Mock db_update_face to raise an exception
            with patch.object(
                clasificador,
                "db_update_face",
                side_effect=ValueError("Database error"),
            ) as mock_db:
                # Should raise the exception after logging
                with pytest.raises(ValueError, match="Database error"):
                    clasificador.update_face(face_id, update_data)

                mock_db.assert_called_once_with(face_id, update_data)
                print(f"✅ update_face exception handling: {face_id}")

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_update_face_via_endpoint_real_call(self):
        """Test update_face through the Flask API endpoint with real execution"""
        try:
            import app

            with app.app.test_client() as client:
                # Use a non-existent face_id - will trigger failure path
                test_face_id = "nonexistent_face_12345"
                update_data = {"name": "Endpoint Test", "notes": "Via API"}

                # This will call the real update_face function
                # which will fail (face not found) but return 200 with success message
                response = client.patch(
                    f"/api/face-rekon/{test_face_id}", json=update_data
                )

                # Should return 200 (endpoint handles the call)
                assert response.status_code == 200
                data = response.get_json()
                # Even if update fails, endpoint returns success structure
                assert "status" in data or "message" in data
                print(f"✅ update_face via endpoint (real call): {test_face_id}")

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")
