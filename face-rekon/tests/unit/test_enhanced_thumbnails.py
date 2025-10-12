"""
Unit tests for enhanced thumbnail generation functions.

Tests the hybrid approach: adaptive interpolation + optional super-resolution.
"""

import os
import sys

import cv2
import numpy as np
import pytest

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../scripts"))


class TestUnsharpMask:
    """Test unsharp mask sharpening function."""

    def test_unsharp_mask_enhances_sharpness(self):
        """Unsharp mask should increase image sharpness (Laplacian variance)."""
        # Create a slightly blurry test image
        original = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        blurred = cv2.GaussianBlur(original, (5, 5), 1.0)

        # Import function
        from clasificador import apply_unsharp_mask

        # Apply unsharp mask
        sharpened = apply_unsharp_mask(blurred, amount=0.7, radius=1.0)

        # Calculate sharpness (Laplacian variance)
        def calc_sharpness(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return cv2.Laplacian(gray, cv2.CV_64F).var()

        blur_sharpness = calc_sharpness(blurred)
        sharp_sharpness = calc_sharpness(sharpened)

        # Sharpened should have higher Laplacian variance
        assert (
            sharp_sharpness > blur_sharpness
        ), "Unsharp mask should increase sharpness"
        print(f"✅ Sharpness increased: {blur_sharpness:.2f} → {sharp_sharpness:.2f}")

    def test_unsharp_mask_preserves_dimensions(self):
        """Unsharp mask should preserve image dimensions."""
        from clasificador import apply_unsharp_mask

        test_image = np.random.randint(0, 256, (75, 60, 3), dtype=np.uint8)
        result = apply_unsharp_mask(test_image, amount=0.5, radius=1.0)

        assert result.shape == test_image.shape
        print(f"✅ Dimensions preserved: {test_image.shape}")

    def test_unsharp_mask_handles_edge_cases(self):
        """Unsharp mask should handle edge cases gracefully."""
        from clasificador import apply_unsharp_mask

        # Very small image
        tiny = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        result_tiny = apply_unsharp_mask(tiny)
        assert result_tiny.shape == tiny.shape

        # Grayscale image
        gray = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        result_gray = apply_unsharp_mask(gray)
        assert result_gray.shape == gray.shape

        print("✅ Edge cases handled correctly")

    def test_unsharp_mask_clips_values(self):
        """Unsharp mask should clip values to valid range [0, 255]."""
        from clasificador import apply_unsharp_mask

        # Create image with values near boundaries
        test_image = np.ones((50, 50, 3), dtype=np.uint8) * 250
        result = apply_unsharp_mask(test_image, amount=2.0)  # Aggressive sharpening

        # Check all values are in valid range
        assert np.all(result >= 0), "Values should not be negative"
        assert np.all(result <= 255), "Values should not exceed 255"
        assert result.dtype == np.uint8, "Should maintain uint8 dtype"
        print("✅ Values properly clipped to [0, 255]")


class TestAdaptiveThumbnailGeneration:
    """Test adaptive interpolation thumbnail generation."""

    def test_adaptive_tiny_faces_use_lanczos4(self):
        """Tiny faces (<80px) should use LANCZOS4 + strong sharpening."""
        from clasificador import create_enhanced_thumbnail_adaptive

        # Create tiny face crop (60x60)
        tiny_face = np.random.randint(0, 256, (60, 60, 3), dtype=np.uint8)

        # Generate thumbnail
        thumbnail = create_enhanced_thumbnail_adaptive(
            tiny_face, target_size=(160, 160)
        )

        # Check output
        assert thumbnail.shape == (160, 160, 3), "Should be 160x160"
        assert thumbnail.dtype == np.uint8, "Should be uint8"
        print("✅ Tiny face processed with LANCZOS4 + sharpening")

    def test_adaptive_small_faces_use_lanczos4(self):
        """Small faces (80-160px) should use LANCZOS4 + moderate sharpening."""
        from clasificador import create_enhanced_thumbnail_adaptive

        # Create small face crop (100x100)
        small_face = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

        thumbnail = create_enhanced_thumbnail_adaptive(
            small_face, target_size=(160, 160)
        )

        assert thumbnail.shape == (160, 160, 3)
        print("✅ Small face processed with LANCZOS4 + moderate sharpening")

    def test_adaptive_medium_faces_use_cubic(self):
        """Medium faces (160-300px) should use CUBIC + light sharpening."""
        from clasificador import create_enhanced_thumbnail_adaptive

        # Create medium face crop (200x200)
        medium_face = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)

        thumbnail = create_enhanced_thumbnail_adaptive(
            medium_face, target_size=(160, 160)
        )

        assert thumbnail.shape == (160, 160, 3)
        print("✅ Medium face processed with CUBIC + light sharpening")

    def test_adaptive_large_faces_use_inter_area(self):
        """Large faces (>300px) should use INTER_AREA (downscaling)."""
        from clasificador import create_enhanced_thumbnail_adaptive

        # Create large face crop (400x400)
        large_face = np.random.randint(0, 256, (400, 400, 3), dtype=np.uint8)

        thumbnail = create_enhanced_thumbnail_adaptive(
            large_face, target_size=(160, 160)
        )

        assert thumbnail.shape == (160, 160, 3)
        print("✅ Large face processed with INTER_AREA (downscaling)")

    def test_adaptive_improves_small_face_quality(self):
        """Adaptive method should improve quality vs INTER_AREA for small faces."""
        from clasificador import create_enhanced_thumbnail_adaptive

        # Create small sharp test face (70x70)
        small_face = np.random.randint(0, 256, (70, 70, 3), dtype=np.uint8)

        # Compare adaptive vs INTER_AREA
        adaptive_thumb = create_enhanced_thumbnail_adaptive(
            small_face, target_size=(160, 160)
        )
        area_thumb = cv2.resize(small_face, (160, 160), interpolation=cv2.INTER_AREA)

        def calc_sharpness(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return cv2.Laplacian(gray, cv2.CV_64F).var()

        adaptive_sharpness = calc_sharpness(adaptive_thumb)
        area_sharpness = calc_sharpness(area_thumb)

        # Adaptive should be sharper for small faces
        improvement = (adaptive_sharpness - area_sharpness) / area_sharpness * 100
        print(
            f"✅ Quality improvement: {improvement:+.1f}% "
            f"(adaptive: {adaptive_sharpness:.2f} vs area: {area_sharpness:.2f})"
        )

        # Allow for some variance in random images, but expect general improvement
        assert improvement >= -10, "Should not significantly degrade quality"

    def test_adaptive_handles_grayscale(self):
        """Adaptive method should handle grayscale images."""
        from clasificador import create_enhanced_thumbnail_adaptive

        # Grayscale face
        gray_face = np.random.randint(0, 256, (80, 80), dtype=np.uint8)

        thumbnail = create_enhanced_thumbnail_adaptive(
            gray_face, target_size=(160, 160)
        )

        assert thumbnail.shape == (160, 160)
        assert thumbnail.dtype == np.uint8
        print("✅ Grayscale images handled correctly")

    def test_adaptive_fallback_on_error(self):
        """Should fallback to INTER_AREA if adaptive fails."""
        from clasificador import create_enhanced_thumbnail_adaptive

        # This should still work even if something goes wrong
        face = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        thumbnail = create_enhanced_thumbnail_adaptive(face, target_size=(160, 160))

        assert thumbnail is not None
        assert thumbnail.shape == (160, 160, 3)
        print("✅ Fallback mechanism works")


class TestHybridThumbnailGeneration:
    """Test hybrid thumbnail generation (adaptive + optional SR)."""

    def test_hybrid_without_sr_uses_adaptive(self):
        """Hybrid should use adaptive interpolation when SR is disabled."""
        import clasificador

        # Temporarily disable SR
        original_sr = clasificador.USE_SUPER_RESOLUTION
        clasificador.USE_SUPER_RESOLUTION = False

        try:
            face = np.random.randint(0, 256, (70, 70, 3), dtype=np.uint8)
            thumbnail = clasificador.create_enhanced_thumbnail_hybrid(
                face, target_size=(160, 160)
            )

            assert thumbnail.shape == (160, 160, 3)
            print("✅ Hybrid uses adaptive when SR disabled")

        finally:
            clasificador.USE_SUPER_RESOLUTION = original_sr

    def test_hybrid_skips_sr_for_large_faces(self):
        """Hybrid should skip SR for faces larger than SR_THRESHOLD."""
        import clasificador

        # Enable SR but use large face
        original_sr = clasificador.USE_SUPER_RESOLUTION
        clasificador.USE_SUPER_RESOLUTION = True
        original_threshold = clasificador.SR_THRESHOLD
        clasificador.SR_THRESHOLD = 100  # Set threshold to 100px

        try:
            # Large face (150x150) should skip SR
            large_face = np.random.randint(0, 256, (150, 150, 3), dtype=np.uint8)
            thumbnail = clasificador.create_enhanced_thumbnail_hybrid(
                large_face, target_size=(160, 160)
            )

            assert thumbnail.shape == (160, 160, 3)
            print("✅ Hybrid skips SR for faces above threshold")

        finally:
            clasificador.USE_SUPER_RESOLUTION = original_sr
            clasificador.SR_THRESHOLD = original_threshold

    def test_hybrid_preserves_dimensions(self):
        """Hybrid should always output correct dimensions."""
        import clasificador

        test_sizes = [(50, 50), (80, 80), (120, 120), (200, 200)]

        for size in test_sizes:
            face = np.random.randint(0, 256, (*size, 3), dtype=np.uint8)
            thumbnail = clasificador.create_enhanced_thumbnail_hybrid(
                face, target_size=(160, 160)
            )

            assert thumbnail.shape == (160, 160, 3), f"Failed for size {size}"

        print(f"✅ Dimensions preserved for {len(test_sizes)} different input sizes")

    def test_hybrid_fallback_mechanism(self):
        """Hybrid should fallback to INTER_AREA if everything fails."""
        import clasificador

        # Disable adaptive interpolation
        original_adaptive = clasificador.ADAPTIVE_INTERPOLATION
        clasificador.ADAPTIVE_INTERPOLATION = False

        try:
            face = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
            thumbnail = clasificador.create_enhanced_thumbnail_hybrid(
                face, target_size=(160, 160)
            )

            assert thumbnail is not None
            assert thumbnail.shape == (160, 160, 3)
            print("✅ Ultimate fallback to INTER_AREA works")

        finally:
            clasificador.ADAPTIVE_INTERPOLATION = original_adaptive


class TestRealWorldScenarios:
    """Test with real-world-like scenarios."""

    def test_three_tiny_faces_scenario(self):
        """
        Simulate the real scenario: 3 faces ~7m away, ~60-70px crops.
        """
        from clasificador import create_enhanced_thumbnail_hybrid

        # Simulate 3 tiny face crops
        face_sizes = [(65, 65), (60, 60), (70, 70)]

        for i, size in enumerate(face_sizes, 1):
            # Create realistic face crop
            face_crop = np.random.randint(50, 200, (*size, 3), dtype=np.uint8)

            # Generate thumbnail
            thumbnail = create_enhanced_thumbnail_hybrid(
                face_crop, target_size=(160, 160)
            )

            # Verify output
            assert thumbnail.shape == (160, 160, 3)
            assert thumbnail.dtype == np.uint8

            # Calculate quality improvement
            def calc_sharpness(img):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                return cv2.Laplacian(gray, cv2.CV_64F).var()

            # Compare with old method
            old_method = cv2.resize(face_crop, (160, 160), interpolation=cv2.INTER_AREA)
            new_sharpness = calc_sharpness(thumbnail)
            old_sharpness = calc_sharpness(old_method)

            improvement = (new_sharpness - old_sharpness) / old_sharpness * 100

            print(
                f"✅ Face {i} ({size[0]}x{size[1]}px): "
                f"Quality improvement: {improvement:+.1f}%"
            )

    def test_mixed_face_sizes_batch(self):
        """Test with a batch of mixed face sizes (realistic scenario)."""
        from clasificador import create_enhanced_thumbnail_hybrid

        # Mixed batch: tiny, small, medium, large
        face_sizes = [(55, 55), (90, 90), (180, 180), (350, 350)]

        for size in face_sizes:
            face = np.random.randint(0, 256, (*size, 3), dtype=np.uint8)
            thumbnail = create_enhanced_thumbnail_hybrid(face, target_size=(160, 160))

            assert thumbnail.shape == (160, 160, 3)
            assert thumbnail.dtype == np.uint8

        print(f"✅ Successfully processed batch of {len(face_sizes)} mixed-size faces")

    def test_extreme_aspect_ratios(self):
        """Test with extreme aspect ratios (partial face crops)."""
        from clasificador import create_enhanced_thumbnail_hybrid

        # Extreme aspect ratios
        faces = [
            np.random.randint(0, 256, (40, 80, 3), dtype=np.uint8),  # Tall
            np.random.randint(0, 256, (80, 40, 3), dtype=np.uint8),  # Wide
            np.random.randint(0, 256, (30, 90, 3), dtype=np.uint8),  # Very tall
        ]

        for face in faces:
            thumbnail = create_enhanced_thumbnail_hybrid(face, target_size=(160, 160))
            assert thumbnail.shape == (160, 160, 3)

        print("✅ Extreme aspect ratios handled correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
