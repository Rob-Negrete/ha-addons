"""
Integration tests for Flask API endpoints.
Tests the complete API flow with real HTTP requests and database operations.
"""
import pytest
import json
import os
import time
from unittest.mock import patch, Mock
import numpy as np


@pytest.mark.integration
class TestFaceRecognitionAPIIntegration:
    """Integration tests for the face recognition API endpoints"""
    
    def test_ping_endpoint_integration(self, flask_test_client):
        """Test ping endpoint with real Flask app"""
        response = flask_test_client.get('/face-rekon/ping')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['pong'] is True

    @patch('clasificador.app')  # Mock InsightFace
    @patch('clasificador.index')  # Mock FAISS
    def test_face_recognition_full_flow_unknown_face(self, mock_index, mock_insightface, 
                                                   flask_test_client, test_images, clean_test_env):
        """
        Integration test: Upload unknown face → Save to database → Return unknown status
        Tests the complete flow for an unrecognized face.
        """
        # Mock InsightFace to return face embeddings
        mock_face = Mock()
        mock_face.embedding = np.random.random(512).astype(np.float32)
        mock_insightface.get.return_value = [mock_face]
        
        # Mock FAISS to return no matches (high distance)
        mock_index.search.return_value = (np.array([[0.8]]), np.array([[0]]))  # No match
        mock_index.add = Mock()
        
        # Use a test image
        test_image = test_images['red_square']
        request_data = {
            'image_base64': test_image['base64'],
            'event_id': 'integration_test_001'
        }
        
        # Make API request
        response = flask_test_client.post(
            '/face-rekon/recognize',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'success'
        assert data['faces_count'] == 1
        assert len(data['faces']) == 1
        assert data['faces'][0]['status'] == 'unknown'
        assert data['faces'][0]['confidence'] == 0.0
        
        # Verify FAISS operations were called
        mock_index.add.assert_called_once()

    @patch('clasificador.app')  # Mock InsightFace  
    @patch('clasificador.index')  # Mock FAISS
    @patch('clasificador.db')  # Mock database for controlled results
    def test_face_recognition_full_flow_known_face(self, mock_db, mock_index, mock_insightface,
                                                 flask_test_client, test_images, known_face_data):
        """
        Integration test: Upload known face → Find in database → Return identified status
        Tests the complete flow for a recognized face.
        """
        # Mock InsightFace to return face embeddings
        mock_face = Mock()
        mock_face.embedding = np.random.random(512).astype(np.float32)
        mock_insightface.get.return_value = [mock_face]
        
        # Mock FAISS to return a match (low distance)
        mock_index.search.return_value = (np.array([[0.3]]), np.array([[0]]))  # Good match
        
        # Mock database to return known face data
        mock_db.get.return_value = known_face_data
        
        # Mock id_map
        with patch('clasificador.id_map', [known_face_data['face_id']]):
            test_image = test_images['blue_rectangle']
            request_data = {
                'image_base64': test_image['base64'],
                'event_id': 'integration_test_002'
            }
            
            # Make API request
            response = flask_test_client.post(
                '/face-rekon/recognize',
                data=json.dumps(request_data),
                content_type='application/json'
            )
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'success'
        assert data['faces_count'] == 1
        assert len(data['faces']) == 1
        assert data['faces'][0]['status'] == 'identified'
        assert data['faces'][0]['face_data']['name'] == 'John Doe'
        assert data['faces'][0]['confidence'] > 0.6  # Should be high confidence

    def test_face_recognition_no_faces_detected(self, flask_test_client, test_images):
        """
        Integration test: Upload image with no faces → Return empty results
        """
        with patch('clasificador.app') as mock_insightface:
            # Mock InsightFace to return no faces
            mock_insightface.get.return_value = []
            
            test_image = test_images['small_image']
            request_data = {
                'image_base64': test_image['base64'],
                'event_id': 'integration_test_003'
            }
            
            response = flask_test_client.post(
                '/face-rekon/recognize',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'no_faces_detected'
            assert data['faces_count'] == 0
            assert data['faces'] == []

    def test_face_recognition_multiple_faces(self, flask_test_client, test_images):
        """
        Integration test: Upload image with multiple faces → Process all faces
        """
        with patch('clasificador.app') as mock_insightface, \
             patch('clasificador.index') as mock_index:
            
            # Mock InsightFace to return multiple faces
            mock_face1 = Mock()
            mock_face1.embedding = np.random.random(512).astype(np.float32)
            mock_face2 = Mock()
            mock_face2.embedding = np.random.random(512).astype(np.float32)
            mock_insightface.get.return_value = [mock_face1, mock_face2]
            
            # Mock FAISS to return no matches for both
            mock_index.search.return_value = (np.array([[0.8]]), np.array([[0]]))
            mock_index.add = Mock()
            
            test_image = test_images['green_circle']
            request_data = {
                'image_base64': test_image['base64'],
                'event_id': 'integration_test_004'
            }
            
            response = flask_test_client.post(
                '/face-rekon/recognize',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
            assert data['faces_count'] == 2
            assert len(data['faces']) == 2
            assert all(face['status'] == 'unknown' for face in data['faces'])

    def test_face_recognition_invalid_request(self, flask_test_client):
        """
        Integration test: Send invalid request → Return proper error
        """
        # Missing image_base64
        invalid_requests = [
            {},  # Empty request
            {'event_id': 'test'},  # Missing image_base64
            {'image_base64': ''},  # Empty image_base64
            {'image_base64': 'invalid_base64', 'event_id': 'test'}  # Invalid base64
        ]
        
        for invalid_request in invalid_requests:
            response = flask_test_client.post(
                '/face-rekon/recognize',
                data=json.dumps(invalid_request),
                content_type='application/json'
            )
            
            if not invalid_request or 'image_base64' not in invalid_request:
                assert response.status_code == 400
                data = json.loads(response.data)
                assert 'error' in data

    def test_data_uri_formats_integration(self, flask_test_client, test_images):
        """
        Integration test: Test different data URI formats are handled correctly
        """
        with patch('clasificador.app') as mock_insightface:
            mock_face = Mock()
            mock_face.embedding = np.random.random(512).astype(np.float32)
            mock_insightface.get.return_value = [mock_face]
            
            base_image = test_images['red_square']['base64']
            
            # Test different data URI formats
            formats = [
                base_image,  # Plain base64
                f"data:image/jpeg;base64,{base_image}",  # Standard data URI
                f"image/jpg;data:{base_image}"  # Alternative format
            ]
            
            for i, image_format in enumerate(formats):
                request_data = {
                    'image_base64': image_format,
                    'event_id': f'integration_test_format_{i}'
                }
                
                response = flask_test_client.post(
                    '/face-rekon/recognize',
                    data=json.dumps(request_data),
                    content_type='application/json'
                )
                
                assert response.status_code == 200, f"Failed for format {i}: {image_format[:50]}..."


@pytest.mark.integration
class TestFaceManagementAPIIntegration:
    """Integration tests for face management endpoints"""
    
    @patch('clasificador.db')
    def test_get_unclassified_faces_integration(self, mock_db, flask_test_client, sample_face_data):
        """
        Integration test: Get list of unclassified faces from database
        """
        # Mock database to return unclassified faces
        unclassified_faces = [
            sample_face_data,
            {**sample_face_data, 'face_id': 'test_face_002', 'name': None}
        ]
        mock_db.all.return_value = unclassified_faces
        
        response = flask_test_client.get('/face-rekon/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return faces without names
        assert len(data) == 2
        assert all(face['name'] is None for face in data)

    @patch('clasificador.db')
    def test_get_specific_face_integration(self, mock_db, flask_test_client, known_face_data):
        """
        Integration test: Get specific face information by ID
        """
        mock_db.search.return_value = [known_face_data]
        
        face_id = known_face_data['face_id']
        response = flask_test_client.get(f'/face-rekon/{face_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['face_id'] == face_id
        assert data[0]['name'] == 'John Doe'

    @patch('clasificador.db')
    def test_update_face_integration(self, mock_db, flask_test_client):
        """
        Integration test: Update face information (classify unknown face)
        """
        update_data = {
            'name': 'Jane Smith',
            'relationship': 'colleague',
            'confidence': 'high'
        }
        
        response = flask_test_client.patch(
            '/face-rekon/test_face_123',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['status'] == 'success'
        assert 'updated successfully' in data['message']
        
        # Verify database update was called
        mock_db.update.assert_called_once()

    @patch('clasificador.db')
    def test_update_face_error_handling(self, mock_db, flask_test_client):
        """
        Integration test: Handle errors during face update
        """
        # Mock database to raise an exception
        mock_db.update.side_effect = Exception("Database connection failed")
        
        update_data = {'name': 'Test Name'}
        
        response = flask_test_client.patch(
            '/face-rekon/test_face_456',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        
        assert 'error' in data
        assert 'Database connection failed' in data['error']