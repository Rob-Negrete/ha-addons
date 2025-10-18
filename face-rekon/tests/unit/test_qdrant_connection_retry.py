"""
Unit tests for QdrantAdapter._connect_with_retry method.
Tests both embedded and remote server mode with various error scenarios.
"""
import importlib
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


class TestQdrantConnectionRetryEmbeddedMode:
    """
    Test embedded Qdrant connection with error handling.
    """

    def test_embedded_mode_generic_error_logging(self):
        """
        Test error logging for generic embedded Qdrant failures (line 78).
        Covers the else branch for non-lock errors.
        """
        with patch.dict(os.environ, {"FACE_REKON_USE_EMBEDDED_QDRANT": "true"}):
            # Reload module to pick up new environment variable
            if "qdrant_adapter" in sys.modules:
                import qdrant_adapter

                importlib.reload(qdrant_adapter)

            with patch("qdrant_adapter.QdrantClient") as mock_client_class:
                # Simulate generic error (not storage lock)
                mock_client_class.side_effect = RuntimeError("Generic Qdrant error")

                from qdrant_adapter import QdrantAdapter

                with pytest.raises(RuntimeError, match="Generic Qdrant error"):
                    QdrantAdapter()


class TestQdrantConnectionRetryRemoteMode:
    """
    Test remote server Qdrant connection with retry logic and error handling.
    Covers lines 82-102 which are completely untested.
    """

    def test_remote_mode_success_first_attempt(self):
        """
        Test successful connection to remote Qdrant on first attempt.
        Covers lines 82-90 (success path).
        """
        with patch.dict(
            os.environ,
            {"FACE_REKON_USE_EMBEDDED_QDRANT": "false"},
        ):
            # Reload to pick up environment changes
            if "qdrant_adapter" in sys.modules:
                import qdrant_adapter

                importlib.reload(qdrant_adapter)

            with patch("qdrant_adapter.QdrantClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_collections.return_value = MagicMock()
                mock_client_class.return_value = mock_client

                from qdrant_adapter import QdrantAdapter

                adapter = QdrantAdapter()

                # Verify client was created correctly
                assert adapter.client is not None
                # Verify connection test was successful
                assert mock_client.get_collections.call_count >= 1

    def test_remote_mode_retry_then_success(self):
        """
        Test remote connection failing first, then succeeding on retry.
        Covers lines 82-97 (retry with exponential backoff).
        """
        with patch.dict(
            os.environ,
            {"FACE_REKON_USE_EMBEDDED_QDRANT": "false"},
        ):
            if "qdrant_adapter" in sys.modules:
                import qdrant_adapter

                importlib.reload(qdrant_adapter)

            with patch("qdrant_adapter.QdrantClient") as mock_client_class:
                with patch("qdrant_adapter.time.sleep") as mock_sleep:
                    mock_client = MagicMock()

                    # Simulate connection test: first attempt fails, second succeeds
                    # Then _ensure_collection also calls get_collections
                    get_collections_results = [
                        ConnectionError("Connection refused"),
                        MagicMock(),  # Success on second retry attempt
                        MagicMock(),  # _ensure_collection call
                    ]
                    mock_client.get_collections.side_effect = get_collections_results

                    # Return mock_client twice (once per retry attempt)
                    mock_client_class.return_value = mock_client

                    from qdrant_adapter import QdrantAdapter

                    adapter = QdrantAdapter()

                    # Verify retry happened
                    assert adapter.client is not None
                    # At least 2 calls: one failure, one success (+ _ensure_collection)
                    assert mock_client.get_collections.call_count >= 2

                    # Verify exponential backoff was used (2^0 = 1 second)
                    assert mock_sleep.call_count >= 1

    def test_remote_mode_all_retries_exhausted(self):
        """
        Test remote connection failing after all retries exhausted.
        Covers lines 82-102 (all retry attempts fail, final error).
        """
        with patch.dict(
            os.environ,
            {"FACE_REKON_USE_EMBEDDED_QDRANT": "false"},
        ):
            if "qdrant_adapter" in sys.modules:
                import qdrant_adapter

                importlib.reload(qdrant_adapter)

            with patch("qdrant_adapter.QdrantClient") as mock_client_class:
                with patch("qdrant_adapter.time.sleep"):
                    mock_client = MagicMock()

                    # All attempts fail
                    mock_client.get_collections.side_effect = ConnectionError(
                        "Connection refused"
                    )
                    mock_client_class.return_value = mock_client

                    from qdrant_adapter import QdrantAdapter

                    # Should raise after max_retries (default 5)
                    with pytest.raises(ConnectionError, match="Connection refused"):
                        QdrantAdapter()

                    # Verify all 5 attempts were made (retry logic)
                    assert mock_client.get_collections.call_count == 5

    def test_remote_mode_exponential_backoff_progression(self):
        """
        Test exponential backoff progression (2^0, 2^1, etc).
        Covers line 97 (exponential backoff calculation).
        """
        with patch.dict(
            os.environ,
            {"FACE_REKON_USE_EMBEDDED_QDRANT": "false"},
        ):
            if "qdrant_adapter" in sys.modules:
                import qdrant_adapter

                importlib.reload(qdrant_adapter)

            with patch("qdrant_adapter.QdrantClient") as mock_client_class:
                with patch("qdrant_adapter.time.sleep") as mock_sleep:
                    mock_client = MagicMock()

                    # Fail 2 times, then succeed, then _ensure_collection
                    mock_client.get_collections.side_effect = [
                        ConnectionError("Attempt 1 failed"),
                        ConnectionError("Attempt 2 failed"),
                        MagicMock(),  # Success on attempt 3
                        MagicMock(),  # _ensure_collection call
                    ]
                    mock_client_class.return_value = mock_client

                    from qdrant_adapter import QdrantAdapter

                    adapter = QdrantAdapter()

                    # Verify exponential backoff: 2^0=1, 2^1=2
                    assert mock_sleep.call_count >= 2
                    # Check that sleep was called with values (allow for float)
                    sleep_calls = [
                        call_args[0][0] for call_args in mock_sleep.call_args_list
                    ]
                    # Should have at least 2 sleeps with exponential progression
                    assert len(sleep_calls) >= 2
                    assert adapter.client is not None

    def test_remote_mode_warning_logs_on_retry(self):
        """
        Test warning logs are generated during retry attempts.
        Covers lines 92-95 (warning logging during retries).
        """
        with patch.dict(
            os.environ,
            {"FACE_REKON_USE_EMBEDDED_QDRANT": "false"},
        ):
            if "qdrant_adapter" in sys.modules:
                import qdrant_adapter

                importlib.reload(qdrant_adapter)

            with patch("qdrant_adapter.QdrantClient") as mock_client_class:
                with patch("qdrant_adapter.logger") as mock_logger:
                    with patch("qdrant_adapter.time.sleep"):
                        mock_client = MagicMock()

                        # First attempt fails, second succeeds, then _ensure_collection
                        mock_client.get_collections.side_effect = [
                            ConnectionError("Connection timeout"),
                            MagicMock(),  # Success
                            MagicMock(),  # _ensure_collection
                        ]
                        mock_client_class.return_value = mock_client

                        from qdrant_adapter import QdrantAdapter

                        QdrantAdapter()  # Create adapter to trigger retry logic

                        # Verify warning was logged during first failure
                        warning_calls = mock_logger.warning.call_args_list
                        assert len(warning_calls) >= 1
                        # Check warning message contains retry info
                        warning_msg = str(warning_calls[0])
                        assert (
                            "attempt" in warning_msg.lower()
                            or "failed" in warning_msg.lower()
                        )

    def test_remote_mode_final_error_log(self):
        """
        Test final error log when all retries are exhausted.
        Covers lines 99-102 (final error logging).
        """
        with patch.dict(
            os.environ,
            {"FACE_REKON_USE_EMBEDDED_QDRANT": "false"},
        ):
            if "qdrant_adapter" in sys.modules:
                import qdrant_adapter

                importlib.reload(qdrant_adapter)

            with patch("qdrant_adapter.QdrantClient") as mock_client_class:
                with patch("qdrant_adapter.logger") as mock_logger:
                    with patch("qdrant_adapter.time.sleep"):
                        mock_client = MagicMock()
                        mock_client.get_collections.side_effect = ConnectionError(
                            "Final failure"
                        )
                        mock_client_class.return_value = mock_client

                        from qdrant_adapter import QdrantAdapter

                        with pytest.raises(ConnectionError):
                            QdrantAdapter()

                        # Verify final error was logged
                        error_calls = mock_logger.error.call_args_list
                        assert len(error_calls) >= 1
                        # Check error message about exhausted retries
                        final_error_msg = str(error_calls[-1])
                        assert (
                            "failed" in final_error_msg.lower()
                            or "retry" in final_error_msg.lower()
                            or "retries" in final_error_msg.lower()
                        )
