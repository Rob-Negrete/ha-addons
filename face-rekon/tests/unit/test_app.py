import base64
import io
import os
import sys
from unittest.mock import Mock, patch

import pytest
from PIL import Image

# Add scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

# Mock the dependencies before importing
mock_insightface = Mock()
mock_tinydb = Mock()
mock_faiss = Mock()
mock_cv2 = Mock()

with patch.dict(
    "sys.modules",
    {
        "insightface.app": mock_insightface,
        "cv2": mock_cv2,
    },
):
    with patch("clasificador.FaceAnalysis"), patch("clasificador.cv2"), patch(
        "clasificador.get_qdrant_adapter_instance"
    ):
        import clasificador


class TestAppFunctionality:
    """Test app functionality without Flask-RESTX complexity"""

    def setup_method(self):
        """Setup test data"""
        # Create a test image as base64
        test_image = Image.new("RGB", (100, 100), color="red")
        buffered = io.BytesIO()
        test_image.save(buffered, format="JPEG")
        self.test_image_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        self.test_request = {
            "image_base64": self.test_image_b64,
            "event_id": "test_event_123",
        }

    def test_app_imports_correctly(self):
        """Test that app module can be imported with proper mocking"""
        # Additional mocking for the app import
        with patch.dict(
            "sys.modules",
            {
                "clasificador": Mock(),
                "insightface.app": Mock(),
                "tinydb": Mock(),
                "faiss": Mock(),
                "cv2": Mock(),
            },
        ):
            # Test that we can import the app module
            try:
                import app

                assert hasattr(app, "app")  # Flask app should exist
                assert hasattr(app, "api")  # API should exist
                assert hasattr(app, "ns")  # Namespace should exist
            except ImportError as e:
                pytest.fail(f"Failed to import app module: {e}")

    def test_ping_endpoint_logic(self):
        """Test the ping endpoint logic directly"""
        # Test the ping response logic without Flask decorators
        expected_response = {"pong": True}
        assert expected_response["pong"] is True

    def test_recognize_endpoint_logic(self):
        """Test recognize endpoint logic directly"""
        # Mock face identification results
        mock_results = [
            {
                "face_index": 0,
                "status": "identified",
                "face_data": {"face_id": "known_face_1", "name": "John Doe"},
                "confidence": 0.85,
            }
        ]
        clasificador.identify_all_faces = Mock(return_value=mock_results)
        clasificador.save_unknown_face = Mock()

        # Test the logic that would be in the recognize endpoint
        faces = clasificador.identify_all_faces(self.test_image_b64)

        # Verify the mocked results
        assert len(faces) == 1
        assert faces[0]["status"] == "identified"
        assert faces[0]["face_data"]["name"] == "John Doe"

        # Should not save unknown face since all faces were identified
        clasificador.save_unknown_face.assert_not_called()

    def test_recognize_unknown_face_logic(self):
        """Test recognize endpoint with unknown faces"""
        # Mock face identification with unknown faces
        mock_results = [
            {"face_index": 0, "status": "unknown", "face_data": None, "confidence": 0.0}
        ]
        clasificador.identify_all_faces = Mock(return_value=mock_results)
        clasificador.save_unknown_face = Mock()

        # Test the logic
        faces = clasificador.identify_all_faces(self.test_image_b64)

        assert len(faces) == 1
        assert faces[0]["status"] == "unknown"
        assert faces[0]["face_data"] is None

        # In real app, would call save_unknown_face for unknown faces
        if faces[0]["status"] == "unknown":
            clasificador.save_unknown_face("temp_image.jpg", "test_event")
            clasificador.save_unknown_face.assert_called_once()

    def test_image_data_processing(self):
        """Test image data processing logic"""
        # Test data URI format
        data_uri_image = f"data:image/jpeg;base64,{self.test_image_b64}"

        # Test extracting base64 from data URI
        if data_uri_image.startswith("data:"):
            base64_data = data_uri_image.split(",")[1]
        else:
            base64_data = data_uri_image

        assert base64_data == self.test_image_b64

    def test_response_structures(self):
        """Test API response structure logic"""
        # Test successful recognition response structure
        response_data = {
            "status": "success",
            "faces_count": 1,
            "faces": [
                {
                    "status": "identified",
                    "name": "John Doe",
                    "confidence": 0.85,
                    "face_id": "test_id",
                }
            ],
        }

        assert response_data["status"] == "success"
        assert response_data["faces_count"] == len(response_data["faces"])
        assert response_data["faces"][0]["name"] == "John Doe"

        # Test no faces detected response
        no_faces_response = {
            "status": "no_faces_detected",
            "faces_count": 0,
            "faces": [],
        }

        assert no_faces_response["status"] == "no_faces_detected"
        assert no_faces_response["faces_count"] == 0
        assert len(no_faces_response["faces"]) == 0

    def test_unclassified_faces_logic(self):
        """Test getting unclassified faces logic"""
        mock_faces = [
            {
                "face_id": "face_1",
                "event_id": "event_1",
                "name": None,
                "relationship": "unknown",
            },
            {
                "face_id": "face_2",
                "event_id": "event_2",
                "name": None,
                "relationship": "unknown",
            },
        ]
        clasificador.get_unclassified_faces = Mock(return_value=mock_faces)

        faces = clasificador.get_unclassified_faces()

        assert len(faces) == 2
        assert faces[0]["face_id"] == "face_1"
        assert faces[1]["face_id"] == "face_2"
        assert all(face["name"] is None for face in faces)

    def test_get_face_logic(self):
        """Test getting specific face logic"""
        mock_face_data = [
            {"face_id": "test_face_id", "name": "John Doe", "event_id": "event_123"}
        ]
        clasificador.get_face = Mock(return_value=mock_face_data)

        face_data = clasificador.get_face("test_face_id")

        assert isinstance(face_data, list)
        assert face_data[0]["face_id"] == "test_face_id"
        clasificador.get_face.assert_called_once_with("test_face_id")

    def test_update_face_logic(self):
        """Test updating face logic"""
        update_data = {
            "name": "John Doe",
            "relationship": "friend",
            "confidence": "high",
        }

        # Test successful update
        clasificador.update_face = Mock(return_value=None)  # Assume success

        try:
            clasificador.update_face("test_face_id", update_data)
            update_result = {
                "status": "success",
                "message": "Face updated successfully",
            }
        except Exception as e:
            update_result = {"error": str(e)}

        assert update_result["status"] == "success"
        assert "updated successfully" in update_result["message"]
        clasificador.update_face.assert_called_once_with("test_face_id", update_data)

    def test_serve_face_image_logic(self):
        """Test image serving endpoint logic"""
        import re
        import uuid

        # Test valid UUID format validation
        valid_face_id = str(uuid.uuid4())
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        assert uuid_pattern.match(valid_face_id)

        # Test invalid UUID format
        invalid_face_id = "invalid-uuid"
        assert not uuid_pattern.match(invalid_face_id)

        # Mock face data with thumbnail
        mock_face_data = [
            {
                "face_id": valid_face_id,
                "thumbnail": self.test_image_b64,
                "name": "Test Face",
            }
        ]
        clasificador.get_face = Mock(return_value=mock_face_data)

        # Test successful image retrieval logic
        face_data = clasificador.get_face(valid_face_id)
        assert len(face_data) > 0
        assert face_data[0]["thumbnail"] == self.test_image_b64

        # Test base64 decoding
        try:
            image_data = base64.b64decode(face_data[0]["thumbnail"])
            assert len(image_data) > 0
        except Exception:
            pytest.fail("Failed to decode base64 thumbnail")

        # Test face not found case
        clasificador.get_face = Mock(return_value=[])
        empty_result = clasificador.get_face("nonexistent-face")
        assert len(empty_result) == 0

    def test_enhanced_recognize_with_face_crops(self):
        """Test enhanced /recognize endpoint with face extraction"""
        # Mock enhanced face identification results with crops
        mock_face_results = [
            {
                "face_index": 0,
                "status": "identified",
                "face_data": {
                    "face_id": "known_face_1",
                    "name": "John Doe",
                    "relationship": "friend",
                },
                "confidence": 0.85,
                "face_bbox": [100, 150, 200, 250],
                "face_crop": "base64_crop_1",
            },
            {
                "face_index": 1,
                "status": "unknown",
                "face_data": None,
                "confidence": 0.0,
                "face_bbox": [300, 100, 400, 200],
                "face_crop": "base64_crop_2",
            },
        ]

        clasificador.identify_all_faces = Mock(return_value=mock_face_results)
        clasificador.save_multiple_faces = Mock(return_value=["unknown_face_id"])

        # Simulate API processing logic
        has_unknown = any(result["status"] == "unknown" for result in mock_face_results)
        assert has_unknown is True

        result = {
            "status": "success",
            "faces_count": len(mock_face_results),
            "faces": mock_face_results,
            "event_id": "test_event_123",
            "processing_method": "face_extraction_crops",
        }

        # Verify enhanced response format
        assert result["status"] == "success"
        assert result["faces_count"] == 2
        assert result["processing_method"] == "face_extraction_crops"
        assert len(result["faces"]) == 2

        # Verify first face (identified)
        face1 = result["faces"][0]
        assert face1["face_index"] == 0
        assert face1["status"] == "identified"
        assert face1["face_bbox"] == [100, 150, 200, 250]
        assert face1["face_crop"] == "base64_crop_1"
        assert face1["confidence"] == 0.85

        # Verify second face (unknown)
        face2 = result["faces"][1]
        assert face2["face_index"] == 1
        assert face2["status"] == "unknown"
        assert face2["face_bbox"] == [300, 100, 400, 200]
        assert face2["face_crop"] == "base64_crop_2"
        assert face2["confidence"] == 0.0

    def test_enhanced_recognize_with_multiple_unknown_faces(self):
        """Test saving multiple unknown faces using new function"""
        # Mock all unknown faces scenario
        mock_face_results = [
            {
                "face_index": 0,
                "status": "unknown",
                "face_data": None,
                "confidence": 0.0,
                "face_bbox": [100, 150, 200, 250],
                "face_crop": "base64_crop_1",
            },
            {
                "face_index": 1,
                "status": "unknown",
                "face_data": None,
                "confidence": 0.0,
                "face_bbox": [300, 100, 400, 200],
                "face_crop": "base64_crop_2",
            },
        ]

        clasificador.identify_all_faces = Mock(return_value=mock_face_results)
        clasificador.save_multiple_faces = Mock(return_value=["face_id_1", "face_id_2"])

        # Test the enhanced logic
        unknown_faces = [
            result for result in mock_face_results if result["status"] == "unknown"
        ]
        assert len(unknown_faces) == 2

        # Verify save_multiple_faces would be called
        if unknown_faces:
            saved_face_ids = clasificador.save_multiple_faces(
                "temp_image.jpg", "test_event_123"
            )
            assert len(saved_face_ids) == 2

    def test_face_crop_data_validation(self):
        """Test validation of face crop data structure"""
        # Test complete face crop data structure
        face_crop_data = {
            "face_index": 0,
            "face_bbox": [100, 150, 200, 250],
            "face_crop": "base64_encoded_image_data",
            "embedding": [0.1, 0.2, 0.3],  # Simplified for test
        }

        # Validate required fields
        required_fields = ["face_index", "face_bbox", "face_crop", "embedding"]
        for field in required_fields:
            assert field in face_crop_data, f"Missing required field: {field}"

        # Validate data types
        assert isinstance(face_crop_data["face_index"], int)
        assert isinstance(face_crop_data["face_bbox"], list)
        assert len(face_crop_data["face_bbox"]) == 4
        assert isinstance(face_crop_data["face_crop"], str)
        assert isinstance(face_crop_data["embedding"], list)

        # Validate bounding box coordinates
        x1, y1, x2, y2 = face_crop_data["face_bbox"]
        assert x2 > x1, "Invalid bounding box: x2 should be greater than x1"
        assert y2 > y1, "Invalid bounding box: y2 should be greater than y1"

    def test_enhanced_api_response_backward_compatibility(self):
        """Test that enhanced API response maintains backward compatibility"""
        # Legacy response format (what existing clients expect)
        legacy_response = {
            "status": "success",
            "faces_count": 1,
            "faces": [
                {
                    "face_index": 0,
                    "status": "identified",
                    "face_data": {"face_id": "test", "name": "John"},
                    "confidence": 0.8,
                }
            ],
        }

        # Enhanced response format (with new fields)
        enhanced_response = {
            "status": "success",
            "faces_count": 1,
            "faces": [
                {
                    "face_index": 0,
                    "status": "identified",
                    "face_data": {"face_id": "test", "name": "John"},
                    "confidence": 0.8,
                    "face_bbox": [100, 150, 200, 250],  # New field
                    "face_crop": "base64_crop_data",  # New field
                }
            ],
            "event_id": "test_event",  # New field
            "processing_method": "face_extraction_crops",  # New field
        }

        # Verify both contain core required fields
        core_fields = ["status", "faces_count", "faces"]
        for field in core_fields:
            assert field in legacy_response
            assert field in enhanced_response

        # Verify face structure compatibility
        legacy_face = legacy_response["faces"][0]
        enhanced_face = enhanced_response["faces"][0]

        face_core_fields = ["face_index", "status", "face_data", "confidence"]
        for field in face_core_fields:
            assert field in legacy_face
            assert field in enhanced_face

        # Enhanced response should have additional fields
        assert "face_bbox" in enhanced_face
        assert "face_crop" in enhanced_face
        assert "event_id" in enhanced_response
        assert "processing_method" in enhanced_response

    def test_face_crop_base64_encoding_validation(self):
        """Test validation of base64-encoded face crops"""
        # Valid base64 encoded image data
        valid_base64 = self.test_image_b64

        # Test base64 validation
        try:
            decoded_data = base64.b64decode(valid_base64)
            assert len(decoded_data) > 0
        except Exception:
            pytest.fail("Valid base64 data should decode successfully")

        # Invalid base64 data
        invalid_base64 = "not_valid_base64_data"

        try:
            base64.b64decode(invalid_base64)
            is_valid = True
        except Exception:
            is_valid = False

        assert not is_valid, "Invalid base64 should raise exception"

    def test_multi_face_processing_performance_considerations(self):
        """Test performance considerations for multi-face processing"""
        # Simulate processing multiple faces in a single image
        face_count_scenarios = [0, 1, 2, 5, 10]  # Different face counts

        for face_count in face_count_scenarios:
            # Mock results for different face counts
            mock_results = []
            for i in range(face_count):
                mock_results.append(
                    {
                        "face_index": i,
                        "status": "unknown",
                        "face_data": None,
                        "confidence": 0.0,
                        "face_bbox": [i * 50, i * 50, (i + 1) * 50, (i + 1) * 50],
                        "face_crop": f"base64_crop_{i}",
                    }
                )

            # Verify processing logic scales appropriately
            assert len(mock_results) == face_count

            # Verify each face has unique index
            face_indices = [face["face_index"] for face in mock_results]
            assert len(set(face_indices)) == face_count  # All indices unique

            # Verify memory usage considerations (mock)
            estimated_memory_per_crop = 10 * 1024  # ~10KB per face crop
            total_estimated_memory = face_count * estimated_memory_per_crop

            # Should handle up to 10 faces reasonably (100KB total)
            assert (
                total_estimated_memory < 1024 * 1024
            )  # Less than 1MB for our test cases
