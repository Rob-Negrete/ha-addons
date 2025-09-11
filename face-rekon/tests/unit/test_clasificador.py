import base64
import os
import sys
from unittest.mock import Mock, patch

import numpy as np
import pytest
from PIL import Image

# Add scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

# Mock the dependencies before importing
mock_insightface = Mock()
mock_tinydb = Mock()
mock_faiss = Mock()

with patch.dict(
    "sys.modules",
    {"insightface.app": mock_insightface, "tinydb": mock_tinydb, "faiss": mock_faiss},
):
    with patch("clasificador.TinyDB"), patch("clasificador.faiss"), patch(
        "clasificador.FaceAnalysis"
    ):
        import clasificador


class TestExtractFaceEmbedding:
    @patch("clasificador.cv2.imread")
    @patch("clasificador.app.get")
    def test_extract_face_embedding_success(self, mock_app_get, mock_imread):
        """Test successful face embedding extraction"""
        # Mock image reading
        mock_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_imread.return_value = mock_img

        # Mock face detection
        mock_face = Mock()
        mock_face.embedding = np.random.random(512).astype(np.float32)
        mock_app_get.return_value = [mock_face]

        result = clasificador.extract_face_embedding("test_image.jpg")

        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (512,)
        mock_imread.assert_called_once_with("test_image.jpg")
        mock_app_get.assert_called_once()

    @patch("clasificador.cv2.imread")
    def test_extract_face_embedding_no_image(self, mock_imread):
        """Test handling of unreadable image"""
        mock_imread.return_value = None

        result = clasificador.extract_face_embedding("nonexistent.jpg")

        assert result is None

    @patch("clasificador.cv2.imread")
    @patch("clasificador.app.get")
    def test_extract_face_embedding_no_face(self, mock_app_get, mock_imread):
        """Test handling when no face is detected"""
        mock_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_imread.return_value = mock_img
        mock_app_get.return_value = []

        result = clasificador.extract_face_embedding("test_image.jpg")

        assert result is None


class TestExtractAllFaceEmbeddings:
    @patch("clasificador.cv2.imread")
    @patch("clasificador.app.get")
    def test_extract_all_face_embeddings_multiple_faces(
        self, mock_app_get, mock_imread
    ):
        """Test extracting embeddings from multiple faces"""
        mock_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_imread.return_value = mock_img

        # Mock multiple faces
        mock_face1 = Mock()
        mock_face1.embedding = np.random.random(512).astype(np.float32)
        mock_face2 = Mock()
        mock_face2.embedding = np.random.random(512).astype(np.float32)
        mock_app_get.return_value = [mock_face1, mock_face2]

        result = clasificador.extract_all_face_embeddings("test_image.jpg")

        assert len(result) == 2
        assert all(isinstance(emb, np.ndarray) for emb in result)
        assert all(emb.shape == (512,) for emb in result)

    @patch("clasificador.cv2.imread")
    @patch("clasificador.app.get")
    def test_extract_all_face_embeddings_no_faces(self, mock_app_get, mock_imread):
        """Test handling when no faces are detected"""
        mock_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_imread.return_value = mock_img
        mock_app_get.return_value = []

        result = clasificador.extract_all_face_embeddings("test_image.jpg")

        assert result == []


class TestGenerateThumbnail:
    def test_generate_thumbnail_success(self, temp_dirs):
        """Test thumbnail generation"""
        # Create a test image
        test_image = Image.new("RGB", (320, 240), color="red")
        image_path = os.path.join(temp_dirs["base"], "test_image.jpg")
        test_image.save(image_path)

        with patch("clasificador.Image.open", return_value=test_image):
            result = clasificador.generate_thumbnail(image_path)

        assert isinstance(result, str)
        assert len(result) > 0
        # Verify it's valid base64
        try:
            base64.b64decode(result)
        except Exception:
            pytest.fail("Generated thumbnail is not valid base64")


