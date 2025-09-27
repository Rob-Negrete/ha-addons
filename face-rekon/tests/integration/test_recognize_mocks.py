"""
Mock data, fixtures, and test utilities for /recognize endpoint testing.
Contains reusable test data generators, mock responses, and assertion helpers.
"""
import base64
import io
import json
import os

from PIL import Image, ImageDraw


class RecognizeTestData:
    """Test data generator for /recognize endpoint tests"""

    @staticmethod
    def create_mock_json_error_response():
        """Create JSON error response disguised as image data (for lines 108-125)"""
        error_response = {"success": False, "message": "Camera error"}
        json_str = json.dumps(error_response)
        return base64.b64encode(json_str.encode()).decode()

    @staticmethod
    def create_data_uri_image(base64_image):
        """Create data URI format image (for lines 91-95)"""
        return f"data:image/jpeg;base64,{base64_image}"

    @staticmethod
    def create_custom_prefix_image(base64_image):
        """Create custom prefix format image (for lines 96-100)"""
        return f"image/jpg;data:{base64_image}"

    @staticmethod
    def create_webp_image():
        """Create WEBP format image for format detection testing"""
        img = Image.new("RGB", (100, 100), color="red")
        buffered = io.BytesIO()
        img.save(buffered, format="WEBP")
        webp_data = buffered.getvalue()
        return base64.b64encode(webp_data).decode()

    @staticmethod
    def create_png_image():
        """Create PNG format image for format detection testing"""
        img = Image.new("RGB", (100, 100), color="blue")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        png_data = buffered.getvalue()
        return base64.b64encode(png_data).decode()

    @staticmethod
    def create_unknown_format_data():
        """Create fake image data with unknown header (for lines 148-150)"""
        fake_data = b"UNKNOWN_FORMAT" + b"fake_image_data" * 100
        return base64.b64encode(fake_data).decode()

    @staticmethod
    def create_corrupted_jpeg_data():
        """Create corrupted JPEG data for error handling testing"""
        corrupted_data = b"\xff\xd8\xff" + b"corrupted_jpeg_data" * 50
        return base64.b64encode(corrupted_data).decode()

    @staticmethod
    def create_large_image():
        """Create large image for stress testing"""
        img = Image.new("RGB", (1000, 750), color="gray")
        draw = ImageDraw.Draw(img)
        # Add a face pattern
        draw.ellipse([400, 300, 600, 450], fill=(255, 220, 177))

        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode()

    @staticmethod
    def create_invalid_base64():
        """Create invalid base64 data for error testing"""
        return "not_valid_base64_data_!@#"

    @staticmethod
    def create_large_payload():
        """Create large payload for memory stress testing"""
        return "A" * (1024 * 1024)  # 1MB of 'A' characters


class RecognizeTestScenarios:
    """Test case scenarios for comprehensive /recognize endpoint coverage"""

    @staticmethod
    def get_error_request_scenarios():
        """Get various error request scenarios"""
        return [
            # Flask-RESTX validation level (won't reach endpoint code)
            ("missing_image_base64", {"event_id": "test_event"}),
            ("empty_request", {}),
            # Endpoint logic level (will reach our code)
            ("null_image", {"image_base64": None, "event_id": "test"}),
            ("empty_image", {"image_base64": "", "event_id": "test"}),
        ]

    @staticmethod
    def get_valid_request_variations(base64_image):
        """Get valid request variations for testing different code paths"""
        return [
            # Standard request
            {"image_base64": base64_image, "event_id": "standard_test"},
            # Missing event_id (should default to "unknown") - lines 81-82
            {"image_base64": base64_image},
            # Custom event_id for logging verification - lines 82-84
            {"image_base64": base64_image, "event_id": "custom_logging_test_12345"},
            # Data URI format - lines 91-95
            {
                "image_base64": RecognizeTestData.create_data_uri_image(base64_image),
                "event_id": "data_uri_test",
            },
            # Custom prefix format - lines 96-100
            {
                "image_base64": RecognizeTestData.create_custom_prefix_image(
                    base64_image
                ),
                "event_id": "custom_prefix_test",
            },
        ]

    @staticmethod
    def get_format_detection_scenarios():
        """Get format detection test scenarios (lines 139-150)"""
        return [
            ("webp", RecognizeTestData.create_webp_image()),
            ("png", RecognizeTestData.create_png_image()),
            ("unknown", RecognizeTestData.create_unknown_format_data()),
            ("corrupted_jpeg", RecognizeTestData.create_corrupted_jpeg_data()),
        ]

    @staticmethod
    def get_error_scenarios():
        """Get error handling test scenarios"""
        return [
            ("invalid_base64", RecognizeTestData.create_invalid_base64()),
            (
                "json_error_response",
                RecognizeTestData.create_mock_json_error_response(),
            ),
            ("large_payload", RecognizeTestData.create_large_payload()),
            ("corrupted_data", RecognizeTestData.create_corrupted_jpeg_data()),
        ]


