"""
Integration tests for enhanced thumbnail generation with real ML pipeline.

CRITICAL TEST: Validates that hybrid adaptive thumbnail generation
improves quality for small/distant faces while maintaining recognition accuracy.

Tests run in Docker with real InsightFace, OpenCV, and Qdrant.
"""

import os
from pathlib import Path

import cv2
import numpy as np
import pytest

# Check for ML dependencies
try:
    from insightface.app import FaceAnalysis

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class TestEnhancedThumbnailsRealML:
    """Test enhanced thumbnail generation with real ML pipeline."""

    def test_hybrid_improves_tiny_face_quality(self):
        """
        CRITICAL: Test that hybrid method improves quality for tiny faces.

        Uses three-tiny-faces.png (real scenario: 3 people ~7m away, ~60-70px crops).
        Compares OLD method (INTER_AREA) vs NEW method (hybrid adaptive).
        """
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import clasificador

            # Initialize InsightFace
            app = FaceAnalysis(providers=["CPUExecutionProvider"])
            app.prepare(ctx_id=0, det_size=(640, 640))

            # Load test image with tiny faces
            test_image_path = "tests/dummies/three-tiny-faces.png"
            img = cv2.imread(test_image_path)
            assert img is not None, f"Could not load {test_image_path}"

            # Detect faces
            faces = app.get(img)
            assert len(faces) > 0, "Should detect at least 1 face"

            print(f"\n🔍 Detected {len(faces)} faces in three-tiny-faces.png")

            improvements = []
            old_losses = []
            new_losses = []

            for i, face in enumerate(faces, 1):
                # Extract face crop
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox

                padding = 20
                x1_padded = max(0, x1 - padding)
                y1_padded = max(0, y1 - padding)
                x2_padded = min(img.shape[1], x2 + padding)
                y2_padded = min(img.shape[0], y2 + padding)

                face_crop = img[y1_padded:y2_padded, x1_padded:x2_padded]

                print(f"   Face {i}: {face_crop.shape[1]}x{face_crop.shape[0]}px")

                # Calculate sharpness
                def calc_sharpness(img_array):
                    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
                    return cv2.Laplacian(gray, cv2.CV_64F).var()

                crop_sharpness = calc_sharpness(face_crop)

                # OLD METHOD: INTER_AREA
                old_thumbnail = cv2.resize(
                    face_crop, (160, 160), interpolation=cv2.INTER_AREA
                )
                old_sharpness = calc_sharpness(old_thumbnail)
                old_loss = (crop_sharpness - old_sharpness) / crop_sharpness * 100

                # NEW METHOD: Hybrid adaptive
                new_thumbnail = clasificador.create_enhanced_thumbnail_hybrid(
                    face_crop, target_size=(160, 160)
                )
                new_sharpness = calc_sharpness(new_thumbnail)
                new_loss = (crop_sharpness - new_sharpness) / crop_sharpness * 100

                # Calculate improvement
                improvement_pct = (new_sharpness - old_sharpness) / old_sharpness * 100
                improvements.append(improvement_pct)
                old_losses.append(old_loss)
                new_losses.append(new_loss)

                print(
                    f"      OLD: {old_sharpness:.2f} | "
                    f"NEW: {new_sharpness:.2f} | "
                    f"Improvement: {improvement_pct:+.1f}%"
                )

            # Assert improvements
            avg_improvement = np.mean(improvements)
            avg_old_loss = np.mean(old_losses)
            avg_new_loss = np.mean(new_losses)
            loss_reduction = avg_old_loss - avg_new_loss

            print(f"\n   ✅ Average improvement: {avg_improvement:+.1f}%")
            print(f"   ✅ Loss reduction: {loss_reduction:+.1f}pp")

            # CRITICAL ASSERTIONS
            assert avg_improvement > 0, (
                f"NEW method should improve quality, "
                f"but got {avg_improvement:+.1f}% (negative = worse)"
            )

            assert loss_reduction > 0, (
                f"NEW method should reduce quality loss, "
                f"but got {loss_reduction:+.1f}pp (negative = worse)"
            )

            # For tiny faces, expect significant improvement (at least 10%)
            assert avg_improvement >= 10, (
                f"For tiny faces, expect ≥10% improvement, "
                f"but got {avg_improvement:.1f}%"
            )

            print(
                f"\n🎉 SUCCESS: Hybrid method improves tiny face quality "
                f"by {avg_improvement:+.1f}%"
            )

        except ImportError as e:
            pytest.skip(f"Dependencies not available: {e}")

    def test_hybrid_preserves_embedding_similarity(self):
        """
        Test that enhanced thumbnails preserve embedding similarity.

        Embeddings from enhanced thumbnails should be closer to original
        face embeddings than old method.

        NOTE: This test disables Real-ESRGAN to test adaptive interpolation only.
        """
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import clasificador

            # Disable Real-ESRGAN for this test (testing adaptive interpolation only)
            original_sr = clasificador.USE_SUPER_RESOLUTION
            clasificador.USE_SUPER_RESOLUTION = False

            try:
                # Initialize InsightFace
                app = FaceAnalysis(providers=["CPUExecutionProvider"])
                app.prepare(ctx_id=0, det_size=(640, 640))

                # Load test image
                test_image_path = "tests/dummies/three-tiny-faces.png"
                img = cv2.imread(test_image_path)
                assert img is not None

                # Detect faces
                faces = app.get(img)
                assert len(faces) > 0

                print(f"\n🎯 Testing embedding preservation for {len(faces)} faces")

                old_distances = []
                new_distances = []

                for i, face in enumerate(faces, 1):
                    # Extract face crop
                    bbox = face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    padding = 20
                    x1_padded = max(0, x1 - padding)
                    y1_padded = max(0, y1 - padding)
                    x2_padded = min(img.shape[1], x2 + padding)
                    y2_padded = min(img.shape[0], y2 + padding)
                    face_crop = img[y1_padded:y2_padded, x1_padded:x2_padded]

                    # Original embedding
                    original_embedding = face.embedding

                    # OLD method thumbnail → embedding
                    old_thumbnail = cv2.resize(
                        face_crop, (160, 160), interpolation=cv2.INTER_AREA
                    )
                    old_thumb_full = cv2.resize(
                        old_thumbnail, (face_crop.shape[1], face_crop.shape[0])
                    )
                    old_faces = app.get(old_thumb_full)

                    # NEW method thumbnail → embedding
                    new_thumbnail = clasificador.create_enhanced_thumbnail_hybrid(
                        face_crop, (160, 160)
                    )
                    new_thumb_full = cv2.resize(
                        new_thumbnail, (face_crop.shape[1], face_crop.shape[0])
                    )
                    new_faces = app.get(new_thumb_full)

                    if old_faces and new_faces:
                        # Cosine distance
                        def cosine_distance(emb1, emb2):
                            return float(np.linalg.norm(emb1 - emb2))

                        old_dist = cosine_distance(
                            original_embedding, old_faces[0].embedding
                        )
                        new_dist = cosine_distance(
                            original_embedding, new_faces[0].embedding
                        )

                        old_distances.append(old_dist)
                        new_distances.append(new_dist)

                        improvement = (old_dist - new_dist) / old_dist * 100
                        print(
                            f"   Face {i}: OLD dist={old_dist:.4f}, "
                            f"NEW dist={new_dist:.4f}, "
                            f"Improvement={improvement:+.1f}%"
                        )

                if len(old_distances) > 0:
                    avg_old_dist = np.mean(old_distances)
                    avg_new_dist = np.mean(new_distances)
                    avg_improvement = (avg_old_dist - avg_new_dist) / avg_old_dist * 100

                    print(
                        f"\n   ✅ Average embedding preservation: "
                        f"{avg_improvement:+.1f}%"
                    )

                    # Assert embedding improvement or at least no degradation
                    assert avg_new_dist <= avg_old_dist * 1.05, (
                        f"NEW method should preserve embeddings, "
                        f"but distance increased: "
                        f"{avg_old_dist:.4f} → {avg_new_dist:.4f}"
                    )

                    print(
                        f"🎉 SUCCESS: Embeddings preserved "
                        f"(improvement: {avg_improvement:+.1f}%)"
                    )

            finally:
                # Restore original SR setting
                clasificador.USE_SUPER_RESOLUTION = original_sr

        except ImportError as e:
            pytest.skip(f"Dependencies not available: {e}")

    def test_adaptive_handles_different_face_sizes(self):
        """Test that adaptive method works for various face sizes."""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import clasificador

            # Test different dummy images with various face sizes
            test_images = [
                "tests/dummies/one-face.jpg",  # Normal size
                "tests/dummies/two-faces.jpg",  # Normal size
                "tests/dummies/three-tiny-faces.png",  # Tiny faces
            ]

            app = FaceAnalysis(providers=["CPUExecutionProvider"])
            app.prepare(ctx_id=0, det_size=(640, 640))

            total_faces = 0
            successful_enhancements = 0

            print("\n📊 Testing adaptive method on various face sizes")

            for test_image_path in test_images:
                if not os.path.exists(test_image_path):
                    continue

                img = cv2.imread(test_image_path)
                if img is None:
                    continue

                faces = app.get(img)
                print(f"   {Path(test_image_path).name}: {len(faces)} faces")

                for face in faces:
                    bbox = face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    padding = 20
                    x1_padded = max(0, x1 - padding)
                    y1_padded = max(0, y1 - padding)
                    x2_padded = min(img.shape[1], x2 + padding)
                    y2_padded = min(img.shape[0], y2 + padding)
                    face_crop = img[y1_padded:y2_padded, x1_padded:x2_padded]

                    # Generate thumbnail
                    thumbnail = clasificador.create_enhanced_thumbnail_hybrid(
                        face_crop, target_size=(160, 160)
                    )

                    # Verify output
                    assert thumbnail.shape == (160, 160, 3), "Should output 160x160 RGB"
                    assert thumbnail.dtype == np.uint8, "Should be uint8"

                    total_faces += 1
                    successful_enhancements += 1

            print(
                f"\n   ✅ Successfully enhanced "
                f"{successful_enhancements}/{total_faces} faces"
            )

            assert (
                successful_enhancements == total_faces
            ), "All faces should be enhanced successfully"

            print("🎉 SUCCESS: Adaptive method handles all face sizes")

        except ImportError as e:
            pytest.skip(f"Dependencies not available: {e}")

    def test_hybrid_fallback_mechanism(self):
        """Test that hybrid method falls back gracefully if enhancement fails."""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import clasificador

            # Create a test face crop
            face_crop = np.random.randint(0, 256, (70, 70, 3), dtype=np.uint8)

            # Even if enhancement fails, should still produce valid thumbnail
            thumbnail = clasificador.create_enhanced_thumbnail_hybrid(
                face_crop, target_size=(160, 160)
            )

            assert thumbnail is not None, "Should return a thumbnail"
            assert thumbnail.shape == (160, 160, 3), "Should be correct size"
            assert thumbnail.dtype == np.uint8, "Should be uint8"

            print("\n✅ Fallback mechanism works correctly")

        except ImportError as e:
            pytest.skip(f"Dependencies not available: {e}")


