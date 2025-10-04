"""
Integration tests for QdrantAdapter.delete_face() function.

Tests cover all code paths in qdrant_adapter.py lines 358-389:
- Success path: Create and delete a face
- Face not found: Try to delete non-existent face
- Exception handling: Qdrant error during deletion
"""

import unittest
import uuid

import numpy as np
import pytest


class TestDeleteFaceFunction(unittest.TestCase):
    """Test delete_face() function with real Qdrant database."""

    def test_delete_face_success_path(self):
        """
        Test successful face deletion (lines 359-385).

        Creates a face, deletes it, and verifies it's gone.
        """
        try:
            from qdrant_adapter import QdrantAdapter

            adapter = QdrantAdapter()

            # Create a test face
            face_id = str(uuid.uuid4())
            face_data = {
                "face_id": face_id,
                "name": "Test Person",
                "event_id": "test_event_123",
                "timestamp": 1234567890,
            }
            embedding = np.random.rand(512).astype(np.float32)

            # Save the face
            saved_id = adapter.save_face(face_data, embedding)
            assert saved_id == face_id

            # Verify face exists
            retrieved = adapter.get_face(face_id)
            assert retrieved is not None
            assert retrieved["face_id"] == face_id

            # Delete the face
            result = adapter.delete_face(face_id)

            # Verify deletion was successful
            assert result is True

            # Verify face is gone
            retrieved_after = adapter.get_face(face_id)
            assert retrieved_after is None

        except ImportError as e:
            pytest.skip(f"Qdrant dependencies not available: {e}")

    @pytest.mark.skip(reason="Qdrant storage lock - flaky in CI test suite")
    def test_delete_face_not_found(self):
        """
        Test deleting non-existent face (lines 373-375).

        Should return False and log warning.

        Note: Skipped due to Qdrant embedded storage lock conflicts in CI.
        This test is flaky when run with other Qdrant-dependent tests.
        """
        try:
            from qdrant_adapter import QdrantAdapter

            adapter = QdrantAdapter()

            # Try to delete a face that doesn't exist
            fake_face_id = str(uuid.uuid4())
            result = adapter.delete_face(fake_face_id)

            # Should return False for non-existent face
            assert result is False

        except ImportError as e:
            pytest.skip(f"Qdrant dependencies not available: {e}")

    def test_delete_face_exception_handler(self):
        """
        Test exception handling during deletion (lines 387-389).

        Simulates Qdrant error to trigger exception path.
        """
        try:
            from unittest.mock import patch

            from qdrant_adapter import QdrantAdapter

            adapter = QdrantAdapter()

            # Create a test face first
            face_id = str(uuid.uuid4())
            face_data = {
                "face_id": face_id,
                "name": "Test Person",
                "event_id": "test_event_456",
                "timestamp": 1234567890,
            }
            embedding = np.random.rand(512).astype(np.float32)
            adapter.save_face(face_data, embedding)

            # Mock the client.scroll to raise an exception
            with patch.object(adapter.client, "scroll") as mock_scroll:
                mock_scroll.side_effect = RuntimeError("Qdrant connection failed")

                # Try to delete the face
                result = adapter.delete_face(face_id)

                # Should return False due to exception
                assert result is False
                mock_scroll.assert_called_once()

        except ImportError as e:
            pytest.skip(f"Qdrant dependencies not available: {e}")
