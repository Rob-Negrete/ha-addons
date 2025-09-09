import os
import shutil
import tempfile
from unittest.mock import Mock

import numpy as np
import pytest


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing"""
    temp_base = tempfile.mkdtemp()
    temp_faces = os.path.join(temp_base, "faces")
    temp_unknowns = os.path.join(temp_base, "unknowns")
    temp_db = os.path.join(temp_base, "db")

    os.makedirs(temp_faces, exist_ok=True)
    os.makedirs(temp_unknowns, exist_ok=True)
    os.makedirs(temp_db, exist_ok=True)

    yield {
        "base": temp_base,
        "faces": temp_faces,
        "unknowns": temp_unknowns,
        "db": temp_db,
    }

    shutil.rmtree(temp_base)


@pytest.fixture
def mock_insightface():
    """Mock InsightFace app"""
    mock_app = Mock()
    mock_face = Mock()
    mock_face.embedding = np.random.random(512).astype(np.float32)
    mock_app.get.return_value = [mock_face]
    return mock_app


@pytest.fixture
def sample_embedding():
    """Sample face embedding"""
    return np.random.random(512).astype(np.float32)


@pytest.fixture
def flask_app():
    """Create Flask app for testing"""
    import os
    import sys
    from unittest.mock import Mock, patch

    # Add scripts directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

    # Mock dependencies
    with patch.dict(
        "sys.modules",
        {
            "clasificador": Mock(),
            "models": Mock(),
            "insightface.app": Mock(),
            "tinydb": Mock(),
            "faiss": Mock(),
        },
    ):
        from app import app

        app.config["TESTING"] = True
        return app


@pytest.fixture
def client(flask_app):
    """Create test client"""
    return flask_app.test_client()
