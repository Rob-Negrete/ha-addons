import pytest
import sys
import json
import base64
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io

# Add scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# Mock dependencies before importing
mock_clasificador = Mock()
mock_models = Mock()

with patch.dict('sys.modules', {
    'clasificador': mock_clasificador,
    'models': mock_models,
    'insightface.app': Mock(),
    'tinydb': Mock(),
    'faiss': Mock()
}):
    # Mock the create_models function
    mock_models.create_models.return_value = {
        'ping_model': Mock(),
        'recognize_request_model': Mock(),
        'recognize_response_model': Mock(),
        'face_model': Mock(),
        'face_update_model': Mock(),
        'update_response_model': Mock(),
        'error_model': Mock()
    }
    from app import app


class TestPingEndpoint:
    def test_ping_success(self):
        """Test ping endpoint returns pong"""
        with app.test_client() as client:
            response = client.get('/face-rekon/ping')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['pong'] is True


class TestRecognizeEndpoint:
    def setup_method(self):
        """Setup test client and mock data"""
        self.client = app.test_client()
        
        # Create a test image as base64
        test_image = Image.new('RGB', (100, 100), color='red')
        buffered = io.BytesIO()
        test_image.save(buffered, format="JPEG")
        self.test_image_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        self.test_request = {
            'image_base64': self.test_image_b64,
            'event_id': 'test_event_123'
        }

    @patch('clasificador.identify_all_faces')
    @patch('clasificador.save_unknown_face')
    @patch('os.makedirs')
    @patch('os.remove')
    def test_recognize_faces_success(self, mock_remove, mock_makedirs, 
                                   mock_save_unknown, mock_identify):
        """Test successful face recognition"""
        # Mock face identification results
        mock_results = [
            {
                'face_index': 0,
                'status': 'identified',
                'face_data': {'face_id': 'known_face_1', 'name': 'John Doe'},
                'confidence': 0.85
            }
        ]
        mock_identify.return_value = mock_results
        
        response = self.client.post(
            '/face-rekon/recognize',
            data=json.dumps(self.test_request),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['faces_count'] == 1
        assert len(data['faces']) == 1
        assert data['faces'][0]['status'] == 'identified'
        
        # Should not save unknown face since all faces were identified
        mock_save_unknown.assert_not_called()

    @patch('clasificador.identify_all_faces')
    @patch('clasificador.save_unknown_face')
    @patch('os.makedirs')
    @patch('os.remove')
    def test_recognize_faces_unknown(self, mock_remove, mock_makedirs,
                                   mock_save_unknown, mock_identify):
        """Test face recognition with unknown faces"""
        # Mock face identification with unknown faces
        mock_results = [
            {
                'face_index': 0,
                'status': 'unknown',
                'face_data': None,
                'confidence': 0.0
            }
        ]
        mock_identify.return_value = mock_results
        
        response = self.client.post(
            '/face-rekon/recognize',
            data=json.dumps(self.test_request),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['faces_count'] == 1
        assert data['faces'][0]['status'] == 'unknown'
        
        # Should save unknown face
        mock_save_unknown.assert_called_once()

    @patch('clasificador.identify_all_faces')
    @patch('os.makedirs')
    @patch('os.remove')
    def test_recognize_faces_no_faces(self, mock_remove, mock_makedirs, mock_identify):
        """Test when no faces are detected"""
        mock_identify.return_value = []
        
        response = self.client.post(
            '/face-rekon/recognize',
            data=json.dumps(self.test_request),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'no_faces_detected'
        assert data['faces_count'] == 0
        assert data['faces'] == []

    def test_recognize_missing_image(self):
        """Test recognition with missing image data"""
        request_data = {'event_id': 'test_event'}
        
        response = self.client.post(
            '/face-rekon/recognize',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing image_base64' in data['error']

    def test_recognize_empty_request(self):
        """Test recognition with empty request"""
        response = self.client.post(
            '/face-rekon/recognize',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_recognize_data_uri_format(self):
        """Test recognition with data URI format image"""
        data_uri_image = f"data:image/jpeg;base64,{self.test_image_b64}"
        request_data = {
            'image_base64': data_uri_image,
            'event_id': 'test_event'
        }
        
        with patch('clasificador.identify_all_faces') as mock_identify, \
             patch('os.makedirs'), \
             patch('os.remove'):
            mock_identify.return_value = []
            
            response = self.client.post(
                '/face-rekon/recognize',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200

    @patch('clasificador.identify_all_faces')
    @patch('os.makedirs')
    @patch('os.remove')
    def test_recognize_exception_handling(self, mock_remove, mock_makedirs, mock_identify):
        """Test exception handling in recognition"""
        mock_identify.side_effect = Exception("Test error")
        
        response = self.client.post(
            '/face-rekon/recognize',
            data=json.dumps(self.test_request),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Test error' in data['error']


class TestUnclassifiedFacesEndpoint:
    def setup_method(self):
        self.client = app.test_client()

    @patch('clasificador.get_unclassified_faces')
    def test_get_unclassified_faces_success(self, mock_get_unclassified):
        """Test getting unclassified faces"""
        mock_faces = [
            {
                'face_id': 'face_1',
                'event_id': 'event_1',
                'name': None,
                'relationship': 'unknown'
            },
            {
                'face_id': 'face_2',
                'event_id': 'event_2',
                'name': None,
                'relationship': 'unknown'
            }
        ]
        mock_get_unclassified.return_value = mock_faces
        
        response = self.client.get('/face-rekon/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]['face_id'] == 'face_1'
        assert data[1]['face_id'] == 'face_2'

    @patch('clasificador.get_unclassified_faces')
    def test_get_unclassified_faces_empty(self, mock_get_unclassified):
        """Test getting unclassified faces when none exist"""
        mock_get_unclassified.return_value = []
        
        response = self.client.get('/face-rekon/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []


class TestFaceEndpoint:
    def setup_method(self):
        self.client = app.test_client()

    @patch('clasificador.get_face')
    def test_get_face_success(self, mock_get_face):
        """Test getting specific face information"""
        mock_face_data = [
            {
                'face_id': 'test_face_id',
                'name': 'John Doe',
                'event_id': 'event_123'
            }
        ]
        mock_get_face.return_value = mock_face_data
        
        response = self.client.get('/face-rekon/test_face_id')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert data[0]['face_id'] == 'test_face_id'
        mock_get_face.assert_called_once_with('test_face_id')

    @patch('clasificador.update_face')
    def test_update_face_success(self, mock_update_face):
        """Test updating face information"""
        update_data = {
            'name': 'John Doe',
            'relationship': 'friend',
            'confidence': 'high'
        }
        
        response = self.client.patch(
            '/face-rekon/test_face_id',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'updated successfully' in data['message']
        mock_update_face.assert_called_once_with('test_face_id', update_data)

    @patch('clasificador.update_face')
    def test_update_face_exception(self, mock_update_face):
        """Test update face exception handling"""
        mock_update_face.side_effect = Exception("Update failed")
        
        update_data = {'name': 'John Doe'}
        
        response = self.client.patch(
            '/face-rekon/test_face_id',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Update failed' in data['error']


class TestStaticRoutes:
    def setup_method(self):
        self.client = app.test_client()

    @patch('app.send_from_directory')
    def test_home_route(self, mock_send_file):
        """Test home route serves index.html"""
        mock_send_file.return_value = "index.html content"
        
        response = self.client.get('/')
        
        assert response.status_code == 200
        mock_send_file.assert_called_once_with("./", "index.html")

    @patch('app.send_from_directory')
    def test_snapshot_route(self, mock_send_file):
        """Test snapshot route serves snapshot.jpg"""
        mock_send_file.return_value = "snapshot image"
        
        response = self.client.get('/snapshot')
        
        assert response.status_code == 200
        mock_send_file.assert_called_once_with("./", "snapshot.jpg")