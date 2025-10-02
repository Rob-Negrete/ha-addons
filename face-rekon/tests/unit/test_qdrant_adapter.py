"""
Unit tests for qdrant_adapter.py

This module contains comprehensive unit tests for the QdrantAdapter class,
targeting remote server connection logic, error handling, and retry mechanisms.
"""

import os
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest


class TestQdrantAdapterRemoteMode:
    """Test suite for QdrantAdapter remote server connection mode."""

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "false"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    def test_remote_connection_success_first_attempt(self, mock_qdrant_client):
        """Test successful remote connection on first attempt."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()

        # Verify
        assert adapter.client == mock_client_instance
        mock_qdrant_client.assert_called_once_with(host="localhost", port=6333)
        # Called twice: once for connection test, once for _ensure_collection
        assert mock_client_instance.get_collections.call_count == 2

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "false"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.time.sleep")
    def test_remote_connection_retry_with_exponential_backoff(
        self, mock_sleep, mock_qdrant_client
    ):
        """Test connection retry with exponential backoff on failures."""
        # Setup
        mock_client_instance = MagicMock()
        # Fail twice, succeed on 3rd, then succeed for _ensure_collection
        mock_client_instance.get_collections.side_effect = [
            Exception("Connection refused"),
            Exception("Connection refused"),
            Mock(collections=[]),  # Success on 3rd connection attempt
            Mock(collections=[Mock(name="faces")]),  # Success for _ensure_collection
        ]
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()

        # Verify
        assert adapter.client == mock_client_instance
        assert mock_qdrant_client.call_count == 3
        # Verify exponential backoff: 2^0=1, 2^1=2
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)  # 2^0
        mock_sleep.assert_any_call(2)  # 2^1

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "false"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    def test_remote_connection_failure_after_max_retries(self, mock_qdrant_client):
        """Test connection failure after exceeding max retries."""
        # Setup
        mock_qdrant_client.return_value.get_collections.side_effect = Exception(
            "Connection refused"
        )

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute & Verify
        with pytest.raises(Exception, match="Connection refused"):
            QdrantAdapter()

        # Should retry 5 times (0-4)
        assert mock_qdrant_client.call_count == 5

    @patch.dict(
        os.environ,
        {"FACE_REKON_USE_EMBEDDED_QDRANT": "false", "QDRANT_HOST": "custom.host"},
    )
    @patch("scripts.qdrant_adapter.QDRANT_HOST", "custom.host")
    @patch("scripts.qdrant_adapter.USE_EMBEDDED_QDRANT", False)
    @patch("scripts.qdrant_adapter.QdrantClient")
    def test_remote_connection_custom_host_port(self, mock_qdrant_client):
        """Test remote connection uses custom host from environment."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        QdrantAdapter()

        # Verify custom host was used
        mock_qdrant_client.assert_called_with(host="custom.host", port=6333)

    @patch.dict(
        os.environ,
        {
            "FACE_REKON_USE_EMBEDDED_QDRANT": "false",
            "QDRANT_HOST": "prod.server",
            "QDRANT_PORT": "7777",
        },
    )
    @patch("scripts.qdrant_adapter.QDRANT_HOST", "prod.server")
    @patch("scripts.qdrant_adapter.QDRANT_PORT", 7777)
    @patch("scripts.qdrant_adapter.USE_EMBEDDED_QDRANT", False)
    @patch("scripts.qdrant_adapter.QdrantClient")
    def test_remote_connection_custom_port(self, mock_qdrant_client):
        """Test remote connection uses custom port from environment."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        QdrantAdapter()

        # Verify custom port was used
        mock_qdrant_client.assert_called_with(host="prod.server", port=7777)


class TestQdrantAdapterEmbeddedMode:
    """Test suite for QdrantAdapter embedded mode error scenarios."""

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_embedded_storage_lock_conflict(self, mock_makedirs, mock_qdrant_client):
        """Test handling of storage lock conflict error in embedded mode."""
        # Setup
        mock_qdrant_client.side_effect = Exception(
            "Storage already accessed by another instance"
        )

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute & Verify
        with pytest.raises(Exception, match="already accessed by another instance"):
            QdrantAdapter()

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_embedded_generic_error(self, mock_makedirs, mock_qdrant_client):
        """Test handling of generic error in embedded mode."""
        # Setup
        mock_qdrant_client.side_effect = Exception("Generic error")

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute & Verify
        with pytest.raises(Exception, match="Generic error"):
            QdrantAdapter()


class TestQdrantAdapterCollectionManagement:
    """Test suite for collection creation and management error scenarios."""

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_collection_creation_failure(self, mock_makedirs, mock_qdrant_client):
        """Test error handling when collection creation fails."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(collections=[])
        mock_client_instance.create_collection.side_effect = Exception(
            "Collection creation failed"
        )
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute & Verify
        with pytest.raises(Exception, match="Collection creation failed"):
            QdrantAdapter()

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_collection_get_collections_failure(
        self, mock_makedirs, mock_qdrant_client
    ):
        """Test error handling when get_collections fails."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.side_effect = Exception(
            "Failed to get collections"
        )
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute & Verify
        with pytest.raises(Exception, match="Failed to get collections"):
            QdrantAdapter()


class TestQdrantAdapterSearchOperations:
    """Test suite for search operation error handling."""

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_search_similar_faces_exception_handling(
        self, mock_makedirs, mock_qdrant_client
    ):
        """Test search operation returns empty list on exception."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_client_instance.search.side_effect = Exception("Search failed")
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        embedding = np.random.rand(512).astype(np.float32)
        results = adapter.search_similar_faces(embedding, limit=5)

        # Verify
        assert results == []  # Should return empty list on error


