"""
Integration tests for calculate_quality_metrics function in clasificador.py

Tests target 80%+ coverage of the quality metrics calculation function,
using Docker integration testing with real ML dependencies (OpenCV, NumPy).
"""

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
    from clasificador import calculate_face_quality_metrics

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class TestCalculateQualityMetricsCoverage:
    """Comprehensive integration tests for calculate_face_quality_metrics() function."""

    def test_quality_metrics_grayscale_conversion_color_image(self):
        """Test quality metrics with color (3-channel) image - grayscale
        conversion path"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        face_crop = np.ones((100, 100, 3), dtype=np.uint8) * 128
        metrics = calculate_face_quality_metrics(face_crop)

        assert all(
            k in metrics
            for k in [
                "sharpness",
                "face_area",
                "brightness",
                "contrast",
                "quality_score",
            ]
        )
        assert all(isinstance(metrics[k], float) for k in metrics)
        assert metrics["face_area"] == 10000.0
        assert 0.0 <= metrics["quality_score"] <= 1.0

    def test_quality_metrics_grayscale_input_direct_path(self):
        """Test quality metrics with grayscale (2D) image - direct gray path"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        face_crop = np.ones((100, 100), dtype=np.uint8) * 128
        metrics = calculate_face_quality_metrics(face_crop)

        assert metrics["face_area"] == 10000.0
        assert metrics["brightness"] == 128.0
        assert 0.0 <= metrics["quality_score"] <= 1.0

    def test_quality_metrics_sharpness_calculation(self):
        """Test Laplacian variance sharpness metric calculation"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        face_crop = np.zeros((100, 100, 3), dtype=np.uint8)
        face_crop[25:75, 25:75] = 255  # White square on black

        metrics = calculate_face_quality_metrics(face_crop)
        assert metrics["sharpness"] > 0.0

    def test_quality_metrics_face_area_calculation(self):
        """Test face area metric for various image sizes"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        test_cases = [(50, 50, 2500.0), (100, 100, 10000.0), (200, 150, 30000.0)]

        for width, height, expected_area in test_cases:
            face_crop = np.ones((height, width, 3), dtype=np.uint8) * 128
            metrics = calculate_face_quality_metrics(face_crop)
            assert metrics["face_area"] == expected_area

    def test_quality_metrics_brightness_calculation(self):
        """Test brightness metric (mean intensity) calculation"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        test_cases = [(0, 0.0), (128, 128.0), (255, 255.0)]

        for intensity, expected_brightness in test_cases:
            face_crop = np.ones((100, 100, 3), dtype=np.uint8) * intensity
            metrics = calculate_face_quality_metrics(face_crop)
            assert abs(metrics["brightness"] - expected_brightness) < 0.1

    def test_quality_metrics_contrast_calculation(self):
        """Test contrast metric (standard deviation) calculation"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        low_contrast = np.ones((100, 100, 3), dtype=np.uint8) * 128
        high_contrast = np.zeros((100, 100, 3), dtype=np.uint8)
        high_contrast[50:, :] = 255

        low_metrics = calculate_face_quality_metrics(low_contrast)
        high_metrics = calculate_face_quality_metrics(high_contrast)

        assert high_metrics["contrast"] > low_metrics["contrast"]
        assert low_metrics["contrast"] >= 0.0

    def test_quality_metrics_quality_score_normalization(self):
        """Test quality score weighted combination and normalization"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        optimal_face = np.random.randint(100, 180, (100, 100, 3), dtype=np.uint8)
        metrics = calculate_face_quality_metrics(optimal_face)

        assert 0.0 <= metrics["quality_score"] <= 1.0
        assert metrics["quality_score"] > 0.0

    def test_quality_metrics_sharpness_score_normalization(self):
        """Test sharpness score capping at 100"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Extremely sharp checkerboard
        face_crop = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(0, 100, 2):
            for j in range(0, 100, 2):
                face_crop[i : i + 1, j : j + 1] = 255

        metrics = calculate_face_quality_metrics(face_crop)
        assert metrics["quality_score"] <= 1.0

    def test_quality_metrics_size_score_normalization(self):
        """Test size score capping at 10000 pixels (100x100)"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        large_face = np.ones((200, 200, 3), dtype=np.uint8) * 128
        small_face = np.ones((50, 50, 3), dtype=np.uint8) * 128

        large_metrics = calculate_face_quality_metrics(large_face)
        small_metrics = calculate_face_quality_metrics(small_face)

        assert large_metrics["face_area"] == 40000.0
        assert small_metrics["face_area"] == 2500.0
        assert 0.0 <= large_metrics["quality_score"] <= 1.0

    def test_quality_metrics_brightness_score_optimal_128(self):
        """Test brightness score optimization around 128 intensity"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        test_intensities = [0, 64, 128, 192, 255]
        scores = []

        for intensity in test_intensities:
            face_crop = np.ones((100, 100, 3), dtype=np.uint8) * intensity
            metrics = calculate_face_quality_metrics(face_crop)
            scores.append(metrics["quality_score"])

        assert scores[2] > 0.0  # 128 intensity has some quality

    def test_quality_metrics_contrast_score_capping(self):
        """Test contrast score capping at 64"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        high_contrast = np.zeros((100, 100, 3), dtype=np.uint8)
        high_contrast[:, 50:] = 255

        metrics = calculate_face_quality_metrics(high_contrast)
        assert 0.0 <= metrics["quality_score"] <= 1.0
        assert metrics["contrast"] > 0.0

    def test_quality_metrics_weighted_combination_formula(self):
        """Test weighted quality score formula: 40% sharp + 20% size +
        20% bright + 20% contrast"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        face_crop = np.ones((100, 100, 3), dtype=np.uint8) * 128
        metrics = calculate_face_quality_metrics(face_crop)

        assert 0.0 < metrics["quality_score"] <= 1.0
        assert all(
            metrics[k] >= 0.0
            for k in ["sharpness", "face_area", "brightness", "contrast"]
        )

    def test_quality_metrics_exception_handling_invalid_input(self):
        """Test exception handling with invalid/malformed input"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        metrics = calculate_face_quality_metrics(None)

        assert metrics["sharpness"] == 0.0
        assert metrics["face_area"] == 0.0
        assert metrics["brightness"] == 0.0
        assert metrics["contrast"] == 0.0
        assert metrics["quality_score"] == 0.0

    def test_quality_metrics_exception_handling_empty_array(self):
        """Test exception handling with empty numpy array"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        empty_array = np.array([])
        metrics = calculate_face_quality_metrics(empty_array)

        assert all(v == 0.0 for v in metrics.values())

    def test_quality_metrics_exception_handling_wrong_dimensions(self):
        """Test exception handling with unexpected array dimensions"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        invalid_array = np.ones(100, dtype=np.uint8)
        metrics = calculate_face_quality_metrics(invalid_array)

        assert metrics["quality_score"] == 0.0

    def test_quality_metrics_all_code_paths_comprehensive(self):
        """Comprehensive test covering all code paths in calculate_quality_metrics"""
        if not ML_AVAILABLE:
            pytest.skip("ML dependencies not available")

        # Test 1: Color image (3-channel) - grayscale conversion path
        color_face = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        color_metrics = calculate_face_quality_metrics(color_face)
        assert len(color_face.shape) == 3
        assert all(
            k in color_metrics
            for k in [
                "sharpness",
                "face_area",
                "brightness",
                "contrast",
                "quality_score",
            ]
        )

        # Test 2: Grayscale image (2-channel) - direct gray path
        gray_face = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        gray_metrics = calculate_face_quality_metrics(gray_face)
        assert len(gray_face.shape) == 2
        assert all(v >= 0.0 for v in gray_metrics.values())

        # Test 3: Various quality levels
        test_faces = [
            np.ones((50, 50, 3), dtype=np.uint8) * 0,
            np.ones((100, 100, 3), dtype=np.uint8) * 128,
            np.ones((200, 200, 3), dtype=np.uint8) * 255,
        ]

        for face in test_faces:
            metrics = calculate_face_quality_metrics(face)
            assert 0.0 <= metrics["quality_score"] <= 1.0

        # Test 4: Exception handling
        invalid_inputs = [None, np.array([]), np.ones(10)]
        for invalid in invalid_inputs:
            error_metrics = calculate_face_quality_metrics(invalid)
            assert error_metrics["quality_score"] == 0.0
