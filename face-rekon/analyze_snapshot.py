#!/usr/bin/env python3
"""
Analysis of snapshot.jpg based on visual inspection.
This simulates what the quality assessment would show for your actual image.
"""


def analyze_snapshot_jpg():
    """Analyze the quality characteristics of snapshot.jpg"""

    print("=== Analizando snapshot.jpg ===")
    print("Image characteristics observed:")
    print("- Security camera footage with timestamp")
    print("- Person detected with bounding box (84% confidence)")
    print("- Distant view of person in courtyard")
    print("- Motion blur visible")
    print("- Low resolution/compressed image")

    # Estimated image dimensions (typical security camera)
    image_width = 1920  # Assuming 1080p security camera
    image_height = 1080
    image_area = image_width * image_height

    # Estimated face bounding box from visual inspection
    # The person appears to be roughly 120x300 pixels in the frame
    # Face would be approximately the top 1/4 of that
    estimated_face_bbox = [
        950,
        400,
        1020,
        500,
    ]  # Rough estimate based on person position
    face_width = estimated_face_bbox[2] - estimated_face_bbox[0]  # ~70 pixels
    face_height = estimated_face_bbox[3] - estimated_face_bbox[1]  # ~100 pixels
    face_area = face_width * face_height

    print("\nEstimated face characteristics:")
    print(f"- Face size: ~{face_width}x{face_height} pixels")
    print(f"- Face area: {face_area} pixels")
    print(f"- Image area: {image_area} pixels")
    print(f"- Face/Image ratio: {(face_area/image_area)*100:.3f}%")

    # Quality score calculations based on thresholds
    MIN_FACE_SIZE = 50
    MIN_BLUR_THRESHOLD = 50.0
    MIN_DETECTION_CONFIDENCE = 0.5
    MIN_QUALITY_SCORE = 0.3

    # 1. Size Score
    size_ratio = face_area / image_area
    size_score = min(1.0, size_ratio / 0.02)  # 2% of image = perfect score
    min_dimension = min(face_width, face_height)
    if min_dimension < MIN_FACE_SIZE:
        size_score *= min_dimension / MIN_FACE_SIZE

    # 2. Blur Score (estimated based on visual inspection)
    # The image shows clear motion blur and compression artifacts
    estimated_laplacian_variance = 15.0  # Very low for blurry/compressed image
    blur_score = min(1.0, estimated_laplacian_variance / MIN_BLUR_THRESHOLD)

    # 3. Detection Score (from the 84% shown in image)
    detection_score = 0.84  # As shown in the image annotation

    # 4. Overall Score
    overall_score = (size_score * 0.3) + (blur_score * 0.4) + (detection_score * 0.3)

    print("\n=== QUALITY ASSESSMENT RESULTS ===")
    print(f"Size Score: {size_score:.3f}")
    print(f"  └─ Face area ratio: {(face_area/image_area)*100:.3f}% (target: ≥2%)")
    print(f"  └─ Minimum dimension: {min_dimension}px (target: ≥{MIN_FACE_SIZE}px)")

    print(f"Blur Score: {blur_score:.3f}")
    print(
        f"  └─ Estimated Laplacian variance: {estimated_laplacian_variance} "
        f"(target: ≥{MIN_BLUR_THRESHOLD})"
    )
    print("  └─ Reason: Motion blur + compression artifacts visible")

    print(f"Detection Score: {detection_score:.3f}")
    print("  └─ InsightFace confidence: 84% (from image annotation)")

    print(f"\nOVERALL SCORE: {overall_score:.3f}")
    print(f"Quality Threshold: {MIN_QUALITY_SCORE}")

    if overall_score >= MIN_QUALITY_SCORE:
        print("✅ RESULT: ACCEPTED - Face would be stored")
    else:
        print("❌ RESULT: FILTERED - Face would be rejected")

        # Explain why it failed
        print("\n📝 REJECTION REASONS:")
        if blur_score < 0.3:
            print(f"   • Very blurry image (blur score: {blur_score:.3f})")
        if size_score < 0.5:
            print(f"   • Small face relative to image (size score: {size_score:.3f})")
        if detection_score < MIN_DETECTION_CONFIDENCE:
            print(f"   • Low detection confidence (score: {detection_score:.3f})")

    print("\n🎯 IMPACT:")
    if overall_score < MIN_QUALITY_SCORE:
        print("   This prevents storing a blurry, distant face crop that would be")
        print("   unusable for identification. The system protects data quality!")
    else:
        print("   This face would be stored and could be used for identification.")

    return overall_score


if __name__ == "__main__":
    analyze_snapshot_jpg()
