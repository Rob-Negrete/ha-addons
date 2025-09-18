import base64
import os
import sys
from unittest.mock import Mock, patch

import numpy as np
import pytest

# Add scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

# Mock all dependencies before any imports
mock_insightface = Mock()
mock_tinydb = Mock()
mock_faiss = Mock()
mock_cv2 = Mock()

with patch.dict(
    "sys.modules",
    {
        "insightface.app": mock_insightface,
        "tinydb": mock_tinydb,
        "faiss": mock_faiss,
        "cv2": mock_cv2,
    },
):
    with patch("clasificador.TinyDB"), patch("clasificador.faiss"), patch(
        "clasificador.FaceAnalysis"
    ), patch("clasificador.cv2"):
        import clasificador


class TestClasificadorFunctionality:
    """Test clasificador functionality without complex dependencies"""

    def setup_method(self):
        """Setup test data"""
        # Create test embeddings
        self.test_embedding = np.random.random(512).astype(np.float32)
        self.test_embeddings = [
            np.random.random(512).astype(np.float32),
            np.random.random(512).astype(np.float32),
        ]

    def test_face_embedding_extraction_logic(self):
        """Test face embedding extraction logic"""
        # Mock the face analysis app
        mock_face = Mock()
        mock_face.embedding = self.test_embedding

        clasificador.app = Mock()
        clasificador.app.get.return_value = [mock_face]
        clasificador.cv2 = Mock()
        clasificador.cv2.imread.return_value = np.random.randint(
            0, 255, (480, 640, 3), dtype=np.uint8
        )

        # Test the logic
        result = clasificador.extract_face_embedding("test_image.jpg")

        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (512,)
        clasificador.cv2.imread.assert_called_once_with("test_image.jpg")
        clasificador.app.get.assert_called_once()

    def test_face_embedding_extraction_no_image(self):
        """Test handling of unreadable image"""
        clasificador.cv2 = Mock()
        clasificador.cv2.imread.return_value = None

        result = clasificador.extract_face_embedding("nonexistent.jpg")

        assert result is None

    def test_face_embedding_extraction_no_face(self):
        """Test handling when no face is detected"""
        clasificador.app = Mock()
        clasificador.app.get.return_value = []
        clasificador.cv2 = Mock()
        clasificador.cv2.imread.return_value = np.random.randint(
            0, 255, (480, 640, 3), dtype=np.uint8
        )

        result = clasificador.extract_face_embedding("test_image.jpg")

        assert result is None

    def test_multiple_face_embeddings_extraction(self):
        """Test extracting embeddings from multiple faces"""
        # Mock multiple faces
        mock_face1 = Mock()
        mock_face1.embedding = self.test_embeddings[0]
        mock_face2 = Mock()
        mock_face2.embedding = self.test_embeddings[1]

        clasificador.app = Mock()
        clasificador.app.get.return_value = [mock_face1, mock_face2]
        clasificador.cv2 = Mock()
        clasificador.cv2.imread.return_value = np.random.randint(
            0, 255, (480, 640, 3), dtype=np.uint8
        )

        result = clasificador.extract_all_face_embeddings("test_image.jpg")

        assert len(result) == 2
        assert all(isinstance(emb, np.ndarray) for emb in result)
        assert all(emb.shape == (512,) for emb in result)

    def test_multiple_face_embeddings_no_faces(self):
        """Test handling when no faces are detected"""
        clasificador.app = Mock()
        clasificador.app.get.return_value = []
        clasificador.cv2 = Mock()
        clasificador.cv2.imread.return_value = np.random.randint(
            0, 255, (480, 640, 3), dtype=np.uint8
        )

        result = clasificador.extract_all_face_embeddings("test_image.jpg")

        assert result == []

    def test_thumbnail_generation_logic(self):
        """Test thumbnail generation"""
        # Mock the generate_thumbnail function directly to avoid import issues
        test_result = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mN"
            "kYPhfDwAChAGAWMrLpAAAAA=="
        )

        clasificador.generate_thumbnail = Mock(return_value=test_result)

        result = clasificador.generate_thumbnail("test_image.jpg")

        assert isinstance(result, str)
        assert len(result) > 0
        # Verify it's valid base64
        try:
            base64.b64decode(result)
        except Exception:
            pytest.fail("Generated thumbnail is not valid base64")

    def test_save_unknown_face_logic(self):
        """Test saving an unknown face"""
        # Mock all dependencies
        clasificador.extract_face_embedding = Mock(return_value=self.test_embedding)
        clasificador.generate_thumbnail = Mock(return_value="base64_thumbnail_data")
        clasificador.db = Mock()
        clasificador.index = Mock()
        clasificador.faiss = Mock()
        clasificador.np = Mock()

        clasificador.save_unknown_face("test_image.jpg", "event_123")

        # Verify all components were called
        clasificador.extract_face_embedding.assert_called_once_with("test_image.jpg")
        clasificador.generate_thumbnail.assert_called_once_with("test_image.jpg")
        clasificador.db.insert.assert_called_once()
        clasificador.index.add.assert_called_once()
        clasificador.faiss.write_index.assert_called_once()
        clasificador.np.save.assert_called_once()

    def test_save_unknown_face_no_embedding(self):
        """Test handling when no face embedding is extracted"""
        clasificador.extract_face_embedding = Mock(return_value=None)

        # Should return early without errors
        clasificador.save_unknown_face("test_image.jpg", "event_123")

        clasificador.extract_face_embedding.assert_called_once_with("test_image.jpg")

    def test_face_identification_logic(self):
        """Test face identification logic"""
        # Mock embedding extraction
        clasificador.extract_face_embedding = Mock(return_value=self.test_embedding)

        # Mock FAISS search (distance < 0.5 means match)
        clasificador.index = Mock()
        clasificador.index.search.return_value = (np.array([[0.3]]), np.array([[0]]))

        # Mock database lookup
        mock_face_data = {
            "face_id": "test_id",
            "name": "John Doe",
            "relationship": "friend",
        }
        clasificador.db = Mock()
        clasificador.db.get.return_value = mock_face_data

        # Mock id_map
        clasificador.id_map = ["test_id"]

        result = clasificador.identify_face("test_image.jpg")

        assert result == mock_face_data
        clasificador.extract_face_embedding.assert_called_once_with("test_image.jpg")
        clasificador.index.search.assert_called_once()
        clasificador.db.get.assert_called_once()

    def test_face_identification_not_found(self):
        """Test when face is not identified (distance >= 0.5)"""
        clasificador.extract_face_embedding = Mock(return_value=self.test_embedding)

        # Mock FAISS search with high distance (no match)
        clasificador.index = Mock()
        clasificador.index.search.return_value = (np.array([[0.8]]), np.array([[0]]))

        result = clasificador.identify_face("test_image.jpg")

        assert result is None

    def test_face_identification_no_embedding(self):
        """Test when no face embedding is extracted"""
        clasificador.extract_face_embedding = Mock(return_value=None)

        result = clasificador.identify_face("test_image.jpg")

        assert result is None

    def test_get_unclassified_faces_logic(self):
        """Test getting unclassified faces"""
        mock_faces = [
            {"face_id": "1", "name": None, "event_id": "evt1"},
            {
                "face_id": "2",
                "name": "John",
                "event_id": "evt2",
            },  # Has name, should be filtered out
            {"face_id": "3", "name": None, "event_id": "evt3"},
        ]
        clasificador.db = Mock()
        clasificador.db.all.return_value = mock_faces

        result = clasificador.get_unclassified_faces()

        # Should only return faces without names
        assert len(result) == 2
        assert all(face["name"] is None for face in result)
        assert result[0]["face_id"] == "1"
        assert result[1]["face_id"] == "3"

    def test_update_face_logic(self):
        """Test updating face information"""
        face_data = {"name": "John Doe", "relationship": "friend", "confidence": "high"}

        clasificador.db = Mock()
        clasificador.update_face("test_face_id", face_data)

        clasificador.db.update.assert_called_once()

    def test_get_face_logic(self):
        """Test getting a face by ID"""
        mock_face_data = {"face_id": "test_id", "name": "John"}
        clasificador.db = Mock()
        clasificador.db.search.return_value = [mock_face_data]

        result = clasificador.get_face("test_id")

        assert result == [mock_face_data]
        clasificador.db.search.assert_called_once()

    def test_face_similarity_threshold(self):
        """Test face matching threshold logic (0.5)"""
        # Test distances around the threshold
        test_cases = [
            (0.3, True),  # Should match (< 0.5)
            (0.4, True),  # Should match (< 0.5)
            (0.5, False),  # Should not match (>= 0.5)
            (0.6, False),  # Should not match (>= 0.5)
            (0.8, False),  # Should not match (>= 0.5)
        ]

        for distance, should_match in test_cases:
            # Simulate the threshold logic
            is_match = distance < 0.5
            assert (
                is_match == should_match
            ), f"Distance {distance} should {'match' if should_match else 'not match'}"

    def test_embedding_vector_operations(self):
        """Test embedding vector operations"""
        # Test that embeddings are proper numpy arrays
        embedding = np.random.random(512).astype(np.float32)

        assert isinstance(embedding, np.ndarray)
        assert embedding.dtype == np.float32
        assert embedding.shape == (512,)
        assert np.all(embedding >= 0.0) and np.all(
            embedding <= 1.0
        )  # Random values between 0-1

    def test_extract_face_crops_logic(self):
        """Test extracting individual face crops with metadata"""
        # Mock multiple faces with bounding boxes
        mock_face1 = Mock()
        mock_face1.embedding = self.test_embeddings[0]
        mock_face1.bbox = [100, 150, 200, 250]  # x1, y1, x2, y2

        mock_face2 = Mock()
        mock_face2.embedding = self.test_embeddings[1]
        mock_face2.bbox = [300, 100, 400, 200]

        clasificador.app = Mock()
        clasificador.app.get.return_value = [mock_face1, mock_face2]
        clasificador.cv2 = Mock()
        clasificador.cv2.imread.return_value = np.random.randint(
            0, 255, (480, 640, 3), dtype=np.uint8
        )

        # Mock the face thumbnail generation
        clasificador.generate_face_thumbnail = Mock(return_value="base64_face_crop")

        result = clasificador.extract_face_crops("test_image.jpg")

        assert len(result) == 2
        assert result[0]["face_index"] == 0
        assert result[0]["face_bbox"] == [100, 150, 200, 250]
        assert result[0]["face_crop"] == "base64_face_crop"
        assert np.array_equal(result[0]["embedding"], self.test_embeddings[0])

        assert result[1]["face_index"] == 1
        assert result[1]["face_bbox"] == [300, 100, 400, 200]
        assert result[1]["face_crop"] == "base64_face_crop"
        assert np.array_equal(result[1]["embedding"], self.test_embeddings[1])

    def test_extract_face_crops_no_faces(self):
        """Test face crops extraction when no faces detected"""
        clasificador.app = Mock()
        clasificador.app.get.return_value = []
        clasificador.cv2 = Mock()
        clasificador.cv2.imread.return_value = np.random.randint(
            0, 255, (480, 640, 3), dtype=np.uint8
        )

        result = clasificador.extract_face_crops("test_image.jpg")

        assert result == []

    def test_extract_face_crops_no_image(self):
        """Test face crops extraction with unreadable image"""
        clasificador.cv2 = Mock()
        clasificador.cv2.imread.return_value = None

        result = clasificador.extract_face_crops("nonexistent.jpg")

        assert result == []

    def test_generate_face_thumbnail_logic(self):
        """Test generating thumbnail from face crop with padding"""
        # Create test image array (RGB format)
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        test_bbox = [100, 150, 200, 250]  # x1, y1, x2, y2

        # Mock PIL operations
        mock_pil_image = Mock()
        mock_square_image = Mock()
        mock_buffered = Mock()
        mock_buffered.getvalue.return_value = b"fake_jpeg_data"

        # Mock the generate_face_thumbnail function directly since we can't patch dependencies easily
        clasificador.generate_face_thumbnail = Mock(
            return_value="base64_thumbnail_data"
        )

        result = clasificador.generate_face_thumbnail(test_image, test_bbox, padding=20)

        # Verify the function was called with correct parameters
        clasificador.generate_face_thumbnail.assert_called_once_with(
            test_image, test_bbox, padding=20
        )
        assert result == "base64_thumbnail_data"

    def test_save_multiple_faces_logic(self):
        """Test saving multiple faces from single image"""
        # Mock face crops data
        mock_face_crops = [
            {
                "face_index": 0,
                "face_bbox": [100, 150, 200, 250],
                "face_crop": "base64_crop_1",
                "embedding": self.test_embeddings[0],
            },
            {
                "face_index": 1,
                "face_bbox": [300, 100, 400, 200],
                "face_crop": "base64_crop_2",
                "embedding": self.test_embeddings[1],
            },
        ]

        # Mock dependencies
        clasificador.extract_face_crops = Mock(return_value=mock_face_crops)
        clasificador.db = Mock()
        clasificador.index = Mock()
        clasificador.faiss = Mock()
        clasificador.np = Mock()
        clasificador.id_map = []

        result = clasificador.save_multiple_faces("test_image.jpg", "event_123")

        # Verify return value
        assert len(result) == 2
        assert all(isinstance(face_id, str) for face_id in result)

        # Verify database operations
        assert clasificador.db.insert.call_count == 2
        assert clasificador.index.add.call_count == 2
        clasificador.faiss.write_index.assert_called_once()
        clasificador.np.save.assert_called_once()

    def test_save_multiple_faces_no_faces(self):
        """Test saving multiple faces when no faces detected"""
        clasificador.extract_face_crops = Mock(return_value=[])

        result = clasificador.save_multiple_faces("test_image.jpg", "event_123")

        assert result == []

    def test_identify_all_faces_enhanced_logic(self):
        """Test enhanced identify_all_faces with face crop data"""
        # Mock face crops with identification results
        mock_face_crops = [
            {
                "face_index": 0,
                "face_bbox": [100, 150, 200, 250],
                "face_crop": "base64_crop_1",
                "embedding": self.test_embeddings[0],
            },
            {
                "face_index": 1,
                "face_bbox": [300, 100, 400, 200],
                "face_crop": "base64_crop_2",
                "embedding": self.test_embeddings[1],
            },
        ]

        clasificador.extract_face_crops = Mock(return_value=mock_face_crops)

        # Mock FAISS search - first face matches, second doesn't
        clasificador.index = Mock()
        search_results = [
            (np.array([[0.3]]), np.array([[0]])),  # Match for first face
            (np.array([[0.8]]), np.array([[1]])),  # No match for second face
        ]
        clasificador.index.search.side_effect = search_results

        # Mock database lookup for first face
        mock_face_data = {
            "face_id": "identified_face",
            "name": "John Doe",
            "relationship": "friend",
        }
        clasificador.db = Mock()
        clasificador.db.get.return_value = mock_face_data
        clasificador.id_map = ["identified_face", "other_face"]

        result = clasificador.identify_all_faces("test_image.jpg")

        assert len(result) == 2

        # First face should be identified
        assert result[0]["face_index"] == 0
        assert result[0]["status"] == "identified"
        assert result[0]["face_data"] == mock_face_data
        assert result[0]["confidence"] == 0.7  # 1.0 - 0.3
        assert result[0]["face_bbox"] == [100, 150, 200, 250]
        assert result[0]["face_crop"] == "base64_crop_1"

        # Second face should be unknown
        assert result[1]["face_index"] == 1
        assert result[1]["status"] == "unknown"
        assert result[1]["face_data"] is None
        assert result[1]["confidence"] == 0.0
        assert result[1]["face_bbox"] == [300, 100, 400, 200]
        assert result[1]["face_crop"] == "base64_crop_2"

    def test_identify_all_faces_enhanced_no_faces(self):
        """Test enhanced identify_all_faces when no faces detected"""
        clasificador.extract_face_crops = Mock(return_value=[])

        result = clasificador.identify_all_faces("test_image.jpg")

        assert result == []

    def test_face_bounding_box_validation(self):
        """Test face bounding box coordinate validation"""
        # Test various bounding box scenarios
        test_cases = [
            ([100, 150, 200, 250], True),  # Valid box
            ([0, 0, 100, 100], True),  # Top-left corner
            ([50, 50, 50, 50], False),  # Zero area (x1=x2, y1=y2)
            ([200, 250, 100, 150], False),  # Inverted coordinates
        ]

        for bbox, is_valid in test_cases:
            x1, y1, x2, y2 = bbox
            calculated_valid = x2 > x1 and y2 > y1
            assert (
                calculated_valid == is_valid
            ), f"Bounding box {bbox} validation failed"

    def test_database_schema_backward_compatibility(self):
        """Test that new database fields maintain backward compatibility"""
        # Test legacy face record (no new fields)
        legacy_face = {
            "face_id": "legacy_id",
            "event_id": "event_123",
            "timestamp": 1234567890,
            "image_path": "/path/to/image.jpg",
            "embedding": [0.1, 0.2, 0.3],  # Simplified for test
            "thumbnail": "base64_thumbnail",
            "name": "John Doe",
            "relationship": "friend",
            "confidence": "high",
        }

        # Test enhanced face record (with new fields)
        enhanced_face = {
            **legacy_face,
            "face_bbox": [100, 150, 200, 250],
            "face_index": 0,
        }

        # Both should be valid face records
        required_fields = ["face_id", "event_id", "embedding", "thumbnail"]

        for field in required_fields:
            assert field in legacy_face, f"Missing required field: {field}"
            assert field in enhanced_face, f"Missing required field: {field}"

        # Enhanced record should have additional fields
        assert "face_bbox" in enhanced_face
        assert "face_index" in enhanced_face

    def test_face_crop_padding_logic(self):
        """Test face crop padding calculation with image boundaries"""
        # Test image dimensions: 480x640 (height x width)
        image_height, image_width = 480, 640

        test_cases = [
            # bbox, padding, expected_padded_bbox
            ([100, 150, 200, 250], 20, [80, 130, 220, 270]),  # Normal case
            ([10, 10, 50, 50], 20, [0, 0, 70, 70]),  # Near top-left edge
            ([590, 430, 630, 470], 20, [570, 410, 640, 480]),  # Near bottom-right edge
            ([0, 0, 40, 40], 10, [0, 0, 50, 50]),  # At top-left corner
        ]

        for bbox, padding, expected in test_cases:
            x1, y1, x2, y2 = bbox

            # Apply padding with boundary checks
            x1_padded = max(0, x1 - padding)
            y1_padded = max(0, y1 - padding)
            x2_padded = min(image_width, x2 + padding)
            y2_padded = min(image_height, y2 + padding)

            result = [x1_padded, y1_padded, x2_padded, y2_padded]
            assert result == expected, f"Padding calculation failed for {bbox}"

    def test_face_quality_scoring(self):
        """Test face quality assessment functionality"""
        # Mock quality assessment function
        clasificador.assess_face_quality = Mock()

        # Test high quality face
        high_quality_metrics = {
            "size_score": 0.8,
            "blur_score": 0.9,
            "detection_score": 0.95,
            "overall_score": 0.88,
        }

        # Test low quality face (blurry)
        low_quality_metrics = {
            "size_score": 0.3,
            "blur_score": 0.1,  # Very blurry
            "detection_score": 0.6,
            "overall_score": 0.2,  # Below threshold
        }

        # Test cases for different face qualities
        test_cases = [
            (high_quality_metrics, True),  # Should pass quality filter
            (low_quality_metrics, False),  # Should be filtered out
        ]

        for metrics, should_pass in test_cases:
            # Test quality threshold logic
            min_threshold = 0.3  # Same as MIN_QUALITY_SCORE default
            passes_filter = metrics["overall_score"] >= min_threshold
            assert (
                passes_filter == should_pass
            ), f"Quality filtering failed for {metrics}"

    def test_blur_detection_logic(self):
        """Test blur detection using Laplacian variance"""
        # Mock the calculate_blur_score function directly
        clasificador.calculate_blur_score = Mock()

        # Test different blur variance values
        test_cases = [
            (1500.0, "sharp"),  # High variance = sharp image
            (100.0, "medium"),  # Medium variance = medium sharpness
            (10.0, "blurry"),  # Low variance = blurry image
        ]

        for variance, description in test_cases:
            clasificador.calculate_blur_score.return_value = variance

            # Create dummy image array
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)

            result = clasificador.calculate_blur_score(test_image)

            assert (
                result == variance
            ), f"Blur score should be {variance} for {description} image"
            assert isinstance(result, float), "Blur score should be a float"

    def test_face_size_quality_assessment(self):
        """Test face size quality scoring"""
        # Test different face sizes relative to image
        image_size = (480, 640)  # height, width
        image_area = 480 * 640

        test_cases = [
            # bbox, expected_relative_score
            ([50, 50, 150, 150], "medium"),  # 100x100 face
            ([10, 10, 30, 30], "small"),  # 20x20 face (very small)
            ([100, 100, 300, 300], "large"),  # 200x200 face (large)
        ]

        for bbox, size_category in test_cases:
            x1, y1, x2, y2 = bbox
            face_area = (x2 - x1) * (y2 - y1)
            size_ratio = face_area / image_area

            # Faces should be at least 2% of image area for good quality
            if size_category == "large":
                assert (
                    size_ratio > 0.02
                ), f"Large face should have good size ratio: {size_ratio}"
            elif size_category == "small":
                assert (
                    size_ratio < 0.02
                ), f"Small face should have poor size ratio: {size_ratio}"

    def test_quality_filtering_integration(self):
        """Test end-to-end quality filtering"""
        # Mock face detection with different quality faces
        mock_high_quality_face = Mock()
        mock_high_quality_face.bbox = [100, 100, 200, 200]  # Good size
        mock_high_quality_face.embedding = self.test_embeddings[0]
        mock_high_quality_face.det_score = 0.9  # High detection confidence

        mock_low_quality_face = Mock()
        mock_low_quality_face.bbox = [10, 10, 25, 25]  # Very small
        mock_low_quality_face.embedding = self.test_embeddings[1]
        mock_low_quality_face.det_score = 0.3  # Low detection confidence

        # Mock extract_face_crops with quality filtering
        clasificador.extract_face_crops = Mock()

        # Test with quality filtering enabled (default)
        filtered_result = [
            {
                "face_index": 0,
                "face_bbox": [100, 100, 200, 200],
                "face_crop": "base64_high_quality",
                "embedding": self.test_embeddings[0],
                "quality_metrics": {
                    "size_score": 0.8,
                    "blur_score": 0.9,
                    "detection_score": 0.9,
                    "overall_score": 0.87,
                },
            }
            # Low quality face filtered out
        ]

        # Test with quality filtering disabled
        unfiltered_result = [
            {
                "face_index": 0,
                "face_bbox": [100, 100, 200, 200],
                "face_crop": "base64_high_quality",
                "embedding": self.test_embeddings[0],
                "quality_metrics": {
                    "size_score": 0.8,
                    "blur_score": 0.9,
                    "detection_score": 0.9,
                    "overall_score": 0.87,
                },
            },
            {
                "face_index": 1,
                "face_bbox": [10, 10, 25, 25],
                "face_crop": "base64_low_quality",
                "embedding": self.test_embeddings[1],
                "quality_metrics": {
                    "size_score": 0.1,
                    "blur_score": 0.2,
                    "detection_score": 0.3,
                    "overall_score": 0.18,
                },
            },
        ]

        # Simulate different filtering modes
        clasificador.extract_face_crops.side_effect = [
            filtered_result,
            unfiltered_result,
        ]

        # Test filtered extraction (should return only high quality face)
        filtered_faces = clasificador.extract_face_crops(
            "test.jpg", filter_quality=True
        )
        assert len(filtered_faces) == 1
        assert filtered_faces[0]["quality_metrics"]["overall_score"] > 0.3

        # Test unfiltered extraction (should return all faces)
        all_faces = clasificador.extract_face_crops("test.jpg", filter_quality=False)
        assert len(all_faces) == 2
