# Integration Tests

## Docker-First Approach

Integration tests for face-rekon **MUST** be run in Docker due to ML dependencies (InsightFace, OpenCV, etc.).

### Running Integration Tests

```bash
# Run integration tests (Docker required)
docker-compose -f docker-compose.test.yml run --rm integration-tests

# Or run all tests
docker-compose -f docker-compose.test.yml run --rm test-runner
```

### Local Development

```bash
# For local development, use unit tests
python run_tests.py unit

# Integration tests will fail locally with helpful error message
python run_tests.py integration  # ❌ Will show Docker requirement
```

### Test Structure

- **`test_integration.py`** - Main comprehensive integration test file
  - Flask API endpoints with real ML backend
  - ML pipeline (InsightFace, OpenCV)
  - Vector database operations (Qdrant)
  - API models and Flask-RESTX components
  - End-to-end system workflows

### Coverage

Current Docker-based integration tests achieve **34% coverage** with all major components tested.

### Why Docker-First?

- **ML Dependencies**: InsightFace, OpenCV require complex native libraries
- **Consistency**: Same environment across development, CI/CD, production
- **Easy Setup**: No local ML dependency installation required
- **Real Testing**: Tests run against actual ML models and processing