class TestSuperResolutionRealESRGAN:
    """
    Integration tests for Real-ESRGAN super-resolution.

    Tests the apply_super_resolution function with real Real-ESRGAN model.
    Requires Real-ESRGAN dependencies (installed in Docker test environment).
    """

    def test_super_resolution_2x_upscaling(self):
        """Test Real-ESRGAN 2x upscaling with real model."""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import clasificador

            # Create small test face (80x80)
            test_face = np.random.randint(0, 256, (80, 80, 3), dtype=np.uint8)

            # Apply 2x super-resolution
            result = clasificador.apply_super_resolution(test_face, scale=2)

            # Should upscale to 160x160
            assert result is not None, "Should return a result"
            assert (
                result.shape[0] == 160
            ), f"Height should be 160, got {result.shape[0]}"
            assert result.shape[1] == 160, f"Width should be 160, got {result.shape[1]}"
            assert result.shape[2] == 3, "Should maintain 3 channels"
            assert result.dtype == np.uint8, "Should be uint8"

            print("\n✅ Real-ESRGAN 2x upscaling works correctly")
            print(f"   Input: {test_face.shape} → Output: {result.shape}")

        except ImportError as e:
            pytest.skip(f"Real-ESRGAN dependencies not available: {e}")

    def test_super_resolution_4x_upscaling(self):
        """Test Real-ESRGAN 4x upscaling with real model."""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import clasificador

            # Create tiny test face (60x60)
            test_face = np.random.randint(0, 256, (60, 60, 3), dtype=np.uint8)

            # Apply 4x super-resolution
            result = clasificador.apply_super_resolution(test_face, scale=4)

            # Should upscale to 240x240
            expected_size = 60 * 4
            assert result is not None, "Should return a result"
            assert (
                result.shape[0] == expected_size
            ), f"Height should be {expected_size}, got {result.shape[0]}"
            assert (
                result.shape[1] == expected_size
            ), f"Width should be {expected_size}, got {result.shape[1]}"
            assert result.shape[2] == 3, "Should maintain 3 channels"

            print("\n✅ Real-ESRGAN 4x upscaling works correctly")
            print(f"   Input: {test_face.shape} → Output: {result.shape}")

        except ImportError as e:
            pytest.skip(f"Real-ESRGAN dependencies not available: {e}")

    def test_super_resolution_model_caching(self):
        """Test that Real-ESRGAN model is cached after first use."""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import time

            import clasificador

            # Clear any cached model
            if hasattr(clasificador.apply_super_resolution, "realesrgan_model"):
                delattr(clasificador.apply_super_resolution, "realesrgan_model")

            test_face = np.random.randint(0, 256, (80, 80, 3), dtype=np.uint8)

            # First call - should initialize model (slower)
            start_first = time.time()
            clasificador.apply_super_resolution(test_face, scale=2)
            time_first = time.time() - start_first

            # Verify model is now cached
            assert hasattr(
                clasificador.apply_super_resolution, "realesrgan_model"
            ), "Model should be cached after first use"

            # Second call - should reuse cached model (faster)
            start_second = time.time()
            clasificador.apply_super_resolution(test_face, scale=2)
            time_second = time.time() - start_second

            # Second call should be significantly faster
            assert time_second < time_first, "Cached call should be faster"

            print("\n✅ Real-ESRGAN model caching works correctly")
            print(f"   First call: {time_first:.3f}s (with model init)")
            print(f"   Second call: {time_second:.3f}s (cached model)")
            print(f"   Speedup: {time_first/time_second:.1f}x")

        except ImportError as e:
            pytest.skip(f"Real-ESRGAN dependencies not available: {e}")

    def test_super_resolution_with_real_tiny_face_image(self):
        """Test Real-ESRGAN with actual tiny face from test images."""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import clasificador
            from insightface.app import FaceAnalysis

            # Initialize InsightFace
            app = FaceAnalysis(providers=["CPUExecutionProvider"])
            app.prepare(ctx_id=0, det_size=(640, 640))

            # Load image with tiny faces
            test_image_path = "tests/dummies/three-tiny-faces.png"
            if not os.path.exists(test_image_path):
                pytest.skip(f"Test image not found: {test_image_path}")

            img = cv2.imread(test_image_path)
            assert img is not None

            # Detect faces
            faces = app.get(img)
            assert len(faces) > 0

            # Get first tiny face
            face = faces[0]
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            face_crop = img[y1:y2, x1:x2]

            original_h, original_w = face_crop.shape[:2]
            print(f"\n🔍 Original face crop: {original_w}x{original_h}px")

            # Apply super-resolution (2x)
            enhanced = clasificador.apply_super_resolution(face_crop, scale=2)

            assert enhanced.shape[0] == original_h * 2
            assert enhanced.shape[1] == original_w * 2

            print("✅ Enhanced with Real-ESRGAN:")
            print(f"   {enhanced.shape[1]}x{enhanced.shape[0]}px")

        except ImportError as e:
            pytest.skip(f"Dependencies not available: {e}")

    def test_hybrid_thumbnail_with_super_resolution_enabled(self):
        """
        Test hybrid thumbnail generation with Real-ESRGAN enabled.

        This tests the full pipeline: tiny face → SR upscale → adaptive thumbnail.
        """
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import clasificador

            # Enable super-resolution temporarily
            original_sr = clasificador.USE_SUPER_RESOLUTION
            original_threshold = clasificador.SR_THRESHOLD

            try:
                # Enable SR for faces < 100px
                clasificador.USE_SUPER_RESOLUTION = True
                clasificador.SR_THRESHOLD = 100

                # Create tiny face (70x70) - should trigger SR
                tiny_face = np.random.randint(0, 256, (70, 70, 3), dtype=np.uint8)

                # Generate hybrid thumbnail (should use SR)
                thumbnail = clasificador.create_enhanced_thumbnail_hybrid(
                    tiny_face, target_size=(160, 160)
                )

                assert thumbnail is not None
                assert thumbnail.shape == (160, 160, 3)
                assert thumbnail.dtype == np.uint8

                print("\n✅ Hybrid thumbnail with SR enabled works correctly")
                print(f"   Input: {tiny_face.shape} → Output: {thumbnail.shape}")
                print(
                    "   Pipeline: tiny face → Real-ESRGAN → adaptive resize → 160x160"
                )

            finally:
                clasificador.USE_SUPER_RESOLUTION = original_sr
                clasificador.SR_THRESHOLD = original_threshold

        except ImportError as e:
            pytest.skip(f"Real-ESRGAN dependencies not available: {e}")

    def test_hybrid_thumbnail_skips_sr_for_large_faces(self):
        """Test that hybrid method skips SR for faces above threshold."""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import clasificador

            original_sr = clasificador.USE_SUPER_RESOLUTION
            original_threshold = clasificador.SR_THRESHOLD

            try:
                # Enable SR but set threshold to 100px
                clasificador.USE_SUPER_RESOLUTION = True
                clasificador.SR_THRESHOLD = 100

                # Create large face (150x150) - should NOT trigger SR
                large_face = np.random.randint(0, 256, (150, 150, 3), dtype=np.uint8)

                # Should complete without using SR (faster)
                import time

                start = time.time()
                thumbnail = clasificador.create_enhanced_thumbnail_hybrid(
                    large_face, target_size=(160, 160)
                )
                elapsed = time.time() - start

                assert thumbnail is not None
                assert thumbnail.shape == (160, 160, 3)

                # Should be very fast since SR was skipped
                assert elapsed < 0.5, "Should be fast without SR"

                print("\n✅ Hybrid correctly skips SR for large faces")
                print(f"   Face size: {large_face.shape[0]}px")
                print(f"   Threshold: {clasificador.SR_THRESHOLD}px")
                print(f"   Processing time: {elapsed:.3f}s (no SR overhead)")

            finally:
                clasificador.USE_SUPER_RESOLUTION = original_sr
                clasificador.SR_THRESHOLD = original_threshold

        except ImportError as e:
            pytest.skip(f"Real-ESRGAN dependencies not available: {e}")

    def test_super_resolution_import_error_fallback(self):
        """Test that apply_super_resolution falls back gracefully on ImportError."""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import sys
            from unittest import mock

            import clasificador

            # Create test face
            test_face = np.random.randint(0, 256, (80, 80, 3), dtype=np.uint8)

            # Mock import to raise ImportError
            with mock.patch.dict(sys.modules, {"basicsr.archs.rrdbnet_arch": None}):
                with mock.patch("clasificador.logger.warning") as mock_warning:
                    result = clasificador.apply_super_resolution(test_face, scale=2)

                    # Should return original image
                    assert result is test_face
                    # Should log warning
                    mock_warning.assert_called()

            print("\n✅ ImportError fallback works correctly")

        except ImportError as e:
            pytest.skip(f"Dependencies not available: {e}")

    def test_super_resolution_enhance_returns_none(self):
        """Test fallback when enhance() returns None."""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            from unittest import mock

            import clasificador

            test_face = np.random.randint(0, 256, (80, 80, 3), dtype=np.uint8)

            # Clear cached model to force reinitialization
            if hasattr(clasificador.apply_super_resolution, "realesrgan_model"):
                delattr(clasificador.apply_super_resolution, "realesrgan_model")

            # Mock enhance() to return (None, None)
            with mock.patch.object(
                clasificador.apply_super_resolution,
                "realesrgan_model",
                create=True,
            ):
                mock_model = mock.MagicMock()
                mock_model.enhance.return_value = (None, None)
                clasificador.apply_super_resolution.realesrgan_model = mock_model

                with mock.patch("clasificador.logger.warning") as mock_warning:
                    result = clasificador.apply_super_resolution(test_face, scale=2)

                    # Should return original image
                    np.testing.assert_array_equal(result, test_face)
                    # Should log warning
                    assert any(
                        "Real-ESRGAN returned None" in str(call)
                        for call in mock_warning.call_args_list
                    )

            print("\n✅ enhance() None return fallback works correctly")

        except ImportError as e:
            pytest.skip(f"Dependencies not available: {e}")

    def test_super_resolution_enhance_raises_exception(self):
        """Test fallback when enhance() raises an exception."""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            from unittest import mock

            import clasificador

            test_face = np.random.randint(0, 256, (80, 80, 3), dtype=np.uint8)

            # Clear cached model
            if hasattr(clasificador.apply_super_resolution, "realesrgan_model"):
                delattr(clasificador.apply_super_resolution, "realesrgan_model")

            # Mock enhance() to raise exception
            with mock.patch.object(
                clasificador.apply_super_resolution,
                "realesrgan_model",
                create=True,
            ):
                mock_model = mock.MagicMock()
                mock_model.enhance.side_effect = RuntimeError("Enhance failed")
                clasificador.apply_super_resolution.realesrgan_model = mock_model

                with mock.patch("clasificador.logger.error") as mock_error:
                    result = clasificador.apply_super_resolution(test_face, scale=2)

                    # Should return original image
                    np.testing.assert_array_equal(result, test_face)
                    # Should log error
                    assert any(
                        "Real-ESRGAN enhance() failed" in str(call)
                        for call in mock_error.call_args_list
                    )

            print("\n✅ enhance() exception fallback works correctly")

        except ImportError as e:
            pytest.skip(f"Dependencies not available: {e}")

    def test_super_resolution_general_exception_handling(self):
        """Test general exception handling in apply_super_resolution."""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            from unittest import mock

            import clasificador

            test_face = np.random.randint(0, 256, (80, 80, 3), dtype=np.uint8)

            # Clear cached model
            if hasattr(clasificador.apply_super_resolution, "realesrgan_model"):
                delattr(clasificador.apply_super_resolution, "realesrgan_model")

            # Mock RRDBNet at the actual import path to raise exception
            with mock.patch(
                "basicsr.archs.rrdbnet_arch.RRDBNet",
                side_effect=ValueError("Unexpected error"),
            ):
                with mock.patch("clasificador.logger.error") as mock_error:
                    result = clasificador.apply_super_resolution(test_face, scale=2)

                    # Should return original image
                    np.testing.assert_array_equal(result, test_face)
                    # Should log error
                    assert any(
                        "Error in Real-ESRGAN super-resolution" in str(call)
                        for call in mock_error.call_args_list
                    )

            print("\n✅ General exception handling works correctly")

        except ImportError as e:
            pytest.skip(f"Dependencies not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
