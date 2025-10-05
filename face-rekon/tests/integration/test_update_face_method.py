"""
Integration tests for update_face method in qdrant_adapter.py.
Achieves 100% coverage for the update_face function (lines 260-308).

These tests run in Docker with real ML dependencies and Qdrant.
Tests cover all code paths: success, face not found, and exception handling.
"""

import time
import uuid

import numpy as np
import pytest


@pytest.mark.integration
class TestUpdateFaceMethodCoverage:
    """Comprehensive tests for update_face method to achieve 100% coverage"""

    def test_update_face_success_path(self, qdrant_adapter):
        """
        Test successful face update with real Qdrant operations.
        Covers lines: 271-284, 290-292, 294-296, 298-304
        """
        try:
            adapter = qdrant_adapter

            # Create a face to update
            face_id = str(uuid.uuid4())
            embedding = np.random.rand(512).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)

            face_data = {
                "face_id": face_id,
                "event_id": f"test_update_success_{int(time.time())}",
                "detected_at": int(time.time()),
                "confidence": 0.95,
                "name": "Original Name",
                "relationship": "unknown",
            }

            # Save the face first
            saved_id = adapter.save_face(face_data, embedding)
            assert saved_id == face_id

            # Now update the face with new data
            updates = {
                "name": "Updated Name",
                "relationship": "friend",
                "tags": ["test"],
            }

            result = adapter.update_face(face_id, updates)

            # Verify update succeeded
            assert result is True

            # Verify the face was actually updated
            updated_face = adapter.get_face(face_id)
            assert updated_face is not None
            assert updated_face["name"] == "Updated Name"
            assert updated_face["relationship"] == "friend"
            assert updated_face["tags"] == ["test"]
            assert "updated_at" in updated_face  # Should have timestamp

            print(f"✅ update_face success path: {face_id}")

        except ImportError:
            pytest.skip("Qdrant adapter not available")

    def test_update_face_not_found(self, qdrant_adapter):
        """
        Test update_face when face_id does not exist.
        Covers lines: 271-284, 286-288 (face not found case)
        """
        try:
            adapter = qdrant_adapter

            # Try to update a non-existent face
            fake_face_id = str(uuid.uuid4())
            updates = {"name": "Should Not Update", "relationship": "test"}

            result = adapter.update_face(fake_face_id, updates)

            # Should return False for non-existent face
            assert result is False

            print(f"✅ update_face not found: {fake_face_id}")

        except ImportError:
            pytest.skip("Qdrant adapter not available")

    def test_update_face_exception_handling(self, qdrant_adapter):
        """
        Test update_face exception handling with invalid parameters.
        Covers lines: 306-308 (exception handler)
        """
        try:
            adapter = qdrant_adapter

            # Test with invalid face_id type (should trigger exception)
            # Qdrant expects string face_id, pass None to trigger exception
            result = adapter.update_face(None, {"name": "Test"})

            # Should return False on exception
            assert result is False

            print("✅ update_face exception handling: invalid parameters")

        except ImportError:
            pytest.skip("Qdrant adapter not available")

    def test_update_face_multiple_fields(self, qdrant_adapter):
        """
        Test updating multiple fields at once.
        Additional coverage for lines: 294-296 (merge updates logic)
        """
        try:
            adapter = qdrant_adapter

            # Create a face with initial data
            face_id = str(uuid.uuid4())
            embedding = np.random.rand(512).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)

            face_data = {
                "face_id": face_id,
                "event_id": f"test_update_multiple_{int(time.time())}",
                "detected_at": int(time.time()),
                "confidence": 0.92,
                "name": "John",
                "relationship": "unknown",
                "location": "camera_1",
            }

            # Save the face
            saved_id = adapter.save_face(face_data, embedding)
            assert saved_id == face_id

            # Update multiple fields
            updates = {
                "name": "John Doe",
                "relationship": "family",
                "location": "camera_2",
                "notes": "Added notes field",
                "verified": True,
            }

            result = adapter.update_face(face_id, updates)
            assert result is True

            # Verify all fields were updated
            updated_face = adapter.get_face(face_id)
            assert updated_face["name"] == "John Doe"
            assert updated_face["relationship"] == "family"
            assert updated_face["location"] == "camera_2"
            assert updated_face["notes"] == "Added notes field"
            assert updated_face["verified"] is True

            print(f"✅ update_face multiple fields: {face_id}")

        except ImportError:
            pytest.skip("Qdrant adapter not available")

    def test_update_face_preserves_existing_fields(self, qdrant_adapter):
        """
        Test that update_face preserves fields not included in updates.
        Covers lines: 290-296 (merge logic preserves existing data)
        """
        try:
            adapter = qdrant_adapter

            # Create a face with multiple fields (using fields save_face actually saves)
            face_id = str(uuid.uuid4())
            embedding = np.random.rand(512).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)

            face_data = {
                "face_id": face_id,
                "event_id": f"test_update_preserve_{int(time.time())}",
                "timestamp": int(time.time() * 1000),
                "confidence": 0.88,
                "name": "Alice",
                "notes": "Original notes",
                "face_bbox": [100, 200, 150, 250],
            }

            # Save the face
            saved_id = adapter.save_face(face_data, embedding)
            assert saved_id == face_id

            # Update only name, other fields should be preserved
            updates = {"name": "Alice Johnson"}

            result = adapter.update_face(face_id, updates)
            assert result is True

            # Verify name was updated but other fields preserved
            updated_face = adapter.get_face(face_id)
            assert updated_face["name"] == "Alice Johnson"  # Updated
            assert updated_face["notes"] == "Original notes"  # Preserved
            assert updated_face["confidence"] == 0.88  # Preserved
            assert updated_face["face_bbox"] == [100, 200, 150, 250]  # Preserved
            assert updated_face["event_id"] == face_data["event_id"]  # Preserved

            print(f"✅ update_face preserves fields: {face_id}")

        except ImportError:
            pytest.skip("Qdrant adapter not available")

    def test_update_face_timestamp_added(self, qdrant_adapter):
        """
        Test that update_face adds updated_at timestamp.
        Covers lines: 296 (timestamp addition)
        """
        try:
            adapter = qdrant_adapter

            # Create a face
            face_id = str(uuid.uuid4())
            embedding = np.random.rand(512).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)

            face_data = {
                "face_id": face_id,
                "event_id": f"test_update_timestamp_{int(time.time())}",
                "detected_at": int(time.time()),
                "confidence": 0.91,
            }

            # Save the face
            saved_id = adapter.save_face(face_data, embedding)
            assert saved_id == face_id

            # Record time before update
            before_update = int(time.time())

            # Small delay to ensure timestamp difference
            time.sleep(0.1)

            # Update the face
            updates = {"name": "Test User"}
            result = adapter.update_face(face_id, updates)
            assert result is True

            # Verify updated_at timestamp was added and is recent
            updated_face = adapter.get_face(face_id)
            assert "updated_at" in updated_face
            assert updated_face["updated_at"] >= before_update
            assert updated_face["updated_at"] <= int(time.time()) + 1

            print(f"✅ update_face timestamp: {face_id}")

        except ImportError:
            pytest.skip("Qdrant adapter not available")

    def test_update_face_empty_updates(self, qdrant_adapter):
        """
        Test update_face with empty updates dictionary.
        Edge case: updates={} should still succeed and add timestamp.
        """
        try:
            adapter = qdrant_adapter

            # Create a face
            face_id = str(uuid.uuid4())
            embedding = np.random.rand(512).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)

            face_data = {
                "face_id": face_id,
                "event_id": f"test_update_empty_{int(time.time())}",
                "detected_at": int(time.time()),
                "confidence": 0.89,
                "name": "Empty Update Test",
            }

            # Save the face
            saved_id = adapter.save_face(face_data, embedding)
            assert saved_id == face_id

            # Update with empty dictionary
            result = adapter.update_face(face_id, {})

            # Should succeed and add timestamp
            assert result is True

            # Verify face still exists with timestamp
            updated_face = adapter.get_face(face_id)
            assert updated_face is not None
            assert updated_face["name"] == "Empty Update Test"  # Unchanged
            assert "updated_at" in updated_face  # Timestamp added

            print(f"✅ update_face empty updates: {face_id}")

        except ImportError:
            pytest.skip("Qdrant adapter not available")
