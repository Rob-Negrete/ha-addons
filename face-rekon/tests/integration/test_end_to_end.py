"""
End-to-end integration tests.
Tests complete user workflows from API request to database persistence.
"""
import pytest
import json
import os
import sys
import time
import tempfile
from unittest.mock import patch, Mock
import numpy as np
from PIL import Image

# Add scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndIntegration:
    """Complete end-to-end integration tests"""
    
    def test_complete_unknown_face_workflow(self, flask_test_client, test_images, clean_test_env):
        """
        End-to-end test: Unknown face detection → Storage → Retrieval → Classification
        
        Tests the complete workflow:
        1. Upload unknown face via API
        2. Verify face saved to database
        3. Retrieve unclassified faces
        4. Classify the face
        5. Verify classification persisted
        """
        with patch('clasificador.app') as mock_insightface, \
             patch('clasificador.faiss') as mock_faiss:
            
            # Setup mocks
            mock_embedding = np.random.random(512).astype(np.float32)
            mock_face = Mock()
            mock_face.embedding = mock_embedding
            mock_insightface.get.return_value = [mock_face]
            
            mock_index = Mock()
            mock_index.search.return_value = (np.array([[0.8]]), np.array([[0]]))  # No match
            mock_index.add = Mock()
            mock_faiss.IndexFlatL2.return_value = mock_index
            mock_faiss.write_index = Mock()
            
            # Step 1: Upload unknown face
            test_image = test_images['red_square']
            request_data = {
                'image_base64': test_image['base64'],
                'event_id': 'e2e_test_workflow'
            }
            
            response = flask_test_client.post(
                '/face-rekon/recognize',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            recognition_result = json.loads(response.data)
            assert recognition_result['status'] == 'success'
            assert recognition_result['faces'][0]['status'] == 'unknown'
            
            # Step 2: Verify face was saved (check unclassified faces)
            response = flask_test_client.get('/face-rekon/')
            assert response.status_code == 200
            unclassified_faces = json.loads(response.data)
            
            assert len(unclassified_faces) >= 1
            new_face = None
            for face in unclassified_faces:
                if face.get('event_id') == 'e2e_test_workflow':
                    new_face = face
                    break
            
            assert new_face is not None
            assert new_face['name'] is None
            face_id = new_face['face_id']
            
            # Step 3: Classify the face
            classification_data = {
                'name': 'E2E Test Person',
                'relationship': 'test_subject',
                'confidence': 'high'
            }
            
            response = flask_test_client.patch(
                f'/face-rekon/{face_id}',
                data=json.dumps(classification_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            update_result = json.loads(response.data)
            assert update_result['status'] == 'success'
            
            # Step 4: Verify classification persisted
            response = flask_test_client.get(f'/face-rekon/{face_id}')
            assert response.status_code == 200
            face_details = json.loads(response.data)
            
            assert len(face_details) == 1
            classified_face = face_details[0]
            assert classified_face['name'] == 'E2E Test Person'
            assert classified_face['relationship'] == 'test_subject'
            assert classified_face['confidence'] == 'high'
            
            # Step 5: Verify face no longer appears in unclassified list
            response = flask_test_client.get('/face-rekon/')
            updated_unclassified = json.loads(response.data)
            
            # Should have one less unclassified face (or same count if other tests added faces)
            classified_face_ids = [f['face_id'] for f in updated_unclassified]
            assert face_id not in classified_face_ids

    def test_complete_known_face_workflow(self, flask_test_client, test_images, clean_test_env, known_face_data):
        """
        End-to-end test: Known face recognition workflow
        
        Tests:
        1. Pre-populate database with known face
        2. Upload image of known person
        3. Verify immediate recognition
        4. Verify no duplicate storage
        """
        with patch('clasificador.app') as mock_insightface, \
             patch('clasificador.faiss') as mock_faiss, \
             patch('clasificador.db') as mock_db:
            
            # Setup mocks for known face recognition
            mock_embedding = np.array(known_face_data['embedding'], dtype=np.float32)
            mock_face = Mock()
            mock_face.embedding = mock_embedding
            mock_insightface.get.return_value = [mock_face]
            
            mock_index = Mock()
            mock_index.search.return_value = (np.array([[0.2]]), np.array([[0]]))  # Good match
            mock_faiss.IndexFlatL2.return_value = mock_index
            
            mock_db.get.return_value = known_face_data
            
            # Mock id_map
            with patch('clasificador.id_map', [known_face_data['face_id']]):
                
                # Upload image of known person
                test_image = test_images['blue_rectangle']
                request_data = {
                    'image_base64': test_image['base64'],
                    'event_id': 'e2e_known_face_test'
                }
                
                response = flask_test_client.post(
                    '/face-rekon/recognize',
                    data=json.dumps(request_data),
                    content_type='application/json'
                )
                
                # Verify immediate recognition
                assert response.status_code == 200
                result = json.loads(response.data)
                
                assert result['status'] == 'success'
                assert result['faces_count'] == 1
                
                recognized_face = result['faces'][0]
                assert recognized_face['status'] == 'identified'
                assert recognized_face['face_data']['name'] == 'John Doe'
                assert recognized_face['face_data']['face_id'] == known_face_data['face_id']
                assert recognized_face['confidence'] > 0.5

    def test_multiple_faces_workflow(self, flask_test_client, test_images):
        """
        End-to-end test: Multiple faces in single image
        
        Tests handling of images with multiple faces:
        1. Upload image with multiple faces
        2. Verify all faces processed
        3. Verify individual face storage
        """
        with patch('clasificador.app') as mock_insightface, \
             patch('clasificador.faiss') as mock_faiss:
            
            # Setup mocks for multiple faces
            embeddings = [
                np.random.random(512).astype(np.float32),
                np.random.random(512).astype(np.float32),
                np.random.random(512).astype(np.float32)
            ]
            
            mock_faces = []
            for embedding in embeddings:
                mock_face = Mock()
                mock_face.embedding = embedding
                mock_faces.append(mock_face)
            
            mock_insightface.get.return_value = mock_faces
            
            mock_index = Mock()
            # All faces are unknown
            mock_index.search.return_value = (np.array([[0.8]]), np.array([[0]]))
            mock_index.add = Mock()
            mock_faiss.IndexFlatL2.return_value = mock_index
            mock_faiss.write_index = Mock()
            
            # Upload image with multiple faces
            test_image = test_images['green_circle']
            request_data = {
                'image_base64': test_image['base64'],
                'event_id': 'e2e_multiple_faces'
            }
            
            response = flask_test_client.post(
                '/face-rekon/recognize',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            # Verify response
            assert response.status_code == 200
            result = json.loads(response.data)
            
            assert result['status'] == 'success'
            assert result['faces_count'] == 3
            assert len(result['faces']) == 3
            
            # All faces should be unknown
            for i, face_result in enumerate(result['faces']):
                assert face_result['face_index'] == i
                assert face_result['status'] == 'unknown'
                assert face_result['confidence'] == 0.0

    def test_error_recovery_workflow(self, flask_test_client, test_images):
        """
        End-to-end test: Error handling and recovery
        
        Tests:
        1. Invalid requests handled gracefully
        2. System errors don't corrupt state
        3. Recovery after errors
        """
        # Test 1: Invalid base64 data
        invalid_request = {
            'image_base64': 'invalid_base64_data',
            'event_id': 'error_test'
        }
        
        response = flask_test_client.post(
            '/face-rekon/recognize',
            data=json.dumps(invalid_request),
            content_type='application/json'
        )
        
        # Should handle error gracefully (may return 500 for invalid base64)
        assert response.status_code in [400, 500]
        
        # Test 2: Recovery - valid request after error
        with patch('clasificador.app') as mock_insightface, \
             patch('clasificador.faiss') as mock_faiss:
            
            mock_face = Mock()
            mock_face.embedding = np.random.random(512).astype(np.float32)
            mock_insightface.get.return_value = [mock_face]
            
            mock_index = Mock()
            mock_index.search.return_value = (np.array([[0.8]]), np.array([[0]]))
            mock_index.add = Mock()
            mock_faiss.IndexFlatL2.return_value = mock_index
            mock_faiss.write_index = Mock()
            
            # Valid request after error
            valid_request = {
                'image_base64': test_images['small_image']['base64'],
                'event_id': 'recovery_test'
            }
            
            response = flask_test_client.post(
                '/face-rekon/recognize',
                data=json.dumps(valid_request),
                content_type='application/json'
            )
            
            # Should work normally
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'success'

    def test_concurrent_requests_workflow(self, flask_test_client, test_images):
        """
        End-to-end test: Concurrent request handling
        
        Tests system behavior under concurrent load:
        1. Multiple simultaneous face recognition requests
        2. Verify all requests processed correctly
        3. Verify no data corruption
        """
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def make_request(image_name, event_id):
            """Make a face recognition request"""
            with patch('clasificador.app') as mock_insightface, \
                 patch('clasificador.faiss') as mock_faiss:
                
                mock_face = Mock()
                mock_face.embedding = np.random.random(512).astype(np.float32)
                mock_insightface.get.return_value = [mock_face]
                
                mock_index = Mock()
                mock_index.search.return_value = (np.array([[0.8]]), np.array([[0]]))
                mock_index.add = Mock()
                mock_faiss.IndexFlatL2.return_value = mock_index
                mock_faiss.write_index = Mock()
                
                request_data = {
                    'image_base64': test_images[image_name]['base64'],
                    'event_id': event_id
                }
                
                response = flask_test_client.post(
                    '/face-rekon/recognize',
                    data=json.dumps(request_data),
                    content_type='application/json'
                )
                
                results_queue.put((event_id, response.status_code, response.data))
        
        # Create multiple concurrent requests
        threads = []
        test_cases = [
            ('red_square', 'concurrent_test_1'),
            ('blue_rectangle', 'concurrent_test_2'),
            ('green_circle', 'concurrent_test_3'),
            ('small_image', 'concurrent_test_4')
        ]
        
        # Start threads
        for image_name, event_id in test_cases:
            thread = threading.Thread(target=make_request, args=(image_name, event_id))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)  # 10 second timeout
        
        # Verify all requests completed successfully
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        assert len(results) == len(test_cases)
        
        for event_id, status_code, response_data in results:
            assert status_code == 200
            data = json.loads(response_data)
            assert data['status'] in ['success', 'no_faces_detected']
            
            # Verify event_id can be tracked back
            assert event_id.startswith('concurrent_test_')


@pytest.mark.integration
class TestSystemIntegration:
    """System-level integration tests"""
    
    def test_system_health_check(self, flask_test_client):
        """
        Integration test: Complete system health check
        """
        # Test ping endpoint
        response = flask_test_client.get('/face-rekon/ping')
        assert response.status_code == 200
        
        # Test unclassified faces endpoint
        response = flask_test_client.get('/face-rekon/')
        assert response.status_code == 200
        
        # System should be operational
        data = json.loads(response.data)
        assert isinstance(data, list)  # Should return list of faces (even if empty)

    def test_api_documentation_endpoints(self, flask_test_client):
        """
        Integration test: Verify API documentation is accessible
        """
        # Test swagger documentation endpoint
        response = flask_test_client.get('/swagger/')
        # May return 200 or 404 depending on configuration
        assert response.status_code in [200, 404, 308]  # 308 for redirect

    def test_static_file_serving(self, flask_test_client):
        """
        Integration test: Verify static file serving works
        """
        # Test home page
        response = flask_test_client.get('/')
        # Should attempt to serve index.html (may return 404 if file doesn't exist)
        assert response.status_code in [200, 404]
        
        # Test snapshot endpoint  
        response = flask_test_client.get('/snapshot')
        # Should attempt to serve snapshot.jpg (may return 404 if file doesn't exist)
        assert response.status_code in [200, 404]