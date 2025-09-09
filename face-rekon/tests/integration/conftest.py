"""
Integration test fixtures and configuration.
Sets up real test environment with isolated databases and file systems.
"""
import pytest
import tempfile
import shutil
import os
import sys
import threading
import time
from pathlib import Path
from PIL import Image
import base64
import io

# Add scripts directory to Python path for real imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))


@pytest.fixture(scope="session")
def integration_test_env():
    """
    Session-scoped fixture that sets up a complete isolated test environment.
    Creates temporary directories, databases, and configuration.
    """
    # Create isolated test environment
    temp_base = tempfile.mkdtemp(prefix="face_rekon_test_")
    
    test_config = {
        'base_path': os.path.join(temp_base, 'faces'),
        'unknown_path': os.path.join(temp_base, 'unknowns'),
        'db_path': os.path.join(temp_base, 'db', 'tinydb.json'),
        'faiss_index_path': os.path.join(temp_base, 'db', 'faiss_index.index'),
        'mapping_path': os.path.join(temp_base, 'db', 'faiss_id_map.npy'),
        'tmp_path': os.path.join(temp_base, 'tmp')
    }
    
    # Create directory structure
    for path_key, path_value in test_config.items():
        if path_key.endswith('_path') and not path_key == 'db_path':
            os.makedirs(os.path.dirname(path_value), exist_ok=True)
        elif path_key in ['base_path', 'unknown_path', 'tmp_path']:
            os.makedirs(path_value, exist_ok=True)
    
    # Create db directory
    os.makedirs(os.path.dirname(test_config['db_path']), exist_ok=True)
    
    yield test_config
    
    # Cleanup
    shutil.rmtree(temp_base, ignore_errors=True)


@pytest.fixture
def clean_test_env(integration_test_env):
    """
    Function-scoped fixture that provides a clean environment for each test.
    Clears databases and files between tests.
    """
    config = integration_test_env.copy()
    
    # Clean up files and databases before each test
    for path in [config['db_path'], config['faiss_index_path'], config['mapping_path']]:
        if os.path.exists(path):
            os.remove(path)
    
    # Clean up directories
    for dir_path in [config['base_path'], config['unknown_path'], config['tmp_path']]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            os.makedirs(dir_path, exist_ok=True)
    
    return config


@pytest.fixture
def test_images():
    """
    Provides a set of test images for integration testing.
    Returns both file paths and base64 encoded versions.
    """
    images = {}
    
    # Create test images with different characteristics
    test_cases = [
        ('red_square', 'RGB', (200, 200), 'red'),
        ('blue_rectangle', 'RGB', (300, 150), 'blue'),
        ('green_circle', 'RGB', (150, 150), 'green'),
        ('small_image', 'RGB', (50, 50), 'yellow')
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for name, mode, size, color in test_cases:
            # Create image
            img = Image.new(mode, size, color)
            
            # Add some pattern to make it more realistic
            if name == 'green_circle':
                # Add a simple circle pattern
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                draw.ellipse([25, 25, 125, 125], fill='darkgreen')
            
            # Save as file
            file_path = os.path.join(temp_dir, f'{name}.jpg')
            img.save(file_path, 'JPEG')
            
            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            images[name] = {
                'file_path': file_path,
                'base64': img_b64,
                'size': size,
                'color': color
            }
        
        yield images


@pytest.fixture
def flask_test_client(clean_test_env):
    """
    Creates a Flask test client with real app configuration but isolated test environment.
    Patches the configuration paths to use test environment.
    """
    from unittest.mock import patch
    
    # Patch the configuration paths in clasificador module
    patches = [
        patch('clasificador.BASE_PATH', clean_test_env['base_path']),
        patch('clasificador.UNKNOWN_PATH', clean_test_env['unknown_path']),
        patch('clasificador.DB_PATH', clean_test_env['db_path']),
        patch('clasificador.FAISS_INDEX_PATH', clean_test_env['faiss_index_path']),
        patch('clasificador.MAPPING_PATH', clean_test_env['mapping_path'])
    ]
    
    # Start all patches
    for p in patches:
        p.start()
    
    try:
        # Import app after patching configuration
        from app import app
        app.config['TESTING'] = True
        client = app.test_client()
        
        yield client
        
    finally:
        # Stop all patches
        for p in patches:
            p.stop()


@pytest.fixture
def sample_face_data():
    """
    Provides sample face data for database testing.
    """
    return {
        'face_id': 'test_face_001',
        'event_id': 'integration_test_event',
        'timestamp': 1234567890,
        'image_path': '/test/path/image.jpg',
        'embedding': [0.1] * 512,  # Simplified 512-dim embedding
        'thumbnail': 'dGVzdF90aHVtYm5haWw=',  # "test_thumbnail" in base64
        'name': None,
        'relationship': 'unknown',
        'confidence': 'unknown'
    }


@pytest.fixture  
def known_face_data():
    """
    Provides sample data for a known/classified face.
    """
    return {
        'face_id': 'known_face_001',
        'event_id': 'integration_test_event',
        'timestamp': 1234567800,
        'image_path': '/test/path/known.jpg',
        'embedding': [0.2] * 512,
        'thumbnail': 'a25vd25fdGh1bWJuYWls',  # "known_thumbnail" in base64
        'name': 'John Doe',
        'relationship': 'friend',
        'confidence': 'high'
    }


@pytest.mark.integration
def pytest_configure(config):
    """
    Configure pytest with custom markers for integration tests.
    """
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """
    Auto-mark integration tests and add skip conditions.
    """
    integration_marker = pytest.mark.integration
    slow_marker = pytest.mark.slow
    
    for item in items:
        # Auto-mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(integration_marker)
            item.add_marker(slow_marker)