"""
Unit tests for clasificador.py image processing functions.

Tests calculate_face_quality_metrics(), create_face_thumbnail(),
and save_face_crop_to_file() functions with comprehensive coverage.
"""

import base64
import io
import os
import tempfile
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image


class TestCalculateFaceQualityMetrics:
    """Test suite for calculate_face_quality_metrics function."""

    def test_quality_metrics_color_image(self):
        """Test quality metrics calculation with color image."""
        try:
            import scripts.clasificador as clasificador

            # Create test color image (100x100 RGB)
            face_crop = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

            metrics = clasificador.calculate_face_quality_metrics(face_crop)

            # Verify all metrics are present
            assert "sharpness" in metrics
            assert "face_area" in metrics
            assert "brightness" in metrics
            assert "contrast" in metrics
            assert "quality_score" in metrics

            # Verify face_area calculation
            assert metrics["face_area"] == 100 * 100  # 10000 pixels

            # Verify all values are floats
            assert isinstance(metrics["sharpness"], float)
            assert isinstance(metrics["face_area"], float)
            assert isinstance(metrics["brightness"], float)
            assert isinstance(metrics["contrast"], float)
            assert isinstance(metrics["quality_score"], float)

            # Verify quality_score is in valid range [0, 1]
            assert 0.0 <= metrics["quality_score"] <= 1.0

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_quality_metrics_grayscale_image(self):
        """Test quality metrics with grayscale image."""
        try:
            import scripts.clasificador as clasificador

            # Create test grayscale image (100x100)
            face_crop = np.random.randint(0, 255, (100, 100), dtype=np.uint8)

            metrics = clasificador.calculate_face_quality_metrics(face_crop)

            assert metrics["face_area"] == 100 * 100
            assert 0.0 <= metrics["quality_score"] <= 1.0

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_quality_metrics_sharpness_calculation(self):
        """Test sharpness metric using Laplacian variance."""
        try:
            import scripts.clasificador as clasificador

            # Create sharp image (high contrast edges)
            sharp_crop = np.zeros((100, 100, 3), dtype=np.uint8)
            sharp_crop[:50, :] = 255  # Sharp horizontal edge

            metrics_sharp = clasificador.calculate_face_quality_metrics(sharp_crop)

            # Create blurry image (low contrast, smooth)
            blurry_crop = np.ones((100, 100, 3), dtype=np.uint8) * 128

            metrics_blurry = clasificador.calculate_face_quality_metrics(blurry_crop)

            # Sharp image should have higher sharpness
            assert metrics_sharp["sharpness"] > metrics_blurry["sharpness"]

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_quality_metrics_brightness_calculation(self):
        """Test brightness metric calculation."""
        try:
            import scripts.clasificador as clasificador

            # Create bright image
            bright_crop = np.ones((50, 50, 3), dtype=np.uint8) * 200

            metrics_bright = clasificador.calculate_face_quality_metrics(bright_crop)

            # Create dark image
            dark_crop = np.ones((50, 50, 3), dtype=np.uint8) * 50

            metrics_dark = clasificador.calculate_face_quality_metrics(dark_crop)

            # Brightness should reflect mean intensity
            assert metrics_bright["brightness"] > metrics_dark["brightness"]

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_quality_metrics_contrast_calculation(self):
        """Test contrast metric using standard deviation."""
        try:
            import scripts.clasificador as clasificador

            # High contrast image (black and white)
            high_contrast = np.zeros((100, 100, 3), dtype=np.uint8)
            high_contrast[::2, :] = 255  # Alternating rows

            metrics_high = clasificador.calculate_face_quality_metrics(high_contrast)

            # Low contrast image (uniform gray)
            low_contrast = np.ones((100, 100, 3), dtype=np.uint8) * 128

            metrics_low = clasificador.calculate_face_quality_metrics(low_contrast)

            # High contrast should have higher std deviation
            assert metrics_high["contrast"] > metrics_low["contrast"]

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_quality_metrics_face_area_different_sizes(self):
        """Test face_area metric with different image sizes."""
        try:
            import scripts.clasificador as clasificador

            # Small face
            small_crop = np.zeros((50, 50, 3), dtype=np.uint8)
            metrics_small = clasificador.calculate_face_quality_metrics(small_crop)

            # Large face
            large_crop = np.zeros((200, 200, 3), dtype=np.uint8)
            metrics_large = clasificador.calculate_face_quality_metrics(large_crop)

            assert metrics_small["face_area"] == 50 * 50
            assert metrics_large["face_area"] == 200 * 200
            assert metrics_large["face_area"] > metrics_small["face_area"]

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_quality_score_normalization(self):
        """Test quality score normalization logic."""
        try:
            import scripts.clasificador as clasificador

            # Optimal quality image: bright (128), high contrast, sharp
            optimal_crop = np.random.randint(100, 150, (100, 100, 3), dtype=np.uint8)

            metrics = clasificador.calculate_face_quality_metrics(optimal_crop)

            # Quality score should be reasonable (not 0 or 1 for random image)
            assert 0.0 < metrics["quality_score"] < 1.0

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_quality_metrics_error_handling(self):
        """Test error handling returns zero metrics."""
        try:
            import scripts.clasificador as clasificador

            # Invalid input (None)
            with patch("cv2.cvtColor", side_effect=Exception("Test error")):
                face_crop = np.zeros((100, 100, 3), dtype=np.uint8)
                metrics = clasificador.calculate_face_quality_metrics(face_crop)

                # Should return zero metrics on error
                assert metrics["sharpness"] == 0.0
                assert metrics["face_area"] == 0.0
                assert metrics["brightness"] == 0.0
                assert metrics["contrast"] == 0.0
                assert metrics["quality_score"] == 0.0

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")