class TestSaveUnknownFace:
    @patch("clasificador.extract_face_embedding")
    @patch("clasificador.generate_thumbnail")
    @patch("clasificador.db.insert")
    @patch("clasificador.index.add")
    @patch("clasificador.faiss.write_index")
    @patch("clasificador.np.save")
    def test_save_unknown_face_success(
        self,
        mock_np_save,
        mock_write_index,
        mock_index_add,
        mock_db_insert,
        mock_generate_thumbnail,
        mock_extract_embedding,
    ):
        """Test saving an unknown face"""
        # Mock dependencies
        mock_embedding = np.random.random(512).astype(np.float32)
        mock_extract_embedding.return_value = mock_embedding
        mock_generate_thumbnail.return_value = "base64_thumbnail_data"

        clasificador.save_unknown_face("test_image.jpg", "event_123")

        # Verify all components were called
        mock_extract_embedding.assert_called_once_with("test_image.jpg")
        mock_generate_thumbnail.assert_called_once_with("test_image.jpg")
        mock_db_insert.assert_called_once()
        mock_index_add.assert_called_once()
        mock_write_index.assert_called_once()
        mock_np_save.assert_called_once()

    @patch("clasificador.extract_face_embedding")
    def test_save_unknown_face_no_embedding(self, mock_extract_embedding):
        """Test handling when no face embedding is extracted"""
        mock_extract_embedding.return_value = None

        # Should return early without errors
        clasificador.save_unknown_face("test_image.jpg", "event_123")

        mock_extract_embedding.assert_called_once_with("test_image.jpg")


class TestIdentifyFace:
    @patch("clasificador.extract_face_embedding")
    @patch("clasificador.index.search")
    @patch("clasificador.db.get")
    def test_identify_face_found(
        self, mock_db_get, mock_index_search, mock_extract_embedding
    ):
        """Test successful face identification"""
        # Mock embedding extraction
        mock_embedding = np.random.random(512).astype(np.float32)
        mock_extract_embedding.return_value = mock_embedding

        # Mock FAISS search (distance < 0.5 means match)
        mock_index_search.return_value = (np.array([[0.3]]), np.array([[0]]))

        # Mock database lookup
        mock_face_data = {
            "face_id": "test_id",
            "name": "John Doe",
            "relationship": "friend",
        }
        mock_db_get.return_value = mock_face_data

        # Mock id_map
        with patch("clasificador.id_map", ["test_id"]):
            result = clasificador.identify_face("test_image.jpg")

        assert result == mock_face_data
        mock_extract_embedding.assert_called_once_with("test_image.jpg")
        mock_index_search.assert_called_once()
        mock_db_get.assert_called_once()

    @patch("clasificador.extract_face_embedding")
    @patch("clasificador.index.search")
    def test_identify_face_not_found(self, mock_index_search, mock_extract_embedding):
        """Test when face is not identified (distance >= 0.5)"""
        mock_embedding = np.random.random(512).astype(np.float32)
        mock_extract_embedding.return_value = mock_embedding

        # Mock FAISS search with high distance (no match)
        mock_index_search.return_value = (np.array([[0.8]]), np.array([[0]]))

        result = clasificador.identify_face("test_image.jpg")

        assert result is None

    @patch("clasificador.extract_face_embedding")
    def test_identify_face_no_embedding(self, mock_extract_embedding):
        """Test when no face embedding is extracted"""
        mock_extract_embedding.return_value = None

        result = clasificador.identify_face("test_image.jpg")

        assert result is None


class TestGetUnclassifiedFaces:
    @patch("clasificador.db.all")
    def test_get_unclassified_faces(self, mock_db_all):
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
        mock_db_all.return_value = mock_faces

        result = clasificador.get_unclassified_faces()

        # Should only return faces without names
        assert len(result) == 2
        assert all(face["name"] is None for face in result)
        assert result[0]["face_id"] == "1"
        assert result[1]["face_id"] == "3"


class TestUpdateFace:
    @patch("clasificador.db.update")
    def test_update_face(self, mock_db_update):
        """Test updating face information"""
        face_data = {"name": "John Doe", "relationship": "friend", "confidence": "high"}

        clasificador.update_face("test_face_id", face_data)

        mock_db_update.assert_called_once()


class TestGetFace:
    @patch("clasificador.db.search")
    def test_get_face(self, mock_db_search):
        """Test getting a face by ID"""
        mock_face_data = {"face_id": "test_id", "name": "John"}
        mock_db_search.return_value = [mock_face_data]

        result = clasificador.get_face("test_id")

        assert result == [mock_face_data]
        mock_db_search.assert_called_once()
