# Face Recognition Add-on Testing Suite

This directory contains a comprehensive testing framework for the face-rekon Home Assistant add-on, including unit tests, integration tests, and end-to-end tests.

## 🏗️ Test Architecture

### Testing Pyramid
```
         E2E Tests (Few, Slow, High Confidence)
                    ▲
                   / \
        Integration Tests (Some, Medium Speed)
                  ▲
                 / \
        Unit Tests (Many, Fast, Focused)
```

## 📁 Test Structure

### Unit Tests (`/tests/unit/`)
- `test_simple.py` - **✅ Production Ready** - Core business logic without dependencies
  - Base64 image encoding/decoding
  - Data URI parsing  
  - Face matching threshold logic
  - Embedding vector operations
  - Flask API patterns
  - Data structure validation
- `test_clasificador.py` - Unit tests for face classification module (with mocking)
- `test_app.py` - Unit tests for Flask API endpoints (with mocking)

### Integration Tests (`/tests/integration/`)
- `test_api_integration.py` - **Real API endpoint testing**
  - Full HTTP request/response cycles
  - Real Flask app with mocked ML dependencies
  - Complete face recognition workflows
  
- `test_database_integration.py` - **Real database operations**
  - TinyDB persistence testing
  - FAISS index operations
  - Data consistency validation
  
- `test_end_to_end.py` - **Complete user workflows**
  - Unknown face → Storage → Classification
  - Known face recognition
  - Multiple faces handling
  - Error recovery scenarios

### Test Configuration
- `conftest.py` - Shared fixtures and setup
- `unit/` - Unit test directory
- `integration/` - Integration test directory  
- `integration/conftest.py` - Integration test environment setup
- `pytest.ini` - Default test configuration (all tests)
- `pytest-unit.ini` - Unit test specific configuration
- `pytest-integration.ini` - Integration test configuration

## 🚀 Quick Start

### Professional Test Runner
```bash
# Use the built-in test runner (recommended)
python run_tests.py unit           # Fast unit tests
python run_tests.py integration    # Integration tests
python run_tests.py api           # API tests only
python run_tests.py e2e           # End-to-end tests
python run_tests.py all           # Complete test suite
python run_tests.py coverage      # With coverage report
python run_tests.py check         # Check dependencies
```

### Direct pytest Commands
```bash
# Unit tests (fastest, no dependencies)
pytest tests/unit/ -c pytest-unit.ini -v

# Integration tests (requires Flask, etc.)
pytest tests/integration/ -c pytest-integration.ini -v

# Specific test categories
pytest tests/unit/test_simple.py -v                              # Core unit tests
pytest tests/integration/test_api_integration.py -v             # API tests
pytest tests/integration/test_database_integration.py -v        # Database tests
pytest tests/integration/test_end_to_end.py -v                  # E2E tests

# All tests with default config
pytest tests/ -v
```

## 🔧 Test Environment Setup

### Minimal Setup (Unit Tests)
```bash
pip install pytest flask pillow numpy
```

### Full Setup (All Tests)
```bash
pip install -r requirements-test.txt
# For advanced mocking, also install:
# pip install opencv-python-headless insightface==0.7.3 faiss-cpu==1.10.0 tinydb
```

## 📊 Test Categories and Markers

### Pytest Markers
```bash
# Run only unit tests
pytest -m "not integration" -v

# Run only integration tests  
pytest -m integration -v

# Skip slow tests
pytest -m "not slow" -v

# Run specific categories
pytest -m api -v
pytest -m database -v
pytest -m e2e -v
```

## 🏛️ Integration Test Features

### Professional Test Isolation
- **Session-scoped fixtures** - Isolated test environment per session
- **Function-scoped cleanup** - Clean state for each test
- **Temporary file systems** - No pollution of real directories
- **Database isolation** - Separate TinyDB instances per test

### Real Test Data
- **Generated test images** - Various sizes, colors, patterns
- **Base64 encoding/decoding** - Real data transformation testing
- **Mock face embeddings** - Realistic 512-dimensional vectors
- **Sample face records** - Complete database schemas

