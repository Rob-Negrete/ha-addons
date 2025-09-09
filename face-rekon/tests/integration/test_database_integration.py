"""
Integration tests for database operations.
Tests real TinyDB operations with FAISS index management.
"""
import pytest
import os
import sys
import numpy as np
import tempfile
import shutil
from unittest.mock import patch, Mock
from pathlib import Path

# Add scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations with real TinyDB"""
    
    def test_database_initialization(self, clean_test_env):
        """
        Integration test: Initialize TinyDB database and FAISS index
        """
        with patch('clasificador.BASE_PATH', clean_test_env['base_path']), \
             patch('clasificador.DB_PATH', clean_test_env['db_path']), \
             patch('clasificador.FAISS_INDEX_PATH', clean_test_env['faiss_index_path']), \
             patch('clasificador.MAPPING_PATH', clean_test_env['mapping_path']), \
             patch('clasificador.app'), \
             patch('clasificador.faiss') as mock_faiss:
            
            # Mock FAISS operations
            mock_index = Mock()
            mock_faiss.IndexFlatL2.return_value = mock_index
            mock_faiss.read_index.return_value = mock_index
            
            # Import after patching
            import clasificador
            
            # Verify database file creation
            assert os.path.exists(os.path.dirname(clean_test_env['db_path']))
            
            # Verify FAISS index initialization
            mock_faiss.IndexFlatL2.assert_called_with(512)  # 512-dimensional embeddings

    @patch('clasificador.app')
    @patch('clasificador.faiss')
    def test_save_unknown_face_database_integration(self, mock_faiss, mock_insightface, 
                                                   clean_test_env, test_images):
        """
        Integration test: Save unknown face to real database
        """
        # Setup mocks
        mock_insightface_instance = Mock()
        mock_embedding = np.random.random(512).astype(np.float32)
        mock_insightface_instance.get.return_value = [Mock(embedding=mock_embedding)]
        mock_insightface.return_value = mock_insightface_instance
        
        mock_index = Mock()
        mock_faiss.IndexFlatL2.return_value = mock_index
        mock_faiss.read_index.return_value = mock_index
        mock_faiss.write_index = Mock()
        
        with patch('clasificador.BASE_PATH', clean_test_env['base_path']), \
             patch('clasificador.UNKNOWN_PATH', clean_test_env['unknown_path']), \
             patch('clasificador.DB_PATH', clean_test_env['db_path']), \
             patch('clasificador.FAISS_INDEX_PATH', clean_test_env['faiss_index_path']), \
             patch('clasificador.MAPPING_PATH', clean_test_env['mapping_path']), \
             patch('clasificador.app', mock_insightface_instance):
            
            # Create a real test image file
            test_image = test_images['red_square']
            test_image_path = os.path.join(clean_test_env['tmp_path'], 'test_face.jpg')
            
            # Save test image to file system
            from PIL import Image
            img = Image.new('RGB', (200, 200), 'red')
            img.save(test_image_path)
            
            # Import and test
            import clasificador
            
            # Save unknown face
            clasificador.save_unknown_face(test_image_path, 'integration_test_event')
            
            # Verify database operations
            mock_index.add.assert_called_once()
            mock_faiss.write_index.assert_called_once()
            
            # Verify database record exists
            records = clasificador.db.all()
            assert len(records) == 1
            
            record = records[0]
            assert record['event_id'] == 'integration_test_event'
            assert record['name'] is None
            assert record['relationship'] == 'unknown'
            assert 'face_id' in record
            assert 'timestamp' in record
            assert 'thumbnail' in record

    @patch('clasificador.app')
    @patch('clasificador.faiss')
    def test_identify_face_database_integration(self, mock_faiss, mock_insightface,
                                              clean_test_env, known_face_data, test_images):
        """
        Integration test: Identify face using real database lookup
        """
        # Setup mocks
        mock_insightface_instance = Mock()
        mock_embedding = np.random.random(512).astype(np.float32)
        mock_insightface_instance.get.return_value = [Mock(embedding=mock_embedding)]
        
        mock_index = Mock()
        # Mock FAISS to return a match
        mock_index.search.return_value = (np.array([[0.3]]), np.array([[0]]))
        mock_faiss.IndexFlatL2.return_value = mock_index
        mock_faiss.read_index.return_value = mock_index
        
        with patch('clasificador.BASE_PATH', clean_test_env['base_path']), \
             patch('clasificador.DB_PATH', clean_test_env['db_path']), \
             patch('clasificador.FAISS_INDEX_PATH', clean_test_env['faiss_index_path']), \
             patch('clasificador.MAPPING_PATH', clean_test_env['mapping_path']), \
             patch('clasificador.app', mock_insightface_instance):
            
            import clasificador
            
            # Insert known face into database
            clasificador.db.insert(known_face_data)
            
            # Mock id_map to return the face_id
            clasificador.id_map = [known_face_data['face_id']]
            
            # Create test image
            test_image_path = os.path.join(clean_test_env['tmp_path'], 'known_face.jpg')
            from PIL import Image
            img = Image.new('RGB', (200, 200), 'blue')
            img.save(test_image_path)
            
            # Test identification
            result = clasificador.identify_face(test_image_path)
            
            # Verify identification worked
            assert result is not None
            assert result['face_id'] == known_face_data['face_id']
            assert result['name'] == 'John Doe'
            assert result['relationship'] == 'friend'

    @patch('clasificador.app')
    @patch('clasificador.faiss')
    def test_get_unclassified_faces_database_integration(self, mock_faiss, mock_insightface,
                                                       clean_test_env, sample_face_data):
        """
        Integration test: Get unclassified faces from real database
        """
        with patch('clasificador.BASE_PATH', clean_test_env['base_path']), \
             patch('clasificador.DB_PATH', clean_test_env['db_path']), \
             patch('clasificador.FAISS_INDEX_PATH', clean_test_env['faiss_index_path']), \
             patch('clasificador.MAPPING_PATH', clean_test_env['mapping_path']):
            
            mock_index = Mock()
            mock_faiss.IndexFlatL2.return_value = mock_index
            
            import clasificador
            
            # Insert test data - mix of classified and unclassified
            test_faces = [
                {**sample_face_data, 'face_id': 'unclassified_1', 'name': None},
                {**sample_face_data, 'face_id': 'classified_1', 'name': 'John Doe'},
                {**sample_face_data, 'face_id': 'unclassified_2', 'name': None},
                {**sample_face_data, 'face_id': 'classified_2', 'name': 'Jane Smith'}
            ]
            
            for face in test_faces:
                clasificador.db.insert(face)
            
            # Get unclassified faces
            unclassified = clasificador.get_unclassified_faces()
            
            # Verify results
            assert len(unclassified) == 2
            unclassified_ids = [face['face_id'] for face in unclassified]
            assert 'unclassified_1' in unclassified_ids
            assert 'unclassified_2' in unclassified_ids
            assert all(face['name'] is None for face in unclassified)

    @patch('clasificador.app')
    @patch('clasificador.faiss')
    def test_update_face_database_integration(self, mock_faiss, mock_insightface,
                                            clean_test_env, sample_face_data):
        """
        Integration test: Update face information in real database
        """
        with patch('clasificador.BASE_PATH', clean_test_env['base_path']), \
             patch('clasificador.DB_PATH', clean_test_env['db_path']), \
             patch('clasificador.FAISS_INDEX_PATH', clean_test_env['faiss_index_path']), \
             patch('clasificador.MAPPING_PATH', clean_test_env['mapping_path']):
            
            mock_index = Mock()
            mock_faiss.IndexFlatL2.return_value = mock_index
            
            import clasificador
            
            # Insert unclassified face
            clasificador.db.insert(sample_face_data)
            
            # Update face information
            update_data = {
                'name': 'Updated Name',
                'relationship': 'family',
                'confidence': 'high'
            }
            
            clasificador.update_face(sample_face_data['face_id'], update_data)
            
            # Verify update
            updated_face = clasificador.db.get(clasificador.Face.face_id == sample_face_data['face_id'])
            
            assert updated_face is not None
            assert updated_face['name'] == 'Updated Name'
            assert updated_face['relationship'] == 'family'
            assert updated_face['confidence'] == 'high'
            # Original data should be preserved
            assert updated_face['event_id'] == sample_face_data['event_id']

    @patch('clasificador.app')
    @patch('clasificador.faiss')
    def test_get_face_database_integration(self, mock_faiss, mock_insightface,
                                         clean_test_env, known_face_data):
        """
        Integration test: Get specific face from real database
        """
        with patch('clasificador.BASE_PATH', clean_test_env['base_path']), \
             patch('clasificador.DB_PATH', clean_test_env['db_path']), \
             patch('clasificador.FAISS_INDEX_PATH', clean_test_env['faiss_index_path']), \
             patch('clasificador.MAPPING_PATH', clean_test_env['mapping_path']):
            
            mock_index = Mock()
            mock_faiss.IndexFlatL2.return_value = mock_index
            
            import clasificador
            
            # Insert test face
            clasificador.db.insert(known_face_data)
            
            # Get face by ID
            result = clasificador.get_face(known_face_data['face_id'])
            
            # Verify result
            assert len(result) == 1
            face = result[0]
            assert face['face_id'] == known_face_data['face_id']
            assert face['name'] == 'John Doe'
            assert face['relationship'] == 'friend'

    @patch('clasificador.app')
    @patch('clasificador.faiss')
    def test_database_persistence_across_operations(self, mock_faiss, mock_insightface,
                                                  clean_test_env, sample_face_data):
        """
        Integration test: Verify database persists data across multiple operations
        """
        with patch('clasificador.BASE_PATH', clean_test_env['base_path']), \
             patch('clasificador.DB_PATH', clean_test_env['db_path']), \
             patch('clasificador.FAISS_INDEX_PATH', clean_test_env['faiss_index_path']), \
             patch('clasificador.MAPPING_PATH', clean_test_env['mapping_path']):
            
            mock_index = Mock()
            mock_faiss.IndexFlatL2.return_value = mock_index
            
            import clasificador
            
            # Perform multiple database operations
            face_1 = {**sample_face_data, 'face_id': 'persist_test_1'}
            face_2 = {**sample_face_data, 'face_id': 'persist_test_2'}
            
            # Insert faces
            clasificador.db.insert(face_1)
            clasificador.db.insert(face_2)
            
            # Update one face
            clasificador.update_face('persist_test_1', {'name': 'Test Person 1'})
            
            # Verify all operations persisted
            all_faces = clasificador.db.all()
            assert len(all_faces) == 2
            
            # Check updated face
            updated_face = clasificador.db.get(clasificador.Face.face_id == 'persist_test_1')
            assert updated_face['name'] == 'Test Person 1'
            
            # Check unchanged face
            unchanged_face = clasificador.db.get(clasificador.Face.face_id == 'persist_test_2')
            assert unchanged_face['name'] is None
            
            # Verify database file exists
            assert os.path.exists(clean_test_env['db_path'])
            assert os.path.getsize(clean_test_env['db_path']) > 0  # File has content


