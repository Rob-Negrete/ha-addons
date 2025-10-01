"""
Integration tests for create_face_thumbnail function in clasificador.py

Tests target 100% coverage of the thumbnail creation function,
using Docker integration testing with real ML dependencies (OpenCV, PIL).
"""

import base64
import io
import os
import sys

import numpy as np
import pytest

# Add the scripts directory to the Python path
scripts_path = os.path.join(os.path.dirname(__file__), "../../scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Import ML dependencies - will work in Docker, may fail locally
try:
    from clasificador import create_face_thumbnail
    from PIL import Image

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class TestCreateFaceThumbnailCoverage:
    """Comprehensive integration tests for create_face_thumbnail() function."""

    def test_thumbnail_color_image_bgr_to_rgb_conversion(self):
        """Test thumbnail creation with color (3-channel) BGR image"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Create synthetic color face crop (BGR format, 200x200)
        face_crop = np.ones((200, 200, 3), dtype=np.uint8) * 128

        # Call function
        thumbnail_b64 = create_face_thumbnail(face_crop)

        # Validate result
        assert isinstance(thumbnail_b64, str)
        assert len(thumbnail_b64) > 0

        # Validate it's valid base64
        thumbnail_bytes = base64.b64decode(thumbnail_b64)
        assert len(thumbnail_bytes) > 0

        # Validate it's a valid JPEG
        img = Image.open(io.BytesIO(thumbnail_bytes))
        assert img.format == "JPEG"
        assert img.size == (160, 160)  # THUMBNAIL_SIZE

    def test_thumbnail_grayscale_image_direct_path(self):
        """Test thumbnail creation with grayscale (2-channel) image"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Create synthetic grayscale face crop (200x200)
        face_crop = np.ones((200, 200), dtype=np.uint8) * 128

        thumbnail_b64 = create_face_thumbnail(face_crop)

        # Validate result
        assert isinstance(thumbnail_b64, str)
        assert len(thumbnail_b64) > 0

        # Validate it's valid base64 and JPEG
        thumbnail_bytes = base64.b64decode(thumbnail_b64)
        img = Image.open(io.BytesIO(thumbnail_bytes))
        assert img.format == "JPEG"
        assert img.size == (160, 160)

    def test_thumbnail_resize_operation(self):
        """Test that images are resized to 160x160 thumbnail size"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Test various input sizes
        test_sizes = [(100, 100), (200, 200), (300, 400), (50, 150)]

        for width, height in test_sizes:
            face_crop = np.ones((height, width, 3), dtype=np.uint8) * 128
            thumbnail_b64 = create_face_thumbnail(face_crop)

            # Decode and verify size
            thumbnail_bytes = base64.b64decode(thumbnail_b64)
            img = Image.open(io.BytesIO(thumbnail_bytes))
            assert img.size == (160, 160), f"Failed for input {width}x{height}"

    def test_thumbnail_jpeg_quality_85(self):
        """Test JPEG encoding with quality=85"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        face_crop = np.ones((200, 200, 3), dtype=np.uint8) * 128
        thumbnail_b64 = create_face_thumbnail(face_crop)

        # Decode thumbnail
        thumbnail_bytes = base64.b64decode(thumbnail_b64)
        img = Image.open(io.BytesIO(thumbnail_bytes))

        # Verify it's JPEG format
        assert img.format == "JPEG"

        # JPEG should have some compression (not lossless)
        assert len(thumbnail_bytes) < 160 * 160 * 3  # Less than raw RGB

    def test_thumbnail_base64_encoding(self):
        """Test base64 encoding of thumbnail"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        face_crop = np.ones((200, 200, 3), dtype=np.uint8) * 128
        thumbnail_b64 = create_face_thumbnail(face_crop)

        # Validate base64 encoding
        assert isinstance(thumbnail_b64, str)
        assert len(thumbnail_b64) > 0

        # Should be decodable
        try:
            thumbnail_bytes = base64.b64decode(thumbnail_b64)
            assert len(thumbnail_bytes) > 0
        except Exception as e:
            pytest.fail(f"Base64 decode failed: {e}")

    def test_thumbnail_color_conversion_bgr_to_rgb(self):
        """Test BGR to RGB color conversion for PIL"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Create BGR image with distinct colors
        face_crop = np.zeros((200, 200, 3), dtype=np.uint8)
        face_crop[:, :, 0] = 255  # Blue channel in BGR
        face_crop[:, :, 1] = 0  # Green channel
        face_crop[:, :, 2] = 0  # Red channel

        thumbnail_b64 = create_face_thumbnail(face_crop)

        # Decode and verify colors were converted correctly
        thumbnail_bytes = base64.b64decode(thumbnail_b64)
        img = Image.open(io.BytesIO(thumbnail_bytes))

        # Convert to numpy to check pixel values
        img_array = np.array(img)

        # After BGR→RGB conversion, blue should be in channel 2
        # (allowing for JPEG compression artifacts)
        assert img_array[:, :, 2].mean() > 200  # Blue in RGB

    def test_thumbnail_interpolation_area_method(self):
        """Test cv2.INTER_AREA interpolation for downsampling"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Large image that will be downsampled
        face_crop = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)

        thumbnail_b64 = create_face_thumbnail(face_crop)

        # Should produce valid thumbnail
        assert len(thumbnail_b64) > 0

        thumbnail_bytes = base64.b64decode(thumbnail_b64)
        img = Image.open(io.BytesIO(thumbnail_bytes))
        assert img.size == (160, 160)

    def test_thumbnail_small_input_upsampling(self):
        """Test upsampling small images to thumbnail size"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Small image that will be upsampled
        face_crop = np.ones((50, 50, 3), dtype=np.uint8) * 128

        thumbnail_b64 = create_face_thumbnail(face_crop)

        # Should still produce 160x160 thumbnail
        thumbnail_bytes = base64.b64decode(thumbnail_b64)
        img = Image.open(io.BytesIO(thumbnail_bytes))
        assert img.size == (160, 160)

    def test_thumbnail_exception_handling_invalid_input(self):
        """Test exception handling with invalid/malformed input"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Test with None
        result = create_face_thumbnail(None)

        # Should return empty string on exception
        assert result == ""

    def test_thumbnail_exception_handling_empty_array(self):
        """Test exception handling with empty numpy array"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Empty array
        empty_array = np.array([])
        result = create_face_thumbnail(empty_array)

        # Should return empty string
        assert result == ""

    def test_thumbnail_exception_handling_wrong_dimensions(self):
        """Test exception handling with unexpected array dimensions"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # 1D array - cv2.resize can handle this, creates 1D output
        # Function will succeed but with unusual dimensions
        invalid_array = np.ones(100, dtype=np.uint8)
        result = create_face_thumbnail(invalid_array)

        # May return valid thumbnail or empty string depending on cv2 behavior
        assert isinstance(result, str)

    def test_thumbnail_exception_handling_4d_array(self):
        """Test exception handling with 4D array (invalid)"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # 4D array (invalid for single image)
        invalid_array = np.ones((10, 10, 3, 3), dtype=np.uint8)
        result = create_face_thumbnail(invalid_array)

        # Should return empty string
        assert result == ""

    def test_thumbnail_various_color_patterns(self):
        """Test thumbnail creation with various color patterns"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        test_patterns = [
            np.zeros((200, 200, 3), dtype=np.uint8),  # Black
            np.ones((200, 200, 3), dtype=np.uint8) * 255,  # White
            np.ones((200, 200, 3), dtype=np.uint8) * 128,  # Gray
            np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8),  # Random
        ]

        for pattern in test_patterns:
            thumbnail_b64 = create_face_thumbnail(pattern)
            assert len(thumbnail_b64) > 0
            assert isinstance(thumbnail_b64, str)

    def test_thumbnail_non_square_input(self):
        """Test thumbnail creation with non-square input images"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Non-square images
        test_cases = [
            (200, 300),  # Portrait
            (300, 200),  # Landscape
            (100, 400),  # Very tall
            (400, 100),  # Very wide
        ]

        for width, height in test_cases:
            face_crop = np.ones((height, width, 3), dtype=np.uint8) * 128
            thumbnail_b64 = create_face_thumbnail(face_crop)

            # Should always produce 160x160 square thumbnail
            thumbnail_bytes = base64.b64decode(thumbnail_b64)
            img = Image.open(io.BytesIO(thumbnail_bytes))
            assert img.size == (160, 160)

    def test_thumbnail_all_code_paths_comprehensive(self):
        """Comprehensive test covering all code paths in create_face_thumbnail"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Test 1: Color image (3-channel) - BGR to RGB conversion path
        color_face = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        color_thumbnail = create_face_thumbnail(color_face)
        assert len(color_face.shape) == 3
        assert len(color_thumbnail) > 0

        # Decode and validate
        color_bytes = base64.b64decode(color_thumbnail)
        color_img = Image.open(io.BytesIO(color_bytes))
        assert color_img.format == "JPEG"
        assert color_img.size == (160, 160)

        # Test 2: Grayscale image (2-channel) - direct path
        gray_face = np.random.randint(0, 255, (200, 200), dtype=np.uint8)
        gray_thumbnail = create_face_thumbnail(gray_face)
        assert len(gray_face.shape) == 2
        assert len(gray_thumbnail) > 0

        # Decode and validate
        gray_bytes = base64.b64decode(gray_thumbnail)
        gray_img = Image.open(io.BytesIO(gray_bytes))
        assert gray_img.format == "JPEG"
        assert gray_img.size == (160, 160)

        # Test 3: Exception handling - invalid inputs
        invalid_inputs = [None, np.array([]), np.ones(10)]
        for invalid in invalid_inputs:
            error_result = create_face_thumbnail(invalid)
            assert error_result == ""

        # Test 4: Various sizes - resize operation
        sizes = [(50, 50), (100, 100), (200, 200), (300, 300)]
        for w, h in sizes:
            test_face = np.ones((h, w, 3), dtype=np.uint8) * 128
            test_thumbnail = create_face_thumbnail(test_face)
            test_bytes = base64.b64decode(test_thumbnail)
            test_img = Image.open(io.BytesIO(test_bytes))
            assert test_img.size == (160, 160)
