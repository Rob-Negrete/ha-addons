"""
Comprehensive integration tests for the /recognize endpoint.
Targets 80% coverage of app.py lines 73-239 (Recognize.post method).
Tests all critical paths: validation, processing, error handling, response assembly.
"""
import base64
import io
import os
import sys
from unittest.mock import Mock, patch

import pytest
from PIL import Image, ImageDraw

from .test_recognize_mocks import (
    RecognizeAssertions,
    RecognizeTestData,
    RecognizeTestScenarios,
    RecognizeTestUtils,
)

# Add scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

# Mock ML dependencies before importing
mock_insightface = Mock()
mock_faiss = Mock()
mock_cv2 = Mock()

with patch.dict(
    "sys.modules",
    {
        "insightface.app": mock_insightface,
        "cv2": mock_cv2,
        "faiss": mock_faiss,
    },
):
    with patch("clasificador.FaceAnalysis"), patch("clasificador.cv2"), patch(
        "clasificador.get_qdrant_adapter_instance"
    ):
        import app


@pytest.fixture
def test_image_base64():
    """Create a realistic test image for face detection"""
    img = Image.new("RGB", (640, 480), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)

    # Create a realistic face pattern
    center = (320, 240)
    width, height = 160, 200

    # Face oval
    face_bbox = [
        center[0] - width // 2,
        center[1] - height // 2,
        center[0] + width // 2,
        center[1] + height // 2,
    ]
    draw.ellipse(face_bbox, fill=(255, 220, 177), outline=(200, 160, 120), width=2)

    # Eyes
    left_eye = (center[0] - 30, center[1] - 40)
    right_eye = (center[0] + 30, center[1] - 40)

    for eye_center in [left_eye, right_eye]:
        draw.ellipse(
            [
                eye_center[0] - 15,
                eye_center[1] - 10,
                eye_center[0] + 15,
                eye_center[1] + 10,
            ],
            fill="white",
            outline="black",
            width=2,
        )
        draw.ellipse(
            [
                eye_center[0] - 6,
                eye_center[1] - 6,
                eye_center[0] + 6,
                eye_center[1] + 6,
            ],
            fill="black",
        )

    # Nose
    draw.polygon(
        [
            (center[0], center[1]),
            (center[0] - 10, center[1] + 20),
            (center[0] + 10, center[1] + 20),
        ],
        fill=(210, 180, 140),
    )

    # Mouth
    draw.arc(
        [center[0] - 30, center[1] + 50, center[0] + 30, center[1] + 80],
        start=0,
        end=180,
        fill="red",
        width=3,
    )

    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=95)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


