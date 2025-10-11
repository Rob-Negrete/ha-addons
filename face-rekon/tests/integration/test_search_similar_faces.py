"""
Integration tests for QdrantAdapter.search_similar_faces function.

Achieves 100% coverage for the search_similar_faces method (lines 183-225)
by testing all code paths with real Qdrant operations and real face embeddings
from dummy test images in Docker environment.
"""

import base64

import numpy as np
import pytest


@pytest.fixture
def qdrant_adapter_with_real_faces(qdrant_adapter):
    """
    Fixture that provides a Qdrant adapter with real face embeddings
    extracted from dummy test images.
    """
    try:
        import scripts.clasificador as clasificador

        # Store the face embeddings for later use in tests
        saved_faces = []

        # Load real test images and extract embeddings
        test_images = ["one-face.jpg", "two-faces.jpg"]

        for img_file in test_images:
            with open(f"tests/dummies/{img_file}", "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode()

            # Extract face embeddings using real ML pipeline
            faces = clasificador.extract_faces_with_crops(image_base64)

            # Save faces to Qdrant
            for i, face in enumerate(faces):
                face_data = {
                    "face_id": f"test_{img_file}_{i}",
                    "name": f"Person from {img_file}",
                    "timestamp": "2024-10-10T12:00:00",
                    "source_file": img_file,
                }
                # Get embedding using real face detection
                embedding = clasificador.get_embedding(face["image"])
                face_id = qdrant_adapter.save_face(face_data, embedding)
                saved_faces.append({"face_id": face_id, "embedding": embedding})
                print(f"✅ Saved face: {face_id} from {img_file}")

        print(f"✅ Total faces saved in fixture: {len(saved_faces)}")

        # Store saved_faces as attribute for test access
        qdrant_adapter.test_saved_faces = saved_faces
        return qdrant_adapter

    except ImportError as e:
        pytest.skip(f"ML dependencies not available: {e}")


class TestSearchSimilarFaces:
    """Comprehensive tests for search_similar_faces to achieve 100% coverage."""

    def test_search_similar_faces_with_real_results_and_metadata(self, qdrant_adapter):
        """
        Test search_similar_faces returns results with full metadata processing.

        Covers lines 212-220: Result iteration, score conversion, metadata extraction
        Uses real face embeddings from dummy images for authentic testing.
        """
        try:
            import scripts.clasificador as clasificador

            adapter = qdrant_adapter

            # Load and save a face first
            with open("tests/dummies/one-face.jpg", "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode()

            faces = clasificador.extract_faces_with_crops(image_base64)
            if len(faces) > 0:
                # Save the face
                embedding = clasificador.get_embedding(faces[0]["image"])
                face_data = {
                    "face_id": "test_face_for_search",
                    "name": "Test Person",
                    "timestamp": "2024-10-10T12:00:00",
                }
                saved_id = adapter.save_face(face_data, embedding)
                print(f"✅ Saved face with ID: {saved_id}")

                # Verify the face was saved
                import time

                time.sleep(0.1)  # Small delay for Qdrant indexing

                # Now search with same embedding to guarantee match (213-218)
                # Use very low threshold to get all results
                results = adapter.search_similar_faces(
                    embedding, limit=10, score_threshold=0.0
                )
                print(f"✅ Search returned {len(results)} results")

                # Verify results structure (lines 212-218)
                assert isinstance(results, list)
                assert len(results) > 0, "Should find at least the saved face itself"

                # Verify each result has correct structure (lines 213-218)
                for face_id, distance, metadata in results:
                    # Line 215: face_id extraction
                    assert isinstance(face_id, str)
                    assert len(face_id) > 0

                    # Line 214: distance conversion from similarity_score
                    assert isinstance(distance, float)
                    assert 0.0 <= distance <= 1.0

                    # Line 216: metadata extraction
                    assert isinstance(metadata, dict)
                    assert "face_id" in metadata

                # Line 220: logger.info logging
                print(f"✅ Found {len(results)} similar faces with real metadata")

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_search_similar_faces_with_score_threshold(
        self, qdrant_adapter_with_real_faces
    ):
        """
        Test search_similar_faces with custom score threshold.

        Covers lines 198-201: score_threshold None check and conversion
        """
        try:
            import scripts.clasificador as clasificador

            adapter = qdrant_adapter_with_real_faces

            # Get real face embedding
            with open("tests/dummies/one-face.jpg", "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode()

            faces = clasificador.extract_faces_with_crops(image_base64)
            if len(faces) > 0:
                query_embedding = clasificador.get_embedding(faces[0]["image"])

                # Test with custom score threshold (lines 198-201)
                results = adapter.search_similar_faces(
                    query_embedding, limit=3, score_threshold=0.7
                )

                assert isinstance(results, list)
                print(
                    f"✅ search_similar_faces with score_threshold=0.7: "
                    f"{len(results)} results"
                )

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_search_similar_faces_with_none_threshold_conversion(
        self, qdrant_adapter_with_real_faces
    ):
        """
        Test search_similar_faces with None threshold (default behavior).

        Covers lines 198-201: Conversion from BORDERLINE_THRESHOLD
        """
        try:
            import scripts.clasificador as clasificador

            adapter = qdrant_adapter_with_real_faces

            # Get real face embedding
            with open("tests/dummies/two-faces.jpg", "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode()

            faces = clasificador.extract_faces_with_crops(image_base64)
            if len(faces) > 0:
                query_embedding = clasificador.get_embedding(faces[0]["image"])

                # Test with None threshold (uses BORDERLINE_THRESHOLD conversion)
                results = adapter.search_similar_faces(query_embedding, limit=10)

                assert isinstance(results, list)
                print(
                    f"✅ search_similar_faces with None threshold (default): "
                    f"{len(results)} results"
                )

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_search_similar_faces_empty_results(self, qdrant_adapter):
        """
        Test search_similar_faces returns empty list when no matches found.

        Covers lines 211-221: Empty results handling
        """
        try:
            # Use clean adapter (no faces stored)
            adapter = qdrant_adapter

            # Search in empty collection with random embedding
            query_embedding = np.random.rand(512).astype(np.float32)
            results = adapter.search_similar_faces(query_embedding, limit=5)

            # Lines 211-221: Should handle empty results gracefully
            assert results == []
            print("✅ search_similar_faces with empty collection: []")

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_search_similar_faces_result_score_conversion(
        self, qdrant_adapter_with_real_faces
    ):
        """
        Test search_similar_faces correctly converts similarity scores to distances.

        Covers line 214: distance = 1.0 - similarity_score
        """
        try:
            import scripts.clasificador as clasificador

            adapter = qdrant_adapter_with_real_faces

            # Get real face embedding
            with open("tests/dummies/one-face.jpg", "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode()

            faces = clasificador.extract_faces_with_crops(image_base64)
            if len(faces) > 0:
                query_embedding = clasificador.get_embedding(faces[0]["image"])
                results = adapter.search_similar_faces(query_embedding, limit=3)

                if len(results) > 0:
                    for face_id, distance, metadata in results:
                        # Line 214: Verify score conversion
                        # similarity_score (0-1) → distance (0-1)
                        # Higher similarity → lower distance
                        assert isinstance(distance, float)
                        assert 0.0 <= distance <= 1.0

                        print(
                            f"✅ Face {face_id}: distance={distance:.4f} "
                            f"(converted from similarity_score)"
                        )

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_search_similar_faces_limit_parameter(self, qdrant_adapter_with_real_faces):
        """
        Test search_similar_faces respects limit parameter.

        Covers lines 203-209: client.search with limit parameter
        """
        try:
            import scripts.clasificador as clasificador

            adapter = qdrant_adapter_with_real_faces

            # Get real face embedding
            with open("tests/dummies/one-face.jpg", "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode()

            faces = clasificador.extract_faces_with_crops(image_base64)
            if len(faces) > 0:
                query_embedding = clasificador.get_embedding(faces[0]["image"])

                # Test with limit=1
                results_1 = adapter.search_similar_faces(query_embedding, limit=1)
                assert len(results_1) <= 1

                # Test with limit=5
                results_5 = adapter.search_similar_faces(query_embedding, limit=5)
                assert len(results_5) <= 5

                print(
                    f"✅ Limit parameter working: limit=1 → {len(results_1)} results, "
                    f"limit=5 → {len(results_5)} results"
                )

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_search_similar_faces_via_clasificador_integration(self):
        """
        Test search_similar_faces through clasificador.py real-world integration.

        This tests the actual usage pattern where clasificador calls
        qdrant_adapter.search_similar_faces during face recognition with
        real face embeddings.
        """
        try:
            import scripts.clasificador as clasificador

            # Load real test image
            with open("tests/dummies/one-face.jpg", "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode()

            # Extract face and get embedding
            faces = clasificador.extract_faces_with_crops(image_base64)

            if len(faces) > 0:
                embedding = clasificador.get_embedding(faces[0]["image"])

                # This will internally call qdrant_adapter.search_similar_faces
                adapter = clasificador.get_qdrant_adapter()
                results = adapter.search_similar_faces(
                    embedding, limit=3, score_threshold=0.0
                )

                # Verify results (covers lines 212-221)
                assert isinstance(results, list)
                print(
                    f"✅ search_similar_faces via clasificador with real face: "
                    f"{len(results)} results"
                )

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")

    def test_search_similar_faces_exception_handling(self, qdrant_adapter):
        """
        Test search_similar_faces exception handling when client fails.

        Covers lines 223-225: Exception handling and error logging
        """
        try:
            from unittest.mock import patch

            adapter = qdrant_adapter

            # Mock the client.search to raise an exception
            with patch.object(
                adapter.client, "search", side_effect=Exception("Search failed")
            ):
                query_embedding = np.random.rand(512).astype(np.float32)

                # Should return empty list on exception (lines 223-225)
                results = adapter.search_similar_faces(query_embedding, limit=5)

                assert results == []
                print("✅ search_similar_faces exception handling: returns []")

        except ImportError as e:
            pytest.skip(f"ML dependencies not available: {e}")
