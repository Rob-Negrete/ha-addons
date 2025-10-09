"""
Integration tests for save_face_crop_to_file function with real ML dependencies.

This module tests save_face_crop_to_file in Docker environment with:
- Real OpenCV and PIL operations
- Actual file system operations
- Real image processing pipeline
"""

import os
import shutil
import tempfile

import numpy as np
import pytest


class TestSaveFaceCropToFileIntegration:
    """Docker integration tests for save_face_crop_to_file function."""

    def test_success_with_rgb_image(self):
        """Test successful save with RGB (3-channel) image in Docker."""
        try:
            from scripts.clasificador import save_face_crop_to_file

            # Create temporary thumbnail directory
            temp_dir = tempfile.mkdtemp()

            try:
                # Patch THUMBNAIL_PATH to use temp directory
                import scripts.clasificador

                original_path = scripts.clasificador.THUMBNAIL_PATH
                scripts.clasificador.THUMBNAIL_PATH = temp_dir

                # Create a real 3-channel BGR image (OpenCV format)
                face_crop = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
                face_id = "test_rgb_face_123"

                # Execute
                result = save_face_crop_to_file(face_crop, face_id)

                # Verify
                assert result != ""
                assert result.endswith("test_rgb_face_123.jpg")
                assert os.path.exists(result)

                # Verify file is a valid JPEG
                assert os.path.getsize(result) > 0

                # Verify we can read it back
                from PIL import Image

                img = Image.open(result)
                assert img.format == "JPEG"
                assert img.size == (160, 160)  # Thumbnail size

            finally:
                # Restore original path
                scripts.clasificador.THUMBNAIL_PATH = original_path
                # Clean up
                shutil.rmtree(temp_dir, ignore_errors=True)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_success_with_grayscale_image(self):
        """Test successful save with grayscale (single-channel) image."""
        try:
            from scripts.clasificador import save_face_crop_to_file

            temp_dir = tempfile.mkdtemp()

            try:
                import scripts.clasificador

                original_path = scripts.clasificador.THUMBNAIL_PATH
                scripts.clasificador.THUMBNAIL_PATH = temp_dir

                # Create grayscale image
                face_crop = np.random.randint(0, 255, (200, 200), dtype=np.uint8)
                face_id = "test_gray_face_456"

                # Execute
                result = save_face_crop_to_file(face_crop, face_id)

                # Verify
                assert result != ""
                assert result.endswith("test_gray_face_456.jpg")
                assert os.path.exists(result)
                assert os.path.getsize(result) > 0

            finally:
                scripts.clasificador.THUMBNAIL_PATH = original_path
                shutil.rmtree(temp_dir, ignore_errors=True)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_directory_creation_fallback(self):
        """
        Test fallback to /tmp when primary directory creation fails.

        This test uses mocking to simulate OSError during directory creation.
        """
        try:
            from unittest.mock import patch

            import scripts.clasificador
            from scripts.clasificador import save_face_crop_to_file

            original_path = scripts.clasificador.THUMBNAIL_PATH

            try:
                protected_dir = "/protected/thumbnails"
                scripts.clasificador.THUMBNAIL_PATH = protected_dir

                face_crop = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
                face_id = "fallback_test_789"

                # Mock os.makedirs to fail on first call, succeed on second
                original_makedirs = os.makedirs
                call_count = [0]

                def mock_makedirs(path, exist_ok=False):
                    call_count[0] += 1
                    if call_count[0] == 1:
                        # First call (protected dir) fails
                        raise OSError("Permission denied")
                    else:
                        # Second call (fallback /tmp) succeeds
                        return original_makedirs(path, exist_ok=exist_ok)

                # Execute with mocked makedirs
                with patch("os.makedirs", side_effect=mock_makedirs):
                    result = save_face_crop_to_file(face_crop, face_id)

                # Should fallback to /tmp
                assert result != ""
                assert "/tmp/face_rekon_thumbnails" in result
                assert result.endswith("fallback_test_789.jpg")

                # Verify file was created in fallback location
                assert os.path.exists(result)

                # Clean up fallback file
                os.remove(result)

            finally:
                scripts.clasificador.THUMBNAIL_PATH = original_path

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_exception_handling_invalid_array(self):
        """Test exception handling with invalid numpy array."""
        try:
            from scripts.clasificador import save_face_crop_to_file

            temp_dir = tempfile.mkdtemp()

            try:
                import scripts.clasificador

                original_path = scripts.clasificador.THUMBNAIL_PATH
                scripts.clasificador.THUMBNAIL_PATH = temp_dir

                # Create invalid array (empty)
                face_crop = np.array([])
                face_id = "error_face_999"

                # Execute
                result = save_face_crop_to_file(face_crop, face_id)

                # Should return empty string on error
                assert result == ""

            finally:
                scripts.clasificador.THUMBNAIL_PATH = original_path
                shutil.rmtree(temp_dir, ignore_errors=True)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_edge_case_empty_face_id(self):
        """Test handling of empty face_id."""
        try:
            from scripts.clasificador import save_face_crop_to_file

            temp_dir = tempfile.mkdtemp()

            try:
                import scripts.clasificador

                original_path = scripts.clasificador.THUMBNAIL_PATH
                scripts.clasificador.THUMBNAIL_PATH = temp_dir

                face_crop = np.random.randint(0, 255, (200, 200), dtype=np.uint8)
                face_id = ""

                # Execute
                result = save_face_crop_to_file(face_crop, face_id)

                # Should work, filename will be .jpg
                assert result != ""
                assert result.endswith(".jpg")
                assert os.path.exists(result)

            finally:
                scripts.clasificador.THUMBNAIL_PATH = original_path
                shutil.rmtree(temp_dir, ignore_errors=True)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_large_image_processing(self):
        """Test processing of large images."""
        try:
            from scripts.clasificador import save_face_crop_to_file

            temp_dir = tempfile.mkdtemp()

            try:
                import scripts.clasificador

                original_path = scripts.clasificador.THUMBNAIL_PATH
                scripts.clasificador.THUMBNAIL_PATH = temp_dir

                # Create a large image
                face_crop = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
                face_id = "large_face_101"

                # Execute
                result = save_face_crop_to_file(face_crop, face_id)

                # Should successfully resize to thumbnail
                assert result != ""
                assert os.path.exists(result)

                # Verify thumbnail is correct size
                from PIL import Image

                img = Image.open(result)
                assert img.size == (160, 160)

            finally:
                scripts.clasificador.THUMBNAIL_PATH = original_path
                shutil.rmtree(temp_dir, ignore_errors=True)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_multiple_saves_same_directory(self):
        """Test multiple saves to the same directory."""
        try:
            from scripts.clasificador import save_face_crop_to_file

            temp_dir = tempfile.mkdtemp()

            try:
                import scripts.clasificador

                original_path = scripts.clasificador.THUMBNAIL_PATH
                scripts.clasificador.THUMBNAIL_PATH = temp_dir

                face_crop = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)

                # Save multiple faces
                results = []
                for i in range(3):
                    face_id = f"batch_face_{i}"
                    result = save_face_crop_to_file(face_crop, face_id)
                    results.append(result)

                # Verify all were saved
                for result in results:
                    assert result != ""
                    assert os.path.exists(result)

                # Verify all files are different
                assert len(set(results)) == 3

            finally:
                scripts.clasificador.THUMBNAIL_PATH = original_path
                shutil.rmtree(temp_dir, ignore_errors=True)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_overwrite_existing_file(self):
        """Test that saving with same face_id overwrites existing file."""
        try:
            from scripts.clasificador import save_face_crop_to_file

            temp_dir = tempfile.mkdtemp()

            try:
                import scripts.clasificador

                original_path = scripts.clasificador.THUMBNAIL_PATH
                scripts.clasificador.THUMBNAIL_PATH = temp_dir

                face_id = "duplicate_face_202"

                # Save first face
                face_crop_1 = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
                result_1 = save_face_crop_to_file(face_crop_1, face_id)

                # Get modification time
                mtime_1 = os.path.getmtime(result_1)

                # Wait a bit
                import time

                time.sleep(0.1)

                # Save second face with same ID
                face_crop_2 = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
                result_2 = save_face_crop_to_file(face_crop_2, face_id)

                # Should be same path
                assert result_1 == result_2

                # But modification time should be different (overwritten)
                mtime_2 = os.path.getmtime(result_2)
                assert mtime_2 > mtime_1

            finally:
                scripts.clasificador.THUMBNAIL_PATH = original_path
                shutil.rmtree(temp_dir, ignore_errors=True)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")
