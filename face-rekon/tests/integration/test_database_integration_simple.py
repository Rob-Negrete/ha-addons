"""
Simplified integration tests for Qdrant database operations.
Tests essential functionality with the new Qdrant-only architecture.
"""
import numpy as np
import pytest


@pytest.mark.integration
class TestQdrantIntegration:
    """Essential integration tests for Qdrant operations"""

    def test_qdrant_adapter_initialization(self, shared_ml_models):
        """Test that Qdrant adapter can be initialized and accessed"""
        clasificador = shared_ml_models["clasificador"]

        # Verify Qdrant adapter exists and is functional
        assert hasattr(clasificador, "get_qdrant_adapter")
        qdrant_adapter = clasificador.get_qdrant_adapter()
        assert qdrant_adapter is not None
        assert hasattr(qdrant_adapter, "save_face")
        assert hasattr(qdrant_adapter, "search_similar_faces")

    def test_face_operations_workflow(self, shared_ml_models):
        """Test complete face save/retrieve/update workflow"""
        clasificador = shared_ml_models["clasificador"]

        # Test data
        test_face_data = {
            "face_id": "integration_test_face",
            "event_id": "integration_test_event",
            "timestamp": 1234567890,
            "name": "unknown",
            "relationship": "unknown",
            "confidence": "unknown",
            "thumbnail": "dGVzdF90aHVtYm5haWw=",
        }
        test_embedding = np.random.random(512).astype(np.float32)

        # Clear any existing data for this face
        try:
            clasificador.get_face(test_face_data["face_id"])
        except Exception:
            pass  # Face doesn't exist, which is fine

        # 1. Save face
        face_id = clasificador.db_save_face(test_face_data, test_embedding)
        assert face_id is not None

        # 2. Retrieve face
        retrieved_face = clasificador.get_face(test_face_data["face_id"])
        assert retrieved_face is not None
        assert retrieved_face["face_id"] == test_face_data["face_id"]

        # 3. Update face
        update_data = {
            "name": "Test Person",
            "relationship": "friend",
            "confidence": "high",
        }
        clasificador.update_face(test_face_data["face_id"], update_data)

        # 4. Verify update
        updated_face = clasificador.get_face(test_face_data["face_id"])
        assert updated_face["name"] == "Test Person"
        assert updated_face["relationship"] == "friend"
        assert updated_face["confidence"] == "high"

    def test_unclassified_faces_functionality(self, shared_ml_models):
        """Test getting unclassified faces"""
        clasificador = shared_ml_models["clasificador"]

        # This should work without errors
        unclassified_faces = clasificador.get_unclassified_faces()
        assert isinstance(unclassified_faces, list)
        # We don't assert length since other tests might have added faces