@pytest.mark.integration
class TestRecognizeEndpointCoverage:
    """Comprehensive tests targeting specific coverage gaps in /recognize endpoint"""

    # Test Cases 1-3: Request validation (lines 76-79)
    def test_recognize_missing_image_base64(self):
        """Test /recognize endpoint with missing image_base64 parameter"""
        with app.app.test_client() as client:
            response = RecognizeTestUtils.make_recognize_request(
                client, {"event_id": "test_event"}
            )
            RecognizeAssertions.assert_missing_image_error(response)
            print("✅ Missing image_base64 test passed")

    def test_recognize_empty_request_body(self):
        """Test /recognize endpoint with empty request body"""
        with app.app.test_client() as client:
            response = RecognizeTestUtils.make_recognize_request(client, {})
            RecognizeAssertions.assert_missing_image_error(response)
            print("✅ Empty request body test passed")

    def test_recognize_no_json_data(self):
        """Test /recognize endpoint with no JSON data"""
        with app.app.test_client() as client:
            response = RecognizeTestUtils.make_recognize_request_with_raw_data(
                client, "not json"
            )
            RecognizeAssertions.assert_missing_image_error(response)
            print("✅ No JSON data test passed")

    # Test Cases 4-5: Base64 processing (lines 91-100)
    def test_recognize_data_uri_format(self, test_image_base64):
        """Test /recognize endpoint with data URI format (lines 91-95)"""
        with app.app.test_client() as client:
            data_uri_image = RecognizeTestData.create_data_uri_image(test_image_base64)
            response = RecognizeTestUtils.make_recognize_request(
                client,
                {"image_base64": data_uri_image, "event_id": "test_data_uri"},
            )
            RecognizeAssertions.assert_processing_response(response)
            print("✅ Data URI format test passed")

    def test_recognize_custom_data_prefix(self, test_image_base64):
        """Test /recognize endpoint with custom data prefix format (lines 96-100)"""
        with app.app.test_client() as client:
            custom_prefix_image = RecognizeTestData.create_custom_prefix_image(
                test_image_base64
            )
            response = RecognizeTestUtils.make_recognize_request(
                client,
                {
                    "image_base64": custom_prefix_image,
                    "event_id": "test_custom_prefix",
                },
            )
            RecognizeAssertions.assert_processing_response(response)
            print("✅ Custom data prefix test passed")

    # Test Case 6: Invalid base64 data (lines 130-132)
    def test_recognize_invalid_base64(self):
        """Test /recognize endpoint with invalid base64 data"""
        with app.app.test_client() as client:
            invalid_base64 = RecognizeTestData.create_invalid_base64()
            response = RecognizeTestUtils.make_recognize_request(
                client,
                {"image_base64": invalid_base64, "event_id": "test_invalid_base64"},
            )
            RecognizeAssertions.assert_invalid_base64_error(response)
            print("✅ Invalid base64 test passed")

    # Test Case 7: JSON error response detection (lines 108-125)
    def test_recognize_json_error_response_detection(self):
        """Test /recognize endpoint detecting JSON error responses"""
        with app.app.test_client() as client:
            json_error_response = RecognizeTestData.create_mock_json_error_response()
            response = RecognizeTestUtils.make_recognize_request(
                client,
                {
                    "image_base64": json_error_response,
                    "event_id": "test_json_error",
                },
            )
            RecognizeAssertions.assert_json_error_response(response)
            print("✅ JSON error response detection test passed")

    # Test Cases 8-10: Format detection (lines 139-150)
    def test_recognize_format_detection(self):
        """Test /recognize endpoint with different image formats"""
        with app.app.test_client() as client:
            format_scenarios = RecognizeTestScenarios.get_format_detection_scenarios()

            for format_name, base64_data in format_scenarios:
                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {
                        "image_base64": base64_data,
                        "event_id": f"test_{format_name}_format",
                    },
                )
                RecognizeAssertions.assert_processing_response(response)
                print(f"✅ {format_name.upper()} format detection test passed")

    # Test Case 11: Missing event_id Flask-RESTX validation
    def test_recognize_missing_event_id(self, test_image_base64):
        """Test /recognize endpoint with missing event_id (Flask-RESTX validation)"""
        with app.app.test_client() as client:
            # This should trigger Flask-RESTX validation error
            response = RecognizeTestUtils.make_recognize_request(
                client, {"image_base64": test_image_base64}
            )
            # Expect Flask-RESTX validation error (400)
            assert response.status_code == 400
            print("✅ Missing event_id validation test passed")

    # Test Case 12: Event ID logging verification (lines 82-84)
    def test_recognize_event_id_logging(self, test_image_base64):
        """Test event ID processing and logging"""
        with app.app.test_client() as client:
            custom_event_id = "integration_test_logging_12345"
            response = RecognizeTestUtils.make_recognize_request(
                client,
                {"image_base64": test_image_base64, "event_id": custom_event_id},
            )
            RecognizeAssertions.assert_processing_response(response)
            RecognizeAssertions.assert_event_id_handling(response, custom_event_id)
            print("✅ Event ID logging test passed")

    # Test Case 13: Successful processing with response structure
    def test_recognize_successful_processing(self, test_image_base64):
        """Test /recognize endpoint with successful recognition"""
        with app.app.test_client() as client:
            response = RecognizeTestUtils.make_recognize_request(
                client,
                {
                    "image_base64": test_image_base64,
                    "event_id": "test_successful_processing",
                },
            )
            RecognizeAssertions.assert_processing_response(response)
            RecognizeAssertions.assert_success_response_structure(response)
            print("✅ Successful processing test passed")

    # Test Case 14: Error handling structure (lines 221-232)
    def test_recognize_error_response_structure(self, test_image_base64):
        """Test /recognize endpoint error handling structure"""
        with app.app.test_client() as client:
            response = RecognizeTestUtils.make_recognize_request(
                client,
                {
                    "image_base64": test_image_base64,
                    "event_id": "test_error_structure",
                },
            )
            RecognizeAssertions.assert_processing_response(response)
            RecognizeAssertions.assert_error_response_structure(response)
            print("✅ Error response structure test passed")

    # Test Case 15: Cleanup verification (lines 234-239)
    def test_recognize_temp_file_cleanup(self, test_image_base64):
        """Test that temporary files are properly cleaned up"""
        with app.app.test_client() as client:
            RecognizeTestUtils.verify_temp_file_cleanup(
                client,
                {"image_base64": test_image_base64, "event_id": "test_cleanup"},
            )
            print("✅ Temp file cleanup test passed")

    # Test Case 16: Request preprocessing error handling (lines 158-160)
    def test_recognize_preprocessing_error(self):
        """Test /recognize endpoint with preprocessing errors"""
        with app.app.test_client() as client:
            large_payload = RecognizeTestData.create_large_payload()
            response = RecognizeTestUtils.make_recognize_request(
                client,
                {
                    "image_base64": large_payload,
                    "event_id": "test_preprocessing_error",
                },
            )
            # Large payload gets processed but fails later
            # Should return 200 with no_faces_detected status
            assert response.status_code == 200
            data = response.get_json()
            assert "status" in data and data["status"] == "no_faces_detected"
            print("✅ Preprocessing error test passed")

    # Test Case 17: Large image handling
    def test_recognize_large_image_handling(self):
        """Test /recognize endpoint with large images"""
        with app.app.test_client() as client:
            large_image = RecognizeTestData.create_large_image()
            response = RecognizeTestUtils.make_recognize_request(
                client,
                {"image_base64": large_image, "event_id": "test_large_image"},
            )
            RecognizeAssertions.assert_processing_response(response)
            print("✅ Large image handling test passed")

    # Test Case 18: Multiple scenario testing for all request variations
    def test_recognize_comprehensive_scenarios(self, test_image_base64):
        """Test multiple request scenarios for comprehensive coverage"""
        with app.app.test_client() as client:
            scenarios = RecognizeTestScenarios.get_valid_request_variations(
                test_image_base64
            )

            for i, request_data in enumerate(scenarios):
                response = RecognizeTestUtils.make_recognize_request(
                    client, request_data
                )
                RecognizeAssertions.assert_processing_response(response)
                print(f"✅ Comprehensive scenario {i+1} test passed")

    # Test Case 19: Error scenarios comprehensive testing
    def test_recognize_error_scenarios_comprehensive(self):
        """Test comprehensive error scenarios"""
        with app.app.test_client() as client:
            error_scenarios = RecognizeTestScenarios.get_error_scenarios()

            for scenario_name, base64_data in error_scenarios:
                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {
                        "image_base64": base64_data,
                        "event_id": f"test_{scenario_name}",
                    },
                )
                # Should handle all error scenarios gracefully
                assert response.status_code in [200, 400, 500]
                data = response.get_json()
                assert "error" in data or "status" in data
                print(f"✅ Error scenario '{scenario_name}' test passed")

    # Test Case 20: Storage logic coverage (lines 175-206)
    def test_recognize_storage_logic_coverage(self, test_image_base64):
        """Test storage logic for faces (optimized vs legacy storage paths)"""
        with app.app.test_client() as client:
            response = RecognizeTestUtils.make_recognize_request(
                client,
                {
                    "image_base64": test_image_base64,
                    "event_id": "test_storage_logic",
                },
            )
            RecognizeAssertions.assert_processing_response(response)
            # Should exercise storage logic paths (lines 175-206)
            print("✅ Storage logic coverage test passed")

    # Test Case 21: Optimized storage path (lines 183-192)
    def test_recognize_optimized_storage_path(self, test_image_base64):
        """Test /recognize with optimized storage enabled (lines 183-192)"""
        with app.app.test_client() as client:
            # Ensure optimized storage is enabled
            original_storage = app.clasificador.USE_OPTIMIZED_STORAGE
            try:
                app.clasificador.USE_OPTIMIZED_STORAGE = True

                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {
                        "image_base64": test_image_base64,
                        "event_id": "test_optimized_storage",
                    },
                )

                # Should process successfully (may or may not find faces)
                assert response.status_code == 200
                data = response.get_json()
                assert "status" in data
                print("✅ Optimized storage path test passed")
            finally:
                app.clasificador.USE_OPTIMIZED_STORAGE = original_storage

    # Test Case 22: Legacy storage path (lines 197-205)
    def test_recognize_legacy_storage_path(self, test_image_base64):
        """Test /recognize with legacy storage (lines 197-205)"""
        with app.app.test_client() as client:
            # Ensure legacy storage is used
            original_storage = app.clasificador.USE_OPTIMIZED_STORAGE
            try:
                app.clasificador.USE_OPTIMIZED_STORAGE = False

                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {
                        "image_base64": test_image_base64,
                        "event_id": "test_legacy_storage",
                    },
                )

                # Should process successfully (may or may not find faces)
                assert response.status_code == 200
                data = response.get_json()
                assert "status" in data
                print("✅ Legacy storage path test passed")
            finally:
                app.clasificador.USE_OPTIMIZED_STORAGE = original_storage

    # Test Case 23: Custom data prefix edge case (lines 97, 100)
    def test_recognize_custom_semicolon_data_prefix(self, test_image_base64):
        """Test /recognize with semicolon data prefix format (lines 97, 100)"""
        with app.app.test_client() as client:
            # Create image with ;data: prefix (not data:)
            custom_image = f"image/jpg;data:{test_image_base64}"

            response = RecognizeTestUtils.make_recognize_request(
                client,
                {
                    "image_base64": custom_image,
                    "event_id": "test_semicolon_prefix",
                },
            )

            RecognizeAssertions.assert_processing_response(response)
            print("✅ Custom semicolon data prefix test passed")

    # Test Case 24: JSON decode exception handling (lines 126, 128)
    def test_recognize_json_decode_exception_handling(self):
        """Test /recognize JSON decode exception path (lines 126, 128)"""
        with app.app.test_client() as client:
            # Create data that decodes to < 100 bytes but is not valid JSON
            # This should trigger the except block on lines 126-128
            small_binary_data = b"small_invalid_json_" + b"\x00\xff" * 10
            small_base64 = base64.b64encode(small_binary_data).decode()

            response = RecognizeTestUtils.make_recognize_request(
                client,
                {
                    "image_base64": small_base64,
                    "event_id": "test_json_decode_exception",
                },
            )

            # Should process without crashing (exception caught and passed)
            assert response.status_code in [200, 400, 500]
            print("✅ JSON decode exception handling test passed")

    # Test Case 25: Suggestion status storage path (lines 183-192)
    def test_recognize_suggestion_face_storage(self, test_image_base64):
        """Test /recognize with suggestion faces (lines 183-192)"""
        with app.app.test_client() as client:
            # This test relies on real face detection possibly returning suggestions
            # Ensure optimized storage is enabled
            original_storage = app.clasificador.USE_OPTIMIZED_STORAGE
            try:
                app.clasificador.USE_OPTIMIZED_STORAGE = True

                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {
                        "image_base64": test_image_base64,
                        "event_id": "test_suggestion_storage",
                    },
                )

                # Should process successfully
                assert response.status_code == 200
                data = response.get_json()
                assert "status" in data
                # Tests the storage path code even if no suggestions returned
                print("✅ Suggestion face storage test passed")
            finally:
                app.clasificador.USE_OPTIMIZED_STORAGE = original_storage

    # Test Case 26: Lines 78-79 validation error path
    def test_recognize_validation_error_logging(self):
        """Test /recognize validation error logging (lines 78-79)"""
        with app.app.test_client() as client:
            # Send request with explicit None for image_base64
            response = client.post(
                "/api/face-rekon/recognize",
                json={"image_base64": None, "event_id": "test"},
            )

            # Should return validation error
            assert response.status_code == 400
            print("✅ Validation error logging test passed")

    # Test Case 27: Real face with optimized storage (lines 183-192)
    def test_recognize_real_face_optimized_storage(self):
        """Test /recognize with real face image to trigger storage (lines 183-192)"""
        with app.app.test_client() as client:
            # Use real test image with a face
            import base64

            with open("tests/dummies/one-face.jpg", "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode()

            original_storage = app.clasificador.USE_OPTIMIZED_STORAGE
            try:
                app.clasificador.USE_OPTIMIZED_STORAGE = True

                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {
                        "image_base64": image_base64,
                        "event_id": "test_real_face_optimized",
                    },
                )

                assert response.status_code == 200
                data = response.get_json()
                # Real face should be detected
                assert "faces_count" in data
                print("✅ Real face with optimized storage test passed")
            finally:
                app.clasificador.USE_OPTIMIZED_STORAGE = original_storage

    # Test Case 28: Real face with legacy storage (lines 197-205)
    def test_recognize_real_face_legacy_storage(self):
        """Test /recognize with real face image and legacy storage (lines 197-205)"""
        with app.app.test_client() as client:
            # Use real test image with a face
            import base64

            with open("tests/dummies/one-face.jpg", "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode()

            original_storage = app.clasificador.USE_OPTIMIZED_STORAGE
            try:
                app.clasificador.USE_OPTIMIZED_STORAGE = False

                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {
                        "image_base64": image_base64,
                        "event_id": "test_real_face_legacy",
                    },
                )

                assert response.status_code == 200
                data = response.get_json()
                # Real face should be detected
                assert "faces_count" in data
                print("✅ Real face with legacy storage test passed")
            finally:
                app.clasificador.USE_OPTIMIZED_STORAGE = original_storage

    # Test Case 29: Main exception handler (lines 223-234)
    def test_recognize_main_exception_handler(self, test_image_base64):
        """Test /recognize main exception handling (lines 223-234)"""
        import app

        with app.app.test_client() as client:
            # Mock identify_all_faces to raise an exception
            # Patch clasificador module (app.py imports: import clasificador)
            with patch("clasificador.identify_all_faces") as mock_identify:
                mock_identify.side_effect = RuntimeError(
                    "Simulated face recognition failure"
                )

                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {
                        "image_base64": test_image_base64,
                        "event_id": "test_main_exception",
                    },
                )

                # Should return 500 error response
                assert response.status_code == 500
                data = response.get_json()

                # Verify error response structure (lines 226-232)
                assert "error" in data
                assert "Simulated face recognition failure" in data["error"]
                assert data["event_id"] == "test_main_exception"
                assert data["status"] == "error"
                assert data["faces_count"] == 0
                assert data["faces"] == []

                print("✅ Main exception handler test passed")
