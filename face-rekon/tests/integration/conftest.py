"""
Integration test fixtures and configuration.
Sets up real test environment with isolated databases and file systems.
"""
import base64
import io
import os
import shutil
import sys
import tempfile

import pytest
from PIL import Image

# Add scripts directory to Python path for real imports
# Handle both local and container environments
scripts_path = os.path.join(os.path.dirname(__file__), "..", "..", "scripts")
if not os.path.exists(scripts_path):
    # We're likely in a container where scripts is at /app/scripts
    scripts_path = "/app/scripts"
sys.path.insert(0, scripts_path)

# Override database paths for testing before importing any modules
# This ensures clasificador.py uses test paths instead of production paths
test_temp_base = "/tmp/face_rekon_integration_test"
os.environ["FACE_REKON_BASE_PATH"] = os.path.join(test_temp_base, "faces")
os.environ["FACE_REKON_UNKNOWN_PATH"] = os.path.join(test_temp_base, "unknowns")
os.environ["FACE_REKON_THUMBNAIL_PATH"] = os.path.join(test_temp_base, "thumbnails")
os.environ["QDRANT_PATH"] = os.path.join(test_temp_base, "qdrant")
os.environ["FACE_REKON_USE_EMBEDDED_QDRANT"] = "true"

# Create the base directories immediately
os.makedirs(os.path.join(test_temp_base, "faces"), exist_ok=True)
os.makedirs(os.path.join(test_temp_base, "unknowns"), exist_ok=True)
os.makedirs(os.path.join(test_temp_base, "thumbnails"), exist_ok=True)
os.makedirs(os.path.join(test_temp_base, "qdrant"), exist_ok=True)

# Set memory optimization flags for ML models
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["NUMEXPR_MAX_THREADS"] = "2"


@pytest.fixture(scope="session")
def integration_test_env():
    """
    Session-scoped fixture that sets up a complete isolated test environment.
    Creates temporary directories, databases, and configuration.
    """
    # Create isolated test environment
    temp_base = tempfile.mkdtemp(prefix="face_rekon_test_")

    test_config = {
        "base_path": os.path.join(temp_base, "faces"),
        "unknown_path": os.path.join(temp_base, "unknowns"),
        "thumbnail_path": os.path.join(temp_base, "thumbnails"),
        "qdrant_path": os.path.join(temp_base, "qdrant"),
        "tmp_path": os.path.join(temp_base, "tmp"),
    }

    # Create directory structure
    for path_key, path_value in test_config.items():
        if path_key.endswith("_path"):
            os.makedirs(path_value, exist_ok=True)

    yield test_config

    # Cleanup
    shutil.rmtree(temp_base, ignore_errors=True)


@pytest.fixture(scope="session")
def shared_ml_models():
    """
    Session-scoped fixture that loads ML models once and reuses them.
    This prevents expensive model reloading for each test.
    """
    # Import here to avoid early model loading
    import app
    import clasificador

    # Return references to the loaded models
    return {
        "clasificador": clasificador,
        "app": app.app,
        "insightface_app": clasificador.app,
        "qdrant_adapter": getattr(clasificador, "qdrant_adapter", None),
    }


@pytest.fixture
def clean_test_env(integration_test_env):
    """
    Function-scoped fixture that provides a clean environment for each test.
    Clears databases and files between tests.
    """
    config = integration_test_env.copy()

    # Clean up directories
    for dir_path in [
        config["base_path"],
        config["unknown_path"],
        config["thumbnail_path"],
        config["qdrant_path"],
        config["tmp_path"],
    ]:
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
        ("red_square", "RGB", (200, 200), "red"),
        ("blue_rectangle", "RGB", (300, 150), "blue"),
        ("green_circle", "RGB", (150, 150), "green"),
        ("small_image", "RGB", (50, 50), "yellow"),
    ]

    with tempfile.TemporaryDirectory() as temp_dir:
        for name, mode, size, color in test_cases:
            # Create image
            img = Image.new(mode, size, color)

            # Add some pattern to make it more realistic
            if name == "green_circle":
                # Add a simple circle pattern
                from PIL import ImageDraw

                draw = ImageDraw.Draw(img)
                draw.ellipse([25, 25, 125, 125], fill="darkgreen")

            # Save as file
            file_path = os.path.join(temp_dir, f"{name}.jpg")
            img.save(file_path, "JPEG")

            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            images[name] = {
                "file_path": file_path,
                "base64": img_b64,
                "size": size,
                "color": color,
            }

        yield images


@pytest.fixture
def flask_test_client(clean_test_env, shared_ml_models):
    """
    Creates a Flask test client using pre-loaded ML models to avoid expensive reloading.
    Reuses session-scoped models for better memory efficiency.
    """
    # Use the pre-loaded Flask app from shared_ml_models
    app = shared_ml_models["app"]
    app.config["TESTING"] = True

    # Create test client
    client = app.test_client()

    yield client


@pytest.fixture
def sample_face_data():
    """
    Provides sample face data for database testing.
    """
    return {
        "face_id": "test_face_001",
        "event_id": "integration_test_event",
        "timestamp": 1234567890,
        "image_path": "/test/path/image.jpg",
        "embedding": [0.1] * 512,  # Simplified 512-dim embedding
        "thumbnail": "dGVzdF90aHVtYm5haWw=",  # "test_thumbnail" in base64
        "name": None,
        "relationship": "unknown",
        "confidence": "unknown",
    }


@pytest.fixture
def known_face_data():
    """
    Provides sample data for a known/classified face.
    """
    return {
        "face_id": "known_face_001",
        "event_id": "integration_test_event",
        "timestamp": 1234567800,
        "image_path": "/test/path/known.jpg",
        "embedding": [0.2] * 512,
        "thumbnail": "a25vd25fdGh1bWJuYWls",  # "known_thumbnail" in base64
        "name": "John Doe",
        "relationship": "friend",
        "confidence": "high",
    }


@pytest.mark.integration
def pytest_configure(config):
    """
    Configure pytest with custom markers for integration tests.
    """
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


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
