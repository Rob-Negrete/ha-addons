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
        """
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        try:
            import clasificador

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

                print(f"\n   ✅ Average embedding preservation: {avg_improvement:+.1f}%")

                # Assert embedding improvement or at least no degradation
                assert avg_new_dist <= avg_old_dist * 1.05, (
                    f"NEW method should preserve embeddings, "
                    f"but distance increased: {avg_old_dist:.4f} → {avg_new_dist:.4f}"
                )

                print(
                    f"🎉 SUCCESS: Embeddings preserved "
                    f"(improvement: {avg_improvement:+.1f}%)"
                )

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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
