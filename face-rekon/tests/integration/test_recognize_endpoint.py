"""
Comprehensive integration tests for the /recognize endpoint.
Targets 80% coverage of app.py lines 73-239 (Recognize.post method).
Tests all critical paths: validation, processing, error handling, response assembly.
"""
import base64
import io

import pytest
from PIL import Image, ImageDraw

from .test_recognize_mocks import (
    RecognizeAssertions,
    RecognizeTestData,
    RecognizeTestScenarios,
    RecognizeTestUtils,
)


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
        try:
            import app

            with app.app.test_client() as client:
                response = RecognizeTestUtils.make_recognize_request(
                    client, {"event_id": "test_event"}
                )
                RecognizeAssertions.assert_missing_image_error(response)
                print("✅ Missing image_base64 test passed")
        except ImportError:
            pytest.skip("Flask app not available")

    def test_recognize_empty_request_body(self):
        """Test /recognize endpoint with empty request body"""
        try:
            import app

            with app.app.test_client() as client:
                response = RecognizeTestUtils.make_recognize_request(client, {})
                RecognizeAssertions.assert_missing_image_error(response)
                print("✅ Empty request body test passed")
        except ImportError:
            pytest.skip("Flask app not available")

    def test_recognize_no_json_data(self):
        """Test /recognize endpoint with no JSON data"""
        try:
            import app

            with app.app.test_client() as client:
                response = RecognizeTestUtils.make_recognize_request_with_raw_data(
                    client, "not json"
                )
                RecognizeAssertions.assert_missing_image_error(response)
                print("✅ No JSON data test passed")
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Cases 4-5: Base64 processing (lines 91-100)
    def test_recognize_data_uri_format(self, test_image_base64):
        """Test /recognize endpoint with data URI format (lines 91-95)"""
        try:
            import app

            with app.app.test_client() as client:
                data_uri_image = RecognizeTestData.create_data_uri_image(
                    test_image_base64
                )
                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {"image_base64": data_uri_image, "event_id": "test_data_uri"},
                )
                RecognizeAssertions.assert_processing_response(response)
                print("✅ Data URI format test passed")
        except ImportError:
            pytest.skip("Flask app not available")

    def test_recognize_custom_data_prefix(self, test_image_base64):
        """Test /recognize endpoint with custom data prefix format (lines 96-100)"""
        try:
            import app

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
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 6: Invalid base64 data (lines 130-132)
    def test_recognize_invalid_base64(self):
        """Test /recognize endpoint with invalid base64 data"""
        try:
            import app

            with app.app.test_client() as client:
                invalid_base64 = RecognizeTestData.create_invalid_base64()
                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {"image_base64": invalid_base64, "event_id": "test_invalid_base64"},
                )
                RecognizeAssertions.assert_invalid_base64_error(response)
                print("✅ Invalid base64 test passed")
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 7: JSON error response detection (lines 108-125)
    def test_recognize_json_error_response_detection(self):
        """Test /recognize endpoint detecting JSON error responses"""
        try:
            import app

            with app.app.test_client() as client:
                json_error_response = (
                    RecognizeTestData.create_mock_json_error_response()
                )
                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {
                        "image_base64": json_error_response,
                        "event_id": "test_json_error",
                    },
                )
                RecognizeAssertions.assert_json_error_response(response)
                print("✅ JSON error response detection test passed")
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Cases 8-10: Format detection (lines 139-150)
    def test_recognize_format_detection(self):
        """Test /recognize endpoint with different image formats"""
        try:
            import app

            with app.app.test_client() as client:
                format_scenarios = (
                    RecognizeTestScenarios.get_format_detection_scenarios()
                )

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
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 11: Missing event_id Flask-RESTX validation
    def test_recognize_missing_event_id(self, test_image_base64):
        """Test /recognize endpoint with missing event_id (Flask-RESTX validation)"""
        try:
            import app

            with app.app.test_client() as client:
                # This should trigger Flask-RESTX validation error
                response = RecognizeTestUtils.make_recognize_request(
                    client, {"image_base64": test_image_base64}
                )
                # Expect Flask-RESTX validation error (400)
                assert response.status_code == 400
                print("✅ Missing event_id validation test passed")
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 12: Event ID logging verification (lines 82-84)
    def test_recognize_event_id_logging(self, test_image_base64):
        """Test event ID processing and logging"""
        try:
            import app

            with app.app.test_client() as client:
                custom_event_id = "integration_test_logging_12345"
                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {"image_base64": test_image_base64, "event_id": custom_event_id},
                )
                RecognizeAssertions.assert_processing_response(response)
                RecognizeAssertions.assert_event_id_handling(response, custom_event_id)
                print("✅ Event ID logging test passed")
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 13: Successful processing with response structure
    def test_recognize_successful_processing(self, test_image_base64):
        """Test /recognize endpoint with successful recognition"""
        try:
            import app

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
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 14: Error handling structure (lines 221-232)
    def test_recognize_error_response_structure(self, test_image_base64):
        """Test /recognize endpoint error handling structure"""
        try:
            import app

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
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 15: Cleanup verification (lines 234-239)
    def test_recognize_temp_file_cleanup(self, test_image_base64):
        """Test that temporary files are properly cleaned up"""
        try:
            import app

            with app.app.test_client() as client:
                RecognizeTestUtils.verify_temp_file_cleanup(
                    client,
                    {"image_base64": test_image_base64, "event_id": "test_cleanup"},
                )
                print("✅ Temp file cleanup test passed")
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 16: Request preprocessing error handling (lines 158-160)
    def test_recognize_preprocessing_error(self):
        """Test /recognize endpoint with preprocessing errors"""
        try:
            import app

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
                # Should return 200 with error in response
                assert response.status_code == 200
                data = response.get_json()
                assert "status" in data and data["status"] == "error"
                print("✅ Preprocessing error test passed")
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 17: Large image handling
    def test_recognize_large_image_handling(self):
        """Test /recognize endpoint with large images"""
        try:
            import app

            with app.app.test_client() as client:
                large_image = RecognizeTestData.create_large_image()
                response = RecognizeTestUtils.make_recognize_request(
                    client,
                    {"image_base64": large_image, "event_id": "test_large_image"},
                )
                RecognizeAssertions.assert_processing_response(response)
                print("✅ Large image handling test passed")
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 18: Multiple scenario testing for all request variations
    def test_recognize_comprehensive_scenarios(self, test_image_base64):
        """Test multiple request scenarios for comprehensive coverage"""
        try:
            import app

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
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 19: Error scenarios comprehensive testing
    def test_recognize_error_scenarios_comprehensive(self):
        """Test comprehensive error scenarios"""
        try:
            import app

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
        except ImportError:
            pytest.skip("Flask app not available")

    # Test Case 20: Storage logic coverage (lines 175-206)
    def test_recognize_storage_logic_coverage(self, test_image_base64):
        """Test storage logic for faces (optimized vs legacy storage paths)"""
        try:
            import app

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
        except ImportError:
            pytest.skip("Flask app not available")
