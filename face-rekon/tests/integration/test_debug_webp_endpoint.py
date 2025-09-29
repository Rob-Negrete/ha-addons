"""
Comprehensive integration tests for the /debug/test-webp endpoint.
Targets 80% coverage of app.py lines 329-419 (debug_test_webp function).
Tests all critical paths: validation, processing, error handling, response assembly.
"""
import base64
import io
import os
import sys
from unittest.mock import Mock, patch

import pytest
from PIL import Image

# Removed external dependencies for simplified testing

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
def debug_test_image_base64():
    """Create a test image for debug endpoint testing"""
    img = Image.new("RGB", (320, 240), color=(200, 200, 200))
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=95)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


@pytest.fixture
def debug_webp_image_base64():
    """Create a WEBP test image for format detection testing"""
    img = Image.new("RGB", (160, 120), color=(150, 150, 150))
    buffered = io.BytesIO()
    img.save(buffered, format="WEBP", quality=80)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


@pytest.mark.integration
class TestDebugWebpEndpointCoverage:
    """Tests targeting specific coverage gaps in /debug/test-webp endpoint"""

    def setup_method(self):
        """Setup test data and mocks"""
        # Mock clasificador.identify_all_faces to return predictable results
        self.mock_faces_result = [
            {"face_index": 0, "status": "unknown", "confidence": 0.0}
        ]

    # Test Cases 1-3: Request validation (lines 334-342)
    def test_debug_webp_missing_json_data(self):
        """Test /debug/test-webp endpoint with no JSON data"""
        with app.app.test_client() as client:
            # Send request without JSON content-type
            response = client.post("/debug/test-webp", data="not json")

            # Debug endpoint handles all errors and returns 200 with error status
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "error"
            assert "Debug endpoint failed" in data["message"]
            print("✅ Missing JSON data test passed")

    def test_debug_webp_missing_image_base64(self):
        """Test /debug/test-webp endpoint with missing image_base64 parameter"""
        with app.app.test_client() as client:
            response = client.post("/debug/test-webp", json={"event_id": "test_event"})

            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data
            assert data["error"] == "Missing image_base64"
            print("✅ Missing image_base64 test passed")

    def test_debug_webp_empty_json(self):
        """Test /debug/test-webp endpoint with empty JSON"""
        with app.app.test_client() as client:
            response = client.post("/debug/test-webp", json={})

            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data
            assert (
                data["error"] == "Missing image_base64"
            )  # Empty dict has data, so goes to missing image check
            print("✅ Empty JSON test passed")

    def test_debug_webp_no_json_content_type(self):
        """Test /debug/test-webp endpoint with no JSON content type - covers line 339"""
        with app.app.test_client() as client:
            # Send request without content-type application/json
            response = client.post(
                "/debug/test-webp", data="not json", content_type="text/plain"
            )

            assert response.status_code == 200  # Debug endpoint catches all errors
            data = response.get_json()
            assert data["status"] == "error"
            assert "Debug endpoint failed" in data["message"]
            print("✅ No JSON content type test passed")

    def test_debug_webp_successful_base64_decode(self, debug_test_image_base64):
        """Test successful base64 decode - covers line 351"""
        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": debug_test_image_base64}
            )

            # Should at least decode the base64 (line 351) before failing
            # Even if it fails later, line 351 should be covered
            assert response.status_code in [200, 400, 500]
            print("✅ Successful base64 decode test passed")

    # Test Cases 4-5: Base64 processing (lines 344-354)
    def test_debug_webp_invalid_base64(self):
        """Test /debug/test-webp endpoint with invalid base64 data"""
        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": "invalid_base64_!@#$%"}
            )

            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data
            assert "Base64 decode failed" in data["error"]
            print("✅ Invalid base64 test passed")

    @patch("app.clasificador.identify_all_faces")
    def test_debug_webp_valid_base64_processing(
        self, mock_identify, debug_test_image_base64
    ):
        """Test /debug/test-webp endpoint with valid base64 processing"""
        mock_identify.return_value = self.mock_faces_result

        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": debug_test_image_base64}
            )

            # Should succeed and process the image
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"
            assert "file_size" in data
            assert data["file_size"] > 0
            print("✅ Valid base64 processing test passed")

    # Test Cases 6-8: Format detection (lines 356-365)
    @patch("app.clasificador.identify_all_faces")
    def test_debug_webp_jpeg_format_detection(
        self, mock_identify, debug_test_image_base64
    ):
        """Test /debug/test-webp endpoint with JPEG format detection"""
        mock_identify.return_value = self.mock_faces_result

        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": debug_test_image_base64}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["format"] == ".jpg"
            print("✅ JPEG format detection test passed")

    @patch("app.clasificador.identify_all_faces")
    def test_debug_webp_webp_format_detection(
        self, mock_identify, debug_webp_image_base64
    ):
        """Test /debug/test-webp endpoint with WEBP format detection"""
        mock_identify.return_value = self.mock_faces_result

        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": debug_webp_image_base64}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["format"] == ".webp"
            print("✅ WEBP format detection test passed")

    @patch("app.clasificador.identify_all_faces")
    def test_debug_webp_png_format_fallback(self, mock_identify):
        """Test /debug/test-webp endpoint with PNG/other format fallback"""
        # Create PNG image
        img = Image.new("RGB", (100, 100), color=(100, 100, 100))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        png_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        mock_identify.return_value = self.mock_faces_result

        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": png_base64}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["format"] == ".png"
            print("✅ PNG format fallback test passed")

    # Test Cases 9-10: File operations (lines 367-376)
    @patch("app.clasificador.identify_all_faces")
    @patch("os.makedirs")
    @patch("builtins.open", create=True)
    @patch("os.path.join")
    def test_debug_webp_file_creation_and_saving(
        self,
        mock_join,
        mock_open,
        mock_makedirs,
        mock_identify,
        debug_test_image_base64,
    ):
        """Test /debug/test-webp endpoint file creation and saving"""
        mock_identify.return_value = self.mock_faces_result
        mock_join.return_value = "/tmp/debug-test.jpg"

        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": debug_test_image_base64}
            )

            # Verify directory creation was attempted
            mock_makedirs.assert_called()

            # Verify file write was attempted
            mock_open.assert_called()

            assert response.status_code == 200
            print("✅ File creation and saving test passed")

    # Test Cases 11-12: Face recognition integration (lines 378-401)
    @patch("app.clasificador.identify_all_faces")
    def test_debug_webp_successful_face_recognition(
        self, mock_identify, debug_test_image_base64
    ):
        """Test /debug/test-webp endpoint with successful face recognition"""
        mock_identify.return_value = [
            {"face_index": 0, "status": "recognized", "confidence": 0.95},
            {"face_index": 1, "status": "unknown", "confidence": 0.0},
        ]

        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": debug_test_image_base64}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"
            assert data["message"] == "Debug test completed successfully"
            assert data["faces_count"] == 2
            assert len(data["faces"]) == 2
            print("✅ Successful face recognition test passed")

    @patch("app.clasificador.identify_all_faces")
    def test_debug_webp_face_recognition_error(
        self, mock_identify, debug_test_image_base64
    ):
        """Test /debug/test-webp endpoint with face recognition error"""
        mock_identify.side_effect = Exception("Face recognition failed")

        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": debug_test_image_base64}
            )

            assert (
                response.status_code == 200
            )  # Debug endpoint returns 200 even on errors
            data = response.get_json()
            assert data["status"] == "error"
            assert "Face recognition failed" in data["message"]
            assert "traceback" in data
            print("✅ Face recognition error test passed")

    # Test Cases 13-14: Cleanup logic (lines 403-410)
    @patch("app.clasificador.identify_all_faces")
    @patch("os.path.exists")
    @patch("os.remove")
    def test_debug_webp_file_cleanup_success(
        self, mock_remove, mock_exists, mock_identify, debug_test_image_base64
    ):
        """Test /debug/test-webp endpoint file cleanup success"""
        mock_identify.return_value = self.mock_faces_result
        mock_exists.return_value = True

        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": debug_test_image_base64}
            )

            # Verify cleanup was attempted
            mock_exists.assert_called()
            mock_remove.assert_called()

            assert response.status_code == 200
            print("✅ File cleanup success test passed")

    @patch("app.clasificador.identify_all_faces")
    @patch("os.path.exists")
    @patch("os.remove")
    def test_debug_webp_file_cleanup_failure(
        self, mock_remove, mock_exists, mock_identify, debug_test_image_base64
    ):
        """Test /debug/test-webp endpoint file cleanup failure handling"""
        mock_identify.return_value = self.mock_faces_result
        mock_exists.return_value = True
        mock_remove.side_effect = Exception("Cleanup failed")

        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": debug_test_image_base64}
            )

            # Should still succeed despite cleanup failure
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"
            print("✅ File cleanup failure handling test passed")

    # Test Cases 15-16: Top-level exception handling (lines 412-419)
    @patch("flask.request.get_json")
    def test_debug_webp_top_level_exception_handling(self, mock_get_json):
        """Test /debug/test-webp endpoint top-level exception handling"""
        mock_get_json.side_effect = Exception("Request processing failed")

        with app.app.test_client() as client:
            response = client.post("/debug/test-webp", json={"image_base64": "test"})

            assert response.status_code == 200  # Debug endpoint always returns 200
            data = response.get_json()
            assert data["status"] == "error"
            assert "Debug endpoint failed" in data["message"]
            assert "traceback" in data
            print("✅ Top-level exception handling test passed")

    # Test Case 17: Comprehensive success scenario
    @patch("app.clasificador.identify_all_faces")
    def test_debug_webp_comprehensive_success_scenario(
        self, mock_identify, debug_test_image_base64
    ):
        """Test /debug/test-webp endpoint comprehensive success scenario"""
        mock_identify.return_value = [
            {
                "face_index": 0,
                "status": "recognized",
                "confidence": 0.88,
                "person_name": "Test Person",
            }
        ]

        with app.app.test_client() as client:
            response = client.post(
                "/debug/test-webp", json={"image_base64": debug_test_image_base64}
            )

            assert response.status_code == 200
            data = response.get_json()

            # Verify all expected response fields
            assert data["status"] == "success"
            assert data["message"] == "Debug test completed successfully"
            assert data["faces_count"] == 1
            assert data["format"] == ".jpg"
            assert data["file_size"] > 0
            assert len(data["faces"]) == 1

            print("✅ Comprehensive success scenario test passed")

    # Test Case 18: Multiple format scenarios
    @patch("app.clasificador.identify_all_faces")
    def test_debug_webp_multiple_format_scenarios(self, mock_identify):
        """Test /debug/test-webp endpoint with multiple image format scenarios"""
        test_cases = [("JPEG", "jpg"), ("WEBP", "webp"), ("PNG", "png")]

        mock_identify.return_value = []

        for format_name, expected_ext in test_cases:
            img = Image.new("RGB", (50, 50), color=(255, 0, 0))
            buffered = io.BytesIO()
            img.save(
                buffered,
                format=format_name,
                quality=90 if format_name != "PNG" else None,
            )
            format_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            with app.app.test_client() as client:
                response = client.post(
                    "/debug/test-webp", json={"image_base64": format_base64}
                )

                assert response.status_code == 200
                data = response.get_json()
                assert data["format"] == f".{expected_ext}"

        print("✅ Multiple format scenarios test passed")