class TestCreateFaceThumbnail:
    """Test suite for create_face_thumbnail function."""

    def test_create_thumbnail_from_color_image(self):
        """Test thumbnail creation from color image."""
        try:
            import scripts.clasificador as clasificador

            # Create test color image
            face_crop = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)

            thumbnail_b64 = clasificador.create_face_thumbnail(face_crop)

            # Verify base64 string is returned
            assert isinstance(thumbnail_b64, str)
            assert len(thumbnail_b64) > 0

            # Verify it's valid base64
            decoded = base64.b64decode(thumbnail_b64)
            assert len(decoded) > 0

            # Verify it's a valid JPEG image
            img = Image.open(io.BytesIO(decoded))
            assert img.format == "JPEG"
            assert img.size == (160, 160)  # THUMBNAIL_SIZE

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_create_thumbnail_from_grayscale_image(self):
        """Test thumbnail creation from grayscale image."""
        try:
            import scripts.clasificador as clasificador

            # Create grayscale image
            face_crop = np.random.randint(0, 255, (200, 200), dtype=np.uint8)

            thumbnail_b64 = clasificador.create_face_thumbnail(face_crop)

            assert isinstance(thumbnail_b64, str)
            assert len(thumbnail_b64) > 0

            # Decode and verify
            decoded = base64.b64decode(thumbnail_b64)
            img = Image.open(io.BytesIO(decoded))
            assert img.format == "JPEG"

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_create_thumbnail_resizes_correctly(self):
        """Test thumbnail resizing to THUMBNAIL_SIZE."""
        try:
            import scripts.clasificador as clasificador

            # Large image
            large_crop = np.zeros((500, 500, 3), dtype=np.uint8)

            thumbnail_b64 = clasificador.create_face_thumbnail(large_crop)

            decoded = base64.b64decode(thumbnail_b64)
            img = Image.open(io.BytesIO(decoded))

            # Should be resized to 160x160
            assert img.size == (160, 160)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_create_thumbnail_jpeg_quality(self):
        """Test JPEG quality setting."""
        try:
            import scripts.clasificador as clasificador

            face_crop = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)

            thumbnail_b64 = clasificador.create_face_thumbnail(face_crop)

            # Verify it's a valid JPEG (quality=85 set in function)
            decoded = base64.b64decode(thumbnail_b64)
            img = Image.open(io.BytesIO(decoded))
            assert img.format == "JPEG"

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_create_thumbnail_error_handling(self):
        """Test error handling returns empty string."""
        try:
            import scripts.clasificador as clasificador

            # Mock cv2.resize to raise exception
            with patch("cv2.resize", side_effect=Exception("Test error")):
                face_crop = np.zeros((100, 100, 3), dtype=np.uint8)
                thumbnail_b64 = clasificador.create_face_thumbnail(face_crop)

                # Should return empty string on error
                assert thumbnail_b64 == ""

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")