@pytest.mark.integration
@pytest.mark.slow
class TestFAISSIntegration:
    """Integration tests for FAISS index operations"""
    
    @patch('clasificador.app')
    def test_faiss_index_creation_and_search(self, mock_insightface, clean_test_env):
        """
        Integration test: Create FAISS index and perform similarity search
        """
        with patch('clasificador.BASE_PATH', clean_test_env['base_path']), \
             patch('clasificador.DB_PATH', clean_test_env['db_path']), \
             patch('clasificador.FAISS_INDEX_PATH', clean_test_env['faiss_index_path']), \
             patch('clasificador.MAPPING_PATH', clean_test_env['mapping_path']):
            
            # Import with real FAISS (if available, otherwise skip)
            try:
                import faiss
            except ImportError:
                pytest.skip("FAISS not available for integration testing")
            
            import clasificador
            
            # Create test embeddings
            embeddings = [
                np.random.random(512).astype(np.float32),
                np.random.random(512).astype(np.float32),
                np.random.random(512).astype(np.float32)
            ]
            
            face_ids = ['faiss_test_1', 'faiss_test_2', 'faiss_test_3']
            
            # Add embeddings to index
            for i, (embedding, face_id) in enumerate(zip(embeddings, face_ids)):
                clasificador.index.add(np.array([embedding]))
                clasificador.id_map.append(face_id)
            
            # Test search for exact match
            distances, indices = clasificador.index.search(np.array([embeddings[0]]), 1)
            
            # Verify exact match
            assert len(distances[0]) == 1
            assert len(indices[0]) == 1
            assert distances[0][0] < 0.01  # Should be very close to 0
            assert clasificador.id_map[indices[0][0]] == face_ids[0]
            
            # Test search for k=3 neighbors
            distances_k3, indices_k3 = clasificador.index.search(np.array([embeddings[0]]), 3)
            
            # Verify we get 3 results
            assert len(distances_k3[0]) == 3
            assert len(indices_k3[0]) == 3
            
            # First result should still be the exact match
            assert distances_k3[0][0] < 0.01
            assert clasificador.id_map[indices_k3[0][0]] == face_ids[0]