### End-to-End Workflows
- **Complete user journeys** - Upload → Process → Store → Classify
- **Error recovery testing** - System resilience validation
- **Concurrent request handling** - Thread safety verification
- **Performance characteristics** - Response time validation

## 📈 Coverage and Reporting

### Coverage Reports
```bash
# Generate HTML coverage report
python run_tests.py coverage

# View coverage
open htmlcov/index.html
```

### Test Reporting
- **Verbose output** - Detailed test descriptions
- **Progress indicators** - Real-time test execution status
- **Failure analysis** - Short traceback format
- **Summary statistics** - Pass/fail counts and timing

## 🔍 Test Development Patterns

### Unit Test Patterns
```python
def test_business_logic():
    """Test core logic without external dependencies"""
    # Arrange
    input_data = "test_input"
    expected = "expected_output"
    
    # Act
    result = process_function(input_data)
    
    # Assert
    assert result == expected
```

### Integration Test Patterns
```python
@pytest.mark.integration
def test_api_endpoint(flask_test_client, test_images):
    """Test real API with mocked dependencies"""
    with patch('clasificador.app') as mock_ml:
        mock_ml.get.return_value = [mock_face]
        
        response = flask_test_client.post('/api/endpoint', 
                                        json=test_data)
        
        assert response.status_code == 200
```

### End-to-End Test Patterns
```python
@pytest.mark.integration
@pytest.mark.e2e
def test_complete_workflow(flask_test_client, clean_test_env):
    """Test complete user workflow"""
    # Step 1: Upload unknown face
    upload_response = flask_test_client.post('/recognize', json=data)
    
    # Step 2: Verify storage
    faces = flask_test_client.get('/faces').json
    
    # Step 3: Classify face
    classify_response = flask_test_client.patch(f'/faces/{face_id}', 
                                              json=classification)
    
    # Step 4: Verify persistence
    updated_face = flask_test_client.get(f'/faces/{face_id}').json
    assert updated_face['name'] == 'Expected Name'
```

## 🛠️ Debugging and Troubleshooting

### Common Issues
1. **Import Errors** - Ensure scripts/ is in Python path
2. **ML Dependencies** - Use mocking for heavy dependencies
3. **File Permissions** - Temporary directories need write access
4. **Port Conflicts** - Flask test client uses internal routing

### Debug Mode
```bash
# Run with debugging
pytest tests/integration/ -v -s --tb=long

# Run single test with debugging
pytest tests/integration/test_api_integration.py::TestFaceRecognitionAPIIntegration::test_ping_endpoint_integration -v -s
```

## 📋 Test Checklist for New Features

### Before Adding New Features
- [ ] Add unit tests for business logic
- [ ] Add integration tests for API endpoints
- [ ] Add database tests if data persistence involved
- [ ] Add end-to-end tests for complete workflows
- [ ] Update test documentation
- [ ] Verify all test categories pass

### Test Quality Standards
- [ ] Tests are isolated and repeatable
- [ ] Tests have clear descriptions
- [ ] Tests cover happy path and edge cases
- [ ] Tests use appropriate mocking
- [ ] Tests run in reasonable time
- [ ] Tests provide meaningful failure messages

## 🎯 Professional Benefits

### Development Velocity
- **Fast feedback loops** - Unit tests provide immediate validation
- **Confident refactoring** - Comprehensive test coverage enables safe changes
- **Regression prevention** - Integration tests catch breaking changes

### Production Readiness  
- **Quality assurance** - Multiple test layers ensure reliability
- **Error handling** - Tests validate graceful failure scenarios
- **Performance validation** - Tests verify response times and throughput

### Team Collaboration
- **Shared understanding** - Tests document expected behavior
- **Onboarding aid** - New team members understand system through tests
- **Deployment confidence** - CI/CD can rely on comprehensive test suite

This testing framework positions your face-rekon project for professional development and production deployment with enterprise-grade quality assurance.