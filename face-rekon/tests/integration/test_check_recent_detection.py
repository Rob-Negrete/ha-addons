"""
Integration tests for QdrantAdapter.check_recent_detection() function.

Tests cover all code paths in qdrant_adapter.py lines 401-434:
- Deduplication disabled (DEDUPLICATION_WINDOW <= 0)
- No recent detections found
- Recent detection found within time window
- Exception handling during check

Uses shared Qdrant adapter fixture to avoid storage locking issues.
"""

import time
import uuid

import numpy as np
import pytest


class TestCheckRecentDetectionFunction:
    """Test check_recent_detection() function with shared Qdrant adapter."""

    def test_check_recent_detection_no_recent_faces(self, qdrant_adapter):
        """
        Test when no recent detections exist (lines 404-423, 430).

        Should return False when event_id has no faces in time window.

        Args:
            qdrant_adapter: Shared Qdrant adapter fixture (auto-cleaned)
        """
        # Use a unique event_id that definitely doesn't exist
        unique_event_id = f"test_event_{uuid.uuid4()}"

        # Check for recent detection (should be False - no faces)
        result = qdrant_adapter.check_recent_detection(unique_event_id)

        assert result is False

    def test_check_recent_detection_found(self, qdrant_adapter):
        """
        Test when recent detection is found (lines 404-430).

        Save a face then immediately check - should find it.

        Args:
            qdrant_adapter: Shared Qdrant adapter fixture (auto-cleaned)
        """
        # Create and save a face with current timestamp
        event_id = f"test_event_{uuid.uuid4()}"
        face_id = str(uuid.uuid4())

        face_data = {
            "face_id": face_id,
            "name": "Test Person",
            "event_id": event_id,
            "timestamp": int(time.time()),  # Current time
        }

        embedding = np.random.rand(512).astype(np.float32)

        # Save the face
        saved_id = qdrant_adapter.save_face(face_data, embedding)
        assert saved_id == face_id

        # Check for recent detection (should be True)
        result = qdrant_adapter.check_recent_detection(event_id)

        # Should find the recent detection
        assert result is True

    def test_check_recent_detection_outside_window(self, qdrant_adapter):
        """
        Test when detection exists but is outside time window (lines 404-430).

        Save a face with old timestamp - should not find it.

        Args:
            qdrant_adapter: Shared Qdrant adapter fixture (auto-cleaned)
        """
        from qdrant_adapter import DEDUPLICATION_WINDOW

        # Only run if deduplication is enabled
        if not DEDUPLICATION_WINDOW or DEDUPLICATION_WINDOW <= 0:
            pytest.skip("Deduplication window disabled")

        # Create face with timestamp outside window
        event_id = f"test_event_{uuid.uuid4()}"
        face_id = str(uuid.uuid4())

        # Timestamp older than deduplication window
        old_timestamp = int(time.time()) - (DEDUPLICATION_WINDOW + 100)

        face_data = {
            "face_id": face_id,
            "name": "Old Face",
            "event_id": event_id,
            "timestamp": old_timestamp,
        }

        embedding = np.random.rand(512).astype(np.float32)

        # Save the old face
        qdrant_adapter.save_face(face_data, embedding)

        # Check for recent detection (should be False - too old)
        result = qdrant_adapter.check_recent_detection(event_id)

        assert result is False

    def test_check_recent_detection_exception_handler(self, qdrant_adapter):
        """
        Test exception handling during check (lines 432-434).

        Mock Qdrant client error to trigger exception path.

        Args:
            qdrant_adapter: Shared Qdrant adapter fixture (auto-cleaned)
        """
        from unittest.mock import patch

        # Mock client.scroll to raise an exception
        with patch.object(qdrant_adapter.client, "scroll") as mock_scroll:
            mock_scroll.side_effect = RuntimeError("Qdrant connection failed")

            # Try to check recent detection
            result = qdrant_adapter.check_recent_detection("test_event_error")

            # Should return False due to exception
            assert result is False
            mock_scroll.assert_called_once()