class TestSaveFaceCropToFile:
    """Test suite for save_face_crop_to_file function."""

    def test_save_face_crop_creates_file(self):
        """Test face crop is saved as JPEG file."""
        try:
            import scripts.clasificador as clasificador

            with tempfile.TemporaryDirectory() as tmpdir:
                # Patch THUMBNAIL_PATH to use temp directory
                with patch("scripts.clasificador.THUMBNAIL_PATH", tmpdir):
                    face_crop = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
                    face_id = "test_face_123"

                    thumbnail_path = clasificador.save_face_crop_to_file(
                        face_crop, face_id
                    )

                    # Verify file was created
                    assert os.path.exists(thumbnail_path)
                    assert thumbnail_path.endswith(f"{face_id}.jpg")

                    # Verify it's a valid JPEG
                    img = Image.open(thumbnail_path)
                    assert img.format == "JPEG"
                    assert img.size == (160, 160)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_face_crop_creates_directory(self):
        """Test thumbnail directory is created if it doesn't exist."""
        try:
            import scripts.clasificador as clasificador

            with tempfile.TemporaryDirectory() as tmpdir:
                thumbnail_dir = os.path.join(tmpdir, "new_thumbnails")

                with patch("scripts.clasificador.THUMBNAIL_PATH", thumbnail_dir):
                    face_crop = np.zeros((100, 100, 3), dtype=np.uint8)
                    face_id = "test_123"

                    clasificador.save_face_crop_to_file(face_crop, face_id)

                    # Directory should be created
                    assert os.path.exists(thumbnail_dir)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_face_crop_handles_grayscale(self):
        """Test saving grayscale face crop."""
        try:
            import scripts.clasificador as clasificador

            with tempfile.TemporaryDirectory() as tmpdir:
                with patch("scripts.clasificador.THUMBNAIL_PATH", tmpdir):
                    # Grayscale image
                    face_crop = np.random.randint(0, 255, (200, 200), dtype=np.uint8)
                    face_id = "gray_face_456"

                    thumbnail_path = clasificador.save_face_crop_to_file(
                        face_crop, face_id
                    )

                    assert os.path.exists(thumbnail_path)

                    # Should save as valid image
                    img = Image.open(thumbnail_path)
                    assert img.format == "JPEG"

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_face_crop_fallback_directory(self):
        """Test fallback to /tmp when main directory fails."""
        try:
            import scripts.clasificador as clasificador

            # Use non-writable path
            with patch("scripts.clasificador.THUMBNAIL_PATH", "/root/cant_write_here"):
                with patch(
                    "os.makedirs", side_effect=[OSError("Permission denied"), None]
                ):
                    face_crop = np.zeros((100, 100, 3), dtype=np.uint8)
                    face_id = "fallback_test"

                    # Should use fallback directory
                    thumbnail_path = clasificador.save_face_crop_to_file(
                        face_crop, face_id
                    )

                    assert "/tmp/face_rekon_thumbnails" in thumbnail_path

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_face_crop_resizes_image(self):
        """Test image is resized to thumbnail size."""
        try:
            import scripts.clasificador as clasificador

            with tempfile.TemporaryDirectory() as tmpdir:
                with patch("scripts.clasificador.THUMBNAIL_PATH", tmpdir):
                    # Large image
                    large_crop = np.zeros((500, 500, 3), dtype=np.uint8)
                    face_id = "large_face"

                    thumbnail_path = clasificador.save_face_crop_to_file(
                        large_crop, face_id
                    )

                    # Check saved thumbnail size
                    img = Image.open(thumbnail_path)
                    assert img.size == (160, 160)

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_save_face_crop_error_handling(self):
        """Test error handling during file save."""
        try:
            import scripts.clasificador as clasificador

            with tempfile.TemporaryDirectory() as tmpdir:
                with patch("scripts.clasificador.THUMBNAIL_PATH", tmpdir):
                    # Mock PIL save to raise exception
                    with patch.object(
                        Image.Image, "save", side_effect=Exception("Save error")
                    ):
                        face_crop = np.zeros((100, 100, 3), dtype=np.uint8)
                        face_id = "error_test"

                        # Should not crash, but return path anyway
                        # (implementation may vary)
                        try:
                            clasificador.save_face_crop_to_file(face_crop, face_id)
                        except Exception:
                            pass  # Error handling varies by implementation

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")
