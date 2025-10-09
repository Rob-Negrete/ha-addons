"""
Unit tests for QdrantAdapter._connect_with_retry method.

This module tests all code paths of the _connect_with_retry method,
including embedded mode, remote mode, retry logic, and error scenarios.
"""

from unittest.mock import Mock, patch

import pytest

from scripts.qdrant_adapter import QdrantAdapter


class TestQdrantAdapterConnectWithRetry:
    """Test suite for _connect_with_retry method."""

    @patch("scripts.qdrant_adapter.USE_EMBEDDED_QDRANT", True)
    @patch("scripts.qdrant_adapter.QDRANT_PATH", "/tmp/test_qdrant")
    @patch("scripts.qdrant_adapter.QdrantAdapter._ensure_collection")
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("os.makedirs")
    def test_embedded_mode_success(self, mock_makedirs, mock_client_class, mock_ensure):
        """Test successful connection in embedded mode."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        adapter = QdrantAdapter()

        # Verify embedded client was created
        mock_makedirs.assert_called_once_with("/tmp/test_qdrant", exist_ok=True)
        mock_client_class.assert_called_with(path="/tmp/test_qdrant")
        assert adapter.client == mock_client

    @patch("scripts.qdrant_adapter.USE_EMBEDDED_QDRANT", True)
    @patch("scripts.qdrant_adapter.QDRANT_PATH", "/tmp/test_qdrant")
    @patch("scripts.qdrant_adapter.QdrantAdapter._ensure_collection")
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("os.makedirs")
    def test_embedded_mode_storage_lock_error(
        self, mock_makedirs, mock_client_class, mock_ensure
    ):
        """Test embedded mode with storage lock conflict (Flask reload scenario)."""
        # Simulate storage lock error
        mock_client_class.side_effect = Exception(
            "Database already accessed by another instance"
        )

        with pytest.raises(Exception) as exc_info:
            QdrantAdapter()

        assert "already accessed by another instance" in str(exc_info.value)
        mock_makedirs.assert_called_once()

    @patch("scripts.qdrant_adapter.USE_EMBEDDED_QDRANT", True)
    @patch("scripts.qdrant_adapter.QDRANT_PATH", "/tmp/test_qdrant")
    @patch("scripts.qdrant_adapter.QdrantAdapter._ensure_collection")
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("os.makedirs")
    def test_embedded_mode_other_exception(
        self, mock_makedirs, mock_client_class, mock_ensure
    ):
        """Test embedded mode with non-lock exception."""
        # Simulate other initialization error
        mock_client_class.side_effect = Exception("Connection refused")

        with pytest.raises(Exception) as exc_info:
            QdrantAdapter()

        assert "Connection refused" in str(exc_info.value)
        mock_makedirs.assert_called_once()

    @patch("scripts.qdrant_adapter.USE_EMBEDDED_QDRANT", False)
    @patch("scripts.qdrant_adapter.QDRANT_HOST", "test-host")
    @patch("scripts.qdrant_adapter.QDRANT_PORT", 6333)
    @patch("scripts.qdrant_adapter.QdrantAdapter._ensure_collection")
    @patch("scripts.qdrant_adapter.QdrantClient")
    def test_remote_mode_success_first_attempt(self, mock_client_class, mock_ensure):
        """Test successful connection to remote server on first attempt."""
        mock_client = Mock()
        mock_client.get_collections.return_value = []
        mock_client_class.return_value = mock_client

        adapter = QdrantAdapter()

        # Verify remote client was created
        mock_client_class.assert_called_with(host="test-host", port=6333)
        mock_client.get_collections.assert_called_once()
        assert adapter.client == mock_client

    @patch("scripts.qdrant_adapter.USE_EMBEDDED_QDRANT", False)
    @patch("scripts.qdrant_adapter.QDRANT_HOST", "test-host")
    @patch("scripts.qdrant_adapter.QDRANT_PORT", 6333)
    @patch("scripts.qdrant_adapter.QdrantAdapter._ensure_collection")
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("time.sleep")
    def test_remote_mode_retry_success(
        self, mock_sleep, mock_client_class, mock_ensure
    ):
        """Test remote mode with retry - succeeds on second attempt."""
        mock_client = Mock()
        mock_client.get_collections.side_effect = [
            Exception("Connection timeout"),  # First attempt fails
            [],  # Second attempt succeeds
        ]
        mock_client_class.return_value = mock_client

        adapter = QdrantAdapter()

        # Verify retry logic
        assert mock_client.get_collections.call_count == 2
        mock_sleep.assert_called_once_with(1)  # 2^0 = 1 second backoff
        assert adapter.client == mock_client

    @patch("scripts.qdrant_adapter.USE_EMBEDDED_QDRANT", False)
    @patch("scripts.qdrant_adapter.QDRANT_HOST", "test-host")
    @patch("scripts.qdrant_adapter.QDRANT_PORT", 6333)
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("time.sleep")
    def test_remote_mode_all_retries_fail(self, mock_sleep, mock_client_class):
        """Test remote mode when all retry attempts fail."""
        mock_client = Mock()
        mock_client.get_collections.side_effect = Exception("Connection refused")
        mock_client_class.return_value = mock_client

        with pytest.raises(Exception) as exc_info:
            QdrantAdapter()

        assert "Connection refused" in str(exc_info.value)
        # Should retry 5 times (max_retries=5)
        assert mock_client.get_collections.call_count == 5
        # Should sleep 4 times (not after last attempt)
        assert mock_sleep.call_count == 4
        # Verify exponential backoff: 2^0, 2^1, 2^2, 2^3
        expected_sleeps = [1, 2, 4, 8]
        actual_sleeps = [call[0][0] for call in mock_sleep.call_args_list]
        assert actual_sleeps == expected_sleeps

    @patch("scripts.qdrant_adapter.USE_EMBEDDED_QDRANT", False)
    @patch("scripts.qdrant_adapter.QDRANT_HOST", "test-host")
    @patch("scripts.qdrant_adapter.QDRANT_PORT", 6333)
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("time.sleep")
    def test_remote_mode_custom_max_retries(self, mock_sleep, mock_client_class):
        """Test remote mode with custom max_retries parameter."""
        mock_client = Mock()
        mock_client.get_collections.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_client

        # Create adapter instance manually to pass max_retries
        adapter = object.__new__(QdrantAdapter)
        adapter.client = None

        with pytest.raises(Exception) as exc_info:
            adapter._connect_with_retry(max_retries=3)

        assert "Network error" in str(exc_info.value)
        # Should retry 3 times
        assert mock_client.get_collections.call_count == 3
        # Should sleep 2 times
        assert mock_sleep.call_count == 2

    @patch("scripts.qdrant_adapter.USE_EMBEDDED_QDRANT", False)
    @patch("scripts.qdrant_adapter.QDRANT_HOST", "test-host")
    @patch("scripts.qdrant_adapter.QDRANT_PORT", 6333)
    @patch("scripts.qdrant_adapter.QdrantAdapter._ensure_collection")
    @patch("scripts.qdrant_adapter.QdrantClient")
    @patch("time.sleep")
    def test_remote_mode_intermittent_failures(
        self, mock_sleep, mock_client_class, mock_ensure
    ):
        """Test remote mode with intermittent failures before success."""
        mock_client = Mock()
        mock_client.get_collections.side_effect = [
            Exception("Timeout"),  # Attempt 1 fails
            Exception("Network unreachable"),  # Attempt 2 fails
            Exception("Connection reset"),  # Attempt 3 fails
            [],  # Attempt 4 succeeds
        ]
        mock_client_class.return_value = mock_client

        adapter = QdrantAdapter()

        # Should succeed on 4th attempt
        assert mock_client.get_collections.call_count == 4
        # Should sleep 3 times (after attempts 1, 2, 3)
        assert mock_sleep.call_count == 3
        # Exponential backoff: 1, 2, 4
        expected_sleeps = [1, 2, 4]
        actual_sleeps = [call[0][0] for call in mock_sleep.call_args_list]
        assert actual_sleeps == expected_sleeps
        assert adapter.client == mock_client
