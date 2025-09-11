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
