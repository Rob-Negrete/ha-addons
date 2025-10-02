"""
Integration tests for save_multiple_faces_optimized() function.

Tests the complete face saving pipeline with real ML stack:
- Face detection and extraction
- Database operations (Qdrant)
- Event tracking and duplicate detection
- Error handling and edge cases

These tests run in Docker with full ML dependencies (InsightFace, OpenCV, Qdrant).
"""

import os
import uuid

import pytest


class TestSaveMultipleFacesOptimized:
    """Test save_multiple_faces_optimized() with real face images."""

    @pytest.fixture
    def test_images_dir(self):
        """Get path to test images directory."""
        return os.path.join(os.path.dirname(__file__), "..", "dummies")

    def test_save_multiple_faces_optimized_with_single_face(self, test_images_dir):
        """Test saving a single face from an image."""
        try:
            from scripts.clasificador import save_multiple_faces_optimized

            image_path = os.path.join(test_images_dir, "one-face.jpg")
            event_id = f"test-event-{uuid.uuid4()}"

            # Save faces
            saved_ids = save_multiple_faces_optimized(image_path, event_id)

            # Verify results
            assert isinstance(saved_ids, list)
            assert len(saved_ids) == 1, "Should save exactly 1 face"
            assert all(isinstance(fid, str) for fid in saved_ids)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_multiple_faces_optimized_with_multiple_faces(self, test_images_dir):
        """Test saving multiple faces from a single image."""
        try:
            from scripts.clasificador import save_multiple_faces_optimized

            image_path = os.path.join(test_images_dir, "two-faces.jpg")
            event_id = f"test-event-{uuid.uuid4()}"

            # Save faces
            saved_ids = save_multiple_faces_optimized(image_path, event_id)

            # Verify results
            assert isinstance(saved_ids, list)
            assert len(saved_ids) == 2, "Should save exactly 2 faces"
            assert all(isinstance(fid, str) for fid in saved_ids)
            # Verify face IDs are unique
            assert len(set(saved_ids)) == len(saved_ids), "Face IDs should be unique"

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_multiple_faces_optimized_with_many_faces(self, test_images_dir):
        """Test saving many faces from a single image."""
        try:
            from scripts.clasificador import save_multiple_faces_optimized

            image_path = os.path.join(test_images_dir, "twelve-faces.png")
            event_id = f"test-event-{uuid.uuid4()}"

            # Save faces
            saved_ids = save_multiple_faces_optimized(image_path, event_id)

            # Verify results
            assert isinstance(saved_ids, list)
            assert len(saved_ids) == 12, "Should save exactly 12 faces"
            assert all(isinstance(fid, str) for fid in saved_ids)
            # Verify all face IDs are unique
            assert len(set(saved_ids)) == len(saved_ids), "Face IDs should be unique"

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_multiple_faces_optimized_no_faces_detected(self, test_images_dir):
        """Test behavior when no faces are detected in image."""
        try:
            from scripts.clasificador import save_multiple_faces_optimized

            image_path = os.path.join(test_images_dir, "zero-faces.jpg")
            event_id = f"test-event-{uuid.uuid4()}"

            # Save faces (should return empty list)
            saved_ids = save_multiple_faces_optimized(image_path, event_id)

            # Verify results
            assert isinstance(saved_ids, list)
            assert (
                len(saved_ids) == 0
            ), "Should return empty list when no faces detected"

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_multiple_faces_optimized_duplicate_detection(self, test_images_dir):
        """Test duplicate event detection - should skip processing."""
        try:
            from scripts.clasificador import save_multiple_faces_optimized

            image_path = os.path.join(test_images_dir, "one-face.jpg")
            event_id = f"test-event-{uuid.uuid4()}"

            # First save - should succeed
            saved_ids_1 = save_multiple_faces_optimized(image_path, event_id)
            assert len(saved_ids_1) == 1, "First save should succeed"

            # Second save with same event_id - should detect duplicate and return empty
            saved_ids_2 = save_multiple_faces_optimized(image_path, event_id)
            assert isinstance(saved_ids_2, list)
            assert (
                len(saved_ids_2) == 0
            ), "Should skip duplicate event and return empty list"

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_multiple_faces_optimized_invalid_image_path(self):
        """Test error handling for invalid image path."""
        try:
            from scripts.clasificador import save_multiple_faces_optimized

            invalid_path = "/nonexistent/path/to/image.jpg"
            event_id = f"test-event-{uuid.uuid4()}"

            # Should handle error gracefully and return empty list
            saved_ids = save_multiple_faces_optimized(invalid_path, event_id)

            assert isinstance(saved_ids, list)
            assert len(saved_ids) == 0, "Should return empty list for invalid path"

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_multiple_faces_optimized_metadata_structure(self, test_images_dir):
        """Test that saved faces have correct metadata structure."""
        try:
            from scripts.clasificador import save_multiple_faces_optimized
            from scripts.qdrant_adapter import db_get_face

            image_path = os.path.join(test_images_dir, "one-face.jpg")
            event_id = f"test-event-{uuid.uuid4()}"

            # Save face
            saved_ids = save_multiple_faces_optimized(image_path, event_id)
            assert len(saved_ids) == 1

            # Retrieve saved face and verify metadata
            face_id = saved_ids[0]
            face_data = db_get_face(face_id)

            assert face_data is not None, "Should be able to retrieve saved face"

            # Verify metadata fields
            metadata = face_data.get("metadata", {})
            assert "face_id" in metadata
            assert "name" in metadata
            assert metadata["name"] == "unknown", "Initial name should be 'unknown'"
            assert "event_id" in metadata
            assert metadata["event_id"] == event_id
            assert "timestamp" in metadata
            assert "thumbnail_path" in metadata
            assert "confidence" in metadata
            assert "quality_metrics" in metadata
            assert "face_bbox" in metadata
            assert "notes" in metadata

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_multiple_faces_optimized_event_id_tracking(self, test_images_dir):
        """Test that event_id is properly tracked across multiple faces."""
        try:
            from scripts.clasificador import save_multiple_faces_optimized
            from scripts.qdrant_adapter import db_get_face

            image_path = os.path.join(test_images_dir, "two-faces.jpg")
            event_id = f"test-event-{uuid.uuid4()}"

            # Save faces
            saved_ids = save_multiple_faces_optimized(image_path, event_id)
            assert len(saved_ids) == 2

            # Verify both faces have same event_id
            for face_id in saved_ids:
                face_data = db_get_face(face_id)
                assert face_data is not None
                metadata = face_data.get("metadata", {})
                assert (
                    metadata["event_id"] == event_id
                ), "All faces should have same event_id"

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_multiple_faces_optimized_timestamp_generation(self, test_images_dir):
        """Test that timestamps are generated for saved faces."""
        try:
            import time

            from scripts.clasificador import save_multiple_faces_optimized
            from scripts.qdrant_adapter import db_get_face

            image_path = os.path.join(test_images_dir, "one-face.jpg")
            event_id = f"test-event-{uuid.uuid4()}"

            before_timestamp = int(time.time() * 1000)

            # Save face
            saved_ids = save_multiple_faces_optimized(image_path, event_id)
            assert len(saved_ids) == 1

            after_timestamp = int(time.time() * 1000)

            # Verify timestamp is within reasonable range
            face_data = db_get_face(saved_ids[0])
            assert face_data is not None
            metadata = face_data.get("metadata", {})

            timestamp = metadata["timestamp"]
            assert isinstance(timestamp, int)
            assert (
                before_timestamp <= timestamp <= after_timestamp
            ), "Timestamp should be generated during save operation"

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_multiple_faces_optimized_quality_metrics_included(
        self, test_images_dir
    ):
        """Test that quality metrics are included in saved metadata."""
        try:
            from scripts.clasificador import save_multiple_faces_optimized
            from scripts.qdrant_adapter import db_get_face

            image_path = os.path.join(test_images_dir, "one-face.jpg")
            event_id = f"test-event-{uuid.uuid4()}"

            # Save face
            saved_ids = save_multiple_faces_optimized(image_path, event_id)
            assert len(saved_ids) == 1

            # Verify quality metrics
            face_data = db_get_face(saved_ids[0])
            assert face_data is not None
            metadata = face_data.get("metadata", {})

            quality_metrics = metadata["quality_metrics"]
            assert isinstance(quality_metrics, dict)
            assert "quality_score" in quality_metrics
            assert isinstance(quality_metrics["quality_score"], (int, float))

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_multiple_faces_optimized_embedding_saved(self, test_images_dir):
        """Test that face embeddings are saved to database."""
        try:
            from scripts.clasificador import save_multiple_faces_optimized
            from scripts.qdrant_adapter import db_get_face

            image_path = os.path.join(test_images_dir, "one-face.jpg")
            event_id = f"test-event-{uuid.uuid4()}"

            # Save face
            saved_ids = save_multiple_faces_optimized(image_path, event_id)
            assert len(saved_ids) == 1

            # Verify embedding exists
            face_data = db_get_face(saved_ids[0])
            assert face_data is not None

            # Check that embedding vector exists
            assert (
                "embedding" in face_data or "vector" in face_data
            ), "Face data should include embedding vector"

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")
