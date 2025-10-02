"""
Integration tests for identify_all_faces function in clasificador.py

Tests use REAL face images to validate face identification, recognition matching,
status determination, and error handling with actual ML pipeline.
"""

import os
import sys

import pytest

# Add the scripts directory to the Python path
scripts_path = os.path.join(os.path.dirname(__file__), "../../scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Import ML dependencies - will work in Docker, may fail locally
try:
    from clasificador import identify_all_faces

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class TestIdentifyAllFacesRealImages:
    """Comprehensive integration tests for identify_all_faces() using real images."""

    @pytest.fixture
    def test_images_dir(self):
        """Get path to test images directory"""
        return os.path.join(os.path.dirname(__file__), "..", "dummies")

    def test_identify_all_faces_with_image(self, test_images_dir):
        """Test identification with real face image"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "one-face.jpg")
        results = identify_all_faces(image_path)

        # Should detect face and return result
        assert len(results) == 1
        assert "status" in results[0]
        assert "name" in results[0]
        assert "face_id" in results[0]
        assert "confidence" in results[0]
        assert "quality_score" in results[0]
        assert "face_bbox" in results[0]

    def test_identify_all_faces_no_faces_detected(self, test_images_dir):
        """Test identification when no faces are detected in image"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "zero-faces.jpg")
        results = identify_all_faces(image_path)

        # Should return empty list
        assert results == []

    def test_identify_all_faces_multiple_faces(self, test_images_dir):
        """Test identification with multiple faces in image"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "two-faces.jpg")
        results = identify_all_faces(image_path)

        # Should detect and process 2 faces
        assert len(results) == 2

        # All should have required fields
        for result in results:
            assert "face_id" in result
            assert "status" in result
            assert "confidence" in result
            assert "quality_score" in result
            assert "face_bbox" in result

    def test_identify_all_faces_twelve_faces(self, test_images_dir):
        """Test identification with twelve faces in image"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "twelve-faces.png")
        results = identify_all_faces(image_path)

        # Should detect and process 12 faces
        assert len(results) == 12

        # All should have required fields
        for result in results:
            assert "status" in result
            assert "name" in result
            assert result["status"] in ["identified", "suggestion", "unknown"]

    def test_identify_all_faces_invalid_image_path(self):
        """Test error handling with invalid image path"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        results = identify_all_faces("/nonexistent/image.jpg")

        # Should return empty list on error
        assert results == []

    def test_identify_all_faces_confidence_and_quality_scores(self, test_images_dir):
        """Test that confidence and quality_score are included"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "one-face.jpg")
        results = identify_all_faces(image_path)

        assert len(results) >= 1
        assert "confidence" in results[0]
        assert "quality_score" in results[0]
        assert isinstance(results[0]["confidence"], float)
        assert isinstance(results[0]["quality_score"], float)
        assert 0.0 <= results[0]["confidence"] <= 1.0
        assert 0.0 <= results[0]["quality_score"] <= 1.0

    def test_identify_all_faces_face_bbox_included(self, test_images_dir):
        """Test that face bounding box coordinates are included"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "two-faces.jpg")
        results = identify_all_faces(image_path)

        for result in results:
            assert "face_bbox" in result
            bbox = result["face_bbox"]
            assert len(bbox) == 4
            assert all(isinstance(coord, int) for coord in bbox)

    def test_identify_all_faces_status_field_values(self, test_images_dir):
        """Test that status field has valid values"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "two-faces.jpg")
        results = identify_all_faces(image_path)

        valid_statuses = ["identified", "suggestion", "unknown", "error"]
        for result in results:
            assert result["status"] in valid_statuses

    def test_identify_all_faces_face_id_unique(self, test_images_dir):
        """Test that each face gets unique face_id"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "twelve-faces.png")
        results = identify_all_faces(image_path)

        face_ids = [r["face_id"] for r in results]
        assert len(face_ids) == len(set(face_ids))  # All unique
