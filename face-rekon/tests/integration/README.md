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

- **`test_integration.py`** - Comprehensive integration test file targeting 60% coverage
  - Flask API endpoints with real ML backend (app.py coverage)
  - ML pipeline (InsightFace, OpenCV, clasificador.py coverage)
  - Vector database operations (Qdrant, qdrant_adapter.py coverage)
  - API models and Flask-RESTX components
  - End-to-end system workflows
  - Error handling and edge cases
  - Concurrent request testing

### Coverage Target

Integration tests target **60% coverage** with comprehensive testing of:

- **app.py**: Flask routes, error handling, static assets
- **clasificador.py**: Face processing, management operations
- **qdrant_adapter.py**: Vector operations, health checks
- **models.py**: API model definitions

### Why Docker-First?

- **ML Dependencies**: InsightFace, OpenCV require complex native libraries
- **Consistency**: Same environment across development, CI/CD, production
- **Easy Setup**: No local ML dependency installation required
- **Real Testing**: Tests run against actual ML models and processing
