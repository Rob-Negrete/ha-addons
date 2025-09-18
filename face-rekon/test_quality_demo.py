#!/usr/bin/env python3
"""
Demo script to show face quality filtering in action.
This demonstrates how the system filters out low-quality faces.
"""

import os
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))


def mock_face_quality_demo():
    """Demonstrate face quality filtering with mock data"""

    # Mock face quality metrics for different scenarios
    test_scenarios = [
        {
            "name": "High Quality Face (Good lighting, clear, large)",
            "metrics": {
                "size_score": 0.85,  # Large face in image
                "blur_score": 0.92,  # Very sharp/clear
                "detection_score": 0.95,  # High confidence detection
                "overall_score": 0.89,  # Excellent overall
            },
            "should_pass": True,
        },
        {
            "name": "Medium Quality Face (Acceptable)",
            "metrics": {
                "size_score": 0.60,  # Medium size
                "blur_score": 0.65,  # Slightly soft but OK
                "detection_score": 0.80,  # Good detection
                "overall_score": 0.68,  # Acceptable
            },
            "should_pass": True,
        },
        {
            "name": "Low Quality Face (Very Blurry - like snapshot.jpg)",
            "metrics": {
                "size_score": 0.40,  # Small face
                "blur_score": 0.08,  # Very blurry (like your snapshot.jpg)
                "detection_score": 0.55,  # Low confidence
                "overall_score": 0.22,  # Poor overall quality
            },
            "should_pass": False,
        },
        {
            "name": "Tiny Face (Too small to be useful)",
            "metrics": {
                "size_score": 0.05,  # Very small
                "blur_score": 0.70,  # Clear but tiny
                "detection_score": 0.40,  # Low confidence due to size
                "overall_score": 0.18,  # Poor due to size
            },
            "should_pass": False,
        },
        {
            "name": "False Positive (Not really a face)",
            "metrics": {
                "size_score": 0.30,  # Medium size
                "blur_score": 0.50,  # OK sharpness
                "detection_score": 0.25,  # Very low detection confidence
                "overall_score": 0.28,  # Poor overall
            },
            "should_pass": False,
        },
    ]

    # Quality threshold (from environment or default)
    quality_threshold = float(os.environ.get("FACE_REKON_MIN_QUALITY_SCORE", "0.3"))

    print("=== Face Quality Filtering Demo ===")
    print(f"Quality threshold: {quality_threshold}")
    print(f"Faces must score >= {quality_threshold} to be accepted\n")

    passed_faces = 0
    filtered_faces = 0

    for scenario in test_scenarios:
        name = scenario["name"]
        metrics = scenario["metrics"]
        expected_pass = scenario["should_pass"]

        overall_score = metrics["overall_score"]
        will_pass = overall_score >= quality_threshold

        # Status indicator
        status = "✅ ACCEPTED" if will_pass else "❌ FILTERED"

        print(f"{status} - {name}")
        print(f"  Overall Score: {overall_score:.3f}")
        print(
            f"  └─ Size: {metrics['size_score']:.3f} | "
            f"Blur: {metrics['blur_score']:.3f} | "
            f"Detection: {metrics['detection_score']:.3f}"
        )

        if will_pass != expected_pass:
            print(
                f"  ⚠️  Unexpected result! Expected: {expected_pass}, "
                f"Got: {will_pass}"
            )

        if will_pass:
            passed_faces += 1
        else:
            filtered_faces += 1
            # Explain why it was filtered
            if metrics["blur_score"] < 0.3:
                print(
                    f"  📝 Reason: Very blurry image (blur score: {metrics['blur_score']:.3f})"
                )
            elif metrics["size_score"] < 0.2:
                print(
                    f"  📝 Reason: Face too small (size score: {metrics['size_score']:.3f})"
                )
            elif metrics["detection_score"] < 0.3:
                print(
                    f"  📝 Reason: Low detection confidence (score: {metrics['detection_score']:.3f})"
                )

        print()

    print("Summary:")
    print(f"  Faces processed: {len(test_scenarios)}")
    print(f"  Faces accepted: {passed_faces}")
    print(f"  Faces filtered: {filtered_faces}")
    print(f"  Filter rate: {(filtered_faces / len(test_scenarios)) * 100:.1f}%")

    print("\n🎯 This explains why your very blurry snapshot.jpg would be filtered out!")
    print(
        "   The system prevents storing unusable face crops that hurt "
        "identification accuracy."
    )


if __name__ == "__main__":
    mock_face_quality_demo()
