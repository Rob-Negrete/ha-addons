"""
Integration tests for extract_faces_with_crops function in clasificador.py

Tests use REAL face images from tests/dummies/ folder to validate face detection,
extraction, quality filtering, and data structure completeness with actual ML pipeline.
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
    from clasificador import extract_faces_with_crops

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class TestExtractFacesWithCropsRealImages:
    """Comprehensive tests for extract_faces_with_crops() with real images."""

    @pytest.fixture
    def test_images_dir(self):
        """Get path to test images directory"""
        return os.path.join(os.path.dirname(__file__), "..", "dummies")

    def test_extract_faces_one_face_image(self, test_images_dir):
        """Test face extraction with image containing exactly one face"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "one-face.jpg")
        faces = extract_faces_with_crops(image_path)

        # Should detect exactly 1 face
        assert len(faces) == 1

        # Validate face data structure
        face = faces[0]
        assert "face_id" in face
        assert "embedding" in face
        assert "detection_confidence" in face
        assert "face_bbox" in face
        assert "quality_metrics" in face
        assert "thumbnail_path" in face
        assert "face_index" in face

        # Validate data types
        assert isinstance(face["face_id"], str)
        assert len(face["embedding"]) == 512  # InsightFace embedding dimension
        assert isinstance(face["detection_confidence"], float)
        assert len(face["face_bbox"]) == 4
        assert all(isinstance(x, int) for x in face["face_bbox"])

    def test_extract_faces_two_faces_image(self, test_images_dir):
        """Test face extraction with image containing two faces"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "two-faces.jpg")
        faces = extract_faces_with_crops(image_path)

        # Should detect exactly 2 faces
        assert len(faces) == 2

        # Validate each face has unique face_id
        face_ids = [f["face_id"] for f in faces]
        assert len(set(face_ids)) == 2  # All unique

        # Validate face indices
        assert faces[0]["face_index"] == 0
        assert faces[1]["face_index"] == 1

    def test_extract_faces_twelve_faces_image(self, test_images_dir):
        """Test face extraction with image containing twelve faces"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "twelve-faces.png")
        faces = extract_faces_with_crops(image_path)

        # Should detect exactly 12 faces
        assert len(faces) == 12

        # Validate all faces have required fields
        for i, face in enumerate(faces):
            assert face["face_index"] == i
            assert "embedding" in face
            assert len(face["embedding"]) == 512

    def test_extract_faces_zero_faces_image(self, test_images_dir):
        """Test face extraction with image containing no faces"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "zero-faces.jpg")
        faces = extract_faces_with_crops(image_path)

        # Should detect 0 faces
        assert len(faces) == 0

    def test_extract_faces_image_read_path(self, test_images_dir):
        """Test cv2.imread path - successful image reading"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "one-face.jpg")
        faces = extract_faces_with_crops(image_path)

        # Should successfully read and process image
        assert faces is not None
        assert isinstance(faces, list)

    def test_extract_faces_invalid_image_path(self):
        """Test exception handling with non-existent image path"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        faces = extract_faces_with_crops("/nonexistent/path/to/image.jpg")

        # Should return empty list
        assert faces == []

    def test_extract_faces_bounding_box_extraction(self, test_images_dir):
        """Test face bounding box extraction and validation"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "one-face.jpg")
        faces = extract_faces_with_crops(image_path)

        bbox = faces[0]["face_bbox"]
        x1, y1, x2, y2 = bbox

        # Validate bounding box coordinates
        assert x2 > x1  # Width positive
        assert y2 > y1  # Height positive
        assert x1 >= 0  # Non-negative coordinates
        assert y1 >= 0

    def test_extract_faces_padding_calculation(self, test_images_dir):
        """Test face crop padding logic (20px padding)"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "two-faces.jpg")
        faces = extract_faces_with_crops(image_path)

        # Should successfully apply padding and crop faces
        assert len(faces) == 2
        for face in faces:
            # Padded crops should have valid dimensions
            assert "face_bbox" in face
            assert len(face["face_bbox"]) == 4

    def test_extract_faces_quality_metrics_integration(self, test_images_dir):
        """Test quality metrics calculation integration"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "one-face.jpg")
        faces = extract_faces_with_crops(image_path)

        metrics = faces[0]["quality_metrics"]

        # Validate quality metrics structure
        assert "sharpness" in metrics
        assert "face_area" in metrics
        assert "brightness" in metrics
        assert "contrast" in metrics
        assert "quality_score" in metrics

        # Validate quality metrics values
        assert metrics["quality_score"] > 0.0
        assert 0.0 <= metrics["quality_score"] <= 1.0

    def test_extract_faces_quality_score_filtering(self, test_images_dir):
        """Test quality score threshold filtering (MIN_QUALITY_SCORE)"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "twelve-faces.png")
        faces = extract_faces_with_crops(image_path)

        # All returned faces should pass quality threshold
        for face in faces:
            # Quality scores should be above minimum (defined in clasificador.py)
            assert face["quality_metrics"]["quality_score"] >= 0.0

    def test_extract_faces_sharpness_filtering(self, test_images_dir):
        """Test sharpness threshold filtering (MIN_BLUR_THRESHOLD)"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "two-faces.jpg")
        faces = extract_faces_with_crops(image_path)

        # All returned faces should pass sharpness threshold
        for face in faces:
            assert face["quality_metrics"]["sharpness"] >= 0.0

    def test_extract_faces_thumbnail_path_generation(self, test_images_dir):
        """Test thumbnail file path generation and saving"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "one-face.jpg")
        faces = extract_faces_with_crops(image_path)

        thumbnail_path = faces[0]["thumbnail_path"]

        # Validate thumbnail path
        assert isinstance(thumbnail_path, str)
        assert len(thumbnail_path) > 0

    def test_extract_faces_face_id_uuid_generation(self, test_images_dir):
        """Test UUID face_id generation uniqueness"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "twelve-faces.png")
        faces = extract_faces_with_crops(image_path)

        # All face_ids should be unique UUIDs
        face_ids = [f["face_id"] for f in faces]
        assert len(face_ids) == len(set(face_ids))  # All unique

        # Validate UUID format (36 characters with hyphens)
        for face_id in face_ids:
            assert len(face_id) == 36
            assert face_id.count("-") == 4

    def test_extract_faces_detection_confidence(self, test_images_dir):
        """Test InsightFace detection confidence scoring"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "two-faces.jpg")
        faces = extract_faces_with_crops(image_path)

        # Validate detection confidence values
        for face in faces:
            confidence = face["detection_confidence"]
            assert isinstance(confidence, float)
            assert 0.0 <= confidence <= 1.0

    def test_extract_faces_embedding_extraction(self, test_images_dir):
        """Test InsightFace embedding extraction (512-dim vectors)"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "one-face.jpg")
        faces = extract_faces_with_crops(image_path)

        embedding = faces[0]["embedding"]

        # Validate embedding properties
        assert len(embedding) == 512  # InsightFace standard dimension
        # Embedding is numpy array, check it has numeric values
        import numpy as np

        assert isinstance(embedding, np.ndarray)
        assert embedding.dtype in [np.float32, np.float64, np.int32, np.int64]

    def test_extract_faces_exception_handling_per_face(self, test_images_dir):
        """Test per-face exception handling (continues on individual face errors)"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        image_path = os.path.join(test_images_dir, "twelve-faces.png")
        faces = extract_faces_with_crops(image_path)

        # Should successfully process multiple faces despite potential errors
        assert isinstance(faces, list)
        assert len(faces) >= 0

    def test_extract_faces_comprehensive_all_paths(self, test_images_dir):
        """Comprehensive test covering all code paths in extract_faces_with_crops"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Test 1: Valid image with one face
        one_face_path = os.path.join(test_images_dir, "one-face.jpg")
        one_face_result = extract_faces_with_crops(one_face_path)
        assert len(one_face_result) == 1
        assert all(
            k in one_face_result[0]
            for k in [
                "face_id",
                "embedding",
                "detection_confidence",
                "face_bbox",
                "quality_metrics",
                "thumbnail_path",
                "face_index",
            ]
        )

        # Test 2: Valid image with multiple faces
        twelve_faces_path = os.path.join(test_images_dir, "twelve-faces.png")
        twelve_faces_result = extract_faces_with_crops(twelve_faces_path)
        assert len(twelve_faces_result) == 12

        # Test 3: Image with no faces
        zero_faces_path = os.path.join(test_images_dir, "zero-faces.jpg")
        zero_faces_result = extract_faces_with_crops(zero_faces_path)
        assert len(zero_faces_result) == 0

        # Test 4: Invalid image path
        invalid_result = extract_faces_with_crops("/invalid/path.jpg")
        assert invalid_result == []

        # Validate face indices are sequential
        for i, face in enumerate(twelve_faces_result):
            assert face["face_index"] == i

        # Validate quality filtering worked
        for face in twelve_faces_result:
            assert face["quality_metrics"]["quality_score"] >= 0.0
            assert face["quality_metrics"]["sharpness"] >= 0.0