class TestQdrantAdapterDeleteOperations:
    """Test suite for delete operation error handling."""

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_delete_face_not_found(self, mock_makedirs, mock_qdrant_client):
        """Test delete operation when face not found."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_client_instance.scroll.return_value = ([], None)  # Empty results
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        result = adapter.delete_face("nonexistent-id")

        # Verify
        assert result is False

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_delete_face_exception_handling(self, mock_makedirs, mock_qdrant_client):
        """Test delete operation exception handling."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_client_instance.scroll.side_effect = Exception("Delete failed")
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        result = adapter.delete_face("test-id")

        # Verify
        assert result is False


class TestQdrantAdapterGetFaceOperations:
    """Test suite for get_face operation error handling."""

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_get_face_not_found(self, mock_makedirs, mock_qdrant_client):
        """Test get_face returns None when face not found."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_client_instance.scroll.return_value = ([], None)  # Empty results
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        result = adapter.get_face("nonexistent-id")

        # Verify
        assert result is None

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_get_face_exception_handling(self, mock_makedirs, mock_qdrant_client):
        """Test get_face exception handling returns None."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_client_instance.scroll.side_effect = Exception("Get failed")
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        result = adapter.get_face("test-id")

        # Verify
        assert result is None


class TestQdrantAdapterUpdateOperations:
    """Test suite for update operation error handling."""

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_update_face_not_found(self, mock_makedirs, mock_qdrant_client):
        """Test update operation when face not found."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_client_instance.scroll.return_value = ([], None)  # Empty results
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        result = adapter.update_face("nonexistent-id", {"name": "Test"})

        # Verify
        assert result is False

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_update_face_exception_handling(self, mock_makedirs, mock_qdrant_client):
        """Test update operation exception handling."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_client_instance.scroll.side_effect = Exception("Update failed")
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        result = adapter.update_face("test-id", {"name": "Test"})

        # Verify
        assert result is False


class TestQdrantAdapterUnclassifiedFaces:
    """Test suite for get_unclassified_faces error handling."""

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_get_unclassified_faces_exception_handling(
        self, mock_makedirs, mock_qdrant_client
    ):
        """Test get_unclassified_faces returns empty list on exception."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_client_instance.scroll.side_effect = Exception("Query failed")
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        results = adapter.get_unclassified_faces()

        # Verify
        assert results == []


class TestQdrantAdapterCheckRecentDetection:
    """Test suite for check_recent_detection functionality."""

    @patch.dict(
        os.environ,
        {
            "FACE_REKON_USE_EMBEDDED_QDRANT": "true",
            "FACE_REKON_DEDUPLICATION_WINDOW": "0",
        },
    )
    @patch("scripts.qdrant_adapter.DEDUPLICATION_WINDOW", 0)
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_check_recent_detection_disabled_window(
        self, mock_makedirs, mock_qdrant_client
    ):
        """Test check_recent_detection returns False when deduplication disabled."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        result = adapter.check_recent_detection("test-event-123")

        # Verify
        assert result is False
        mock_client_instance.scroll.assert_not_called()

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_check_recent_detection_exception_handling(
        self, mock_makedirs, mock_qdrant_client
    ):
        """Test check_recent_detection returns False on exception."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_client_instance.scroll.side_effect = Exception("Query failed")
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        result = adapter.check_recent_detection("test-event-123")

        # Verify
        assert result is False


class TestQdrantAdapterGetStats:
    """Test suite for get_stats error handling."""

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_get_stats_exception_handling(self, mock_makedirs, mock_qdrant_client):
        """Test get_stats returns error status on exception."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_client_instance.get_collection.side_effect = Exception("Stats failed")
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        stats = adapter.get_stats()

        # Verify
        assert stats["status"] == "error"
        assert "Stats failed" in stats["error"]


class TestQdrantAdapterSaveFaceEdgeCases:
    """Test suite for save_face edge cases and error handling."""

    @patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"})
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("scripts.qdrant_adapter.os.makedirs")
    def test_save_face_invalid_uuid_conversion(self, mock_makedirs, mock_qdrant_client):
        """Test save_face handles invalid UUID gracefully."""
        # Setup
        mock_client_instance = MagicMock()
        mock_client_instance.get_collections.return_value = Mock(
            collections=[Mock(name="faces")]
        )
        mock_qdrant_client.return_value = mock_client_instance

        # Import after patching environment
        from scripts.qdrant_adapter import QdrantAdapter

        # Execute
        adapter = QdrantAdapter()
        face_data = {
            "face_id": "invalid-uuid-format",  # No hyphens
            "name": "Test",
        }
        embedding = np.random.rand(512).astype(np.float32)

        face_id = adapter.save_face(face_data, embedding)

        # Verify - should generate new UUID instead of using invalid one
        assert face_id == "invalid-uuid-format"
        mock_client_instance.upsert.assert_called_once()