class RecognizeAssertions:
    """Common assertions for /recognize endpoint testing"""

    @staticmethod
    def assert_missing_image_error(response):
        """Assert missing image_base64 error response (Flask-RESTX validation)"""
        assert response.status_code == 400
        data = response.get_json()
        # Flask-RESTX validation response format
        assert "errors" in data or "message" in data
        if "errors" in data:
            assert "image_base64" in str(data["errors"])

    @staticmethod
    def assert_invalid_base64_error(response):
        """Assert invalid base64 error response (lines 130-132)"""
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "Invalid base64 image data"

    @staticmethod
    def assert_json_error_response(response):
        """Assert JSON error response detection (lines 117-125)"""
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"] == "Invalid image data - received error response"
        assert "details" in data

    @staticmethod
    def assert_success_response_structure(response):
        """Assert successful response structure (lines 208-219)"""
        if response.status_code == 200:
            data = response.get_json()
            assert "status" in data
            assert "faces_count" in data
            assert "faces" in data
            assert "event_id" in data
            assert "processing_method" in data
            assert data["processing_method"] == "face_extraction_crops"

    @staticmethod
    def assert_error_response_structure(response):
        """Assert error response has proper structure (lines 224-232)"""
        if response.status_code == 500:
            data = response.get_json()
            assert "error" in data
            assert "event_id" in data
            assert "status" in data
            assert data["status"] == "error"
            assert "faces_count" in data
            assert "faces" in data

    @staticmethod
    def assert_processing_response(response):
        """Assert response is either success or proper error"""
        assert response.status_code in [200, 400, 500]
        data = response.get_json()
        assert "error" in data or "status" in data

    @staticmethod
    def assert_event_id_handling(response, expected_event_id):
        """Assert event_id is properly handled"""
        if response.status_code == 200:
            data = response.get_json()
            assert data["event_id"] == expected_event_id


class RecognizeTestUtils:
    """Utility functions for /recognize endpoint testing"""

    @staticmethod
    def count_temp_files():
        """Count temporary files in the temp directory for cleanup testing."""
        tmp_dir = "/app/data/tmp"
        os.makedirs(tmp_dir, exist_ok=True)
        return len(os.listdir(tmp_dir))

    @staticmethod
    def make_recognize_request(client, request_data):
        """Make a standardized recognize request"""
        import json

        return client.post(
            "/api/face-rekon/recognize",
            data=json.dumps(request_data),
            content_type="application/json",
        )

    @staticmethod
    def make_recognize_request_with_raw_data(
        client, data, content_type="application/json"
    ):
        """Make recognize request with raw data"""
        return client.post(
            "/api/face-rekon/recognize", data=data, content_type=content_type
        )

    @staticmethod
    def verify_temp_file_cleanup(client, request_data):
        """Verify temporary files are cleaned up after request"""
        files_before = RecognizeTestUtils.count_temp_files()
        response = RecognizeTestUtils.make_recognize_request(client, request_data)
        files_after = RecognizeTestUtils.count_temp_files()
        # Should have same number of files (cleanup successful)
        assert files_after == files_before
        return response
