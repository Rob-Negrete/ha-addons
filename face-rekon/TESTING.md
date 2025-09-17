# 🧪 Face-Rekon Testing Guide

Complete instructions for running the professional testing suite for the face-rekon Home Assistant add-on.

## 📋 Quick Reference

| Command                      | Description        | Time  | Use Case                    |
| ---------------------------- | ------------------ | ----- | --------------------------- |
| `python run_tests.py unit`   | Fast unit tests    | ~0.1s | Development feedback        |
| `python run_tests.py ui`     | UI tests only      | ~5s   | Frontend development        |
| `python run_tests.py check`  | Dependency check   | ~2s   | Setup verification          |
| `./run_integration_tests.sh` | **⭐ Recommended** | ~57s  | Full integration testing    |
| `python run_tests.py all`    | All tests locally  | ~65s  | Local comprehensive testing |

## 🚀 Recommended Usage

### For Development (Fast Feedback)

```bash
# Quick unit tests during development
python run_tests.py unit

# UI component tests
python run_tests.py ui

# Check if dependencies are available
python run_tests.py check
```

### For CI/CD Pipeline (Production Ready)

```bash
# Memory-optimized, containerized integration tests
./run_integration_tests.sh
```

### For Local Comprehensive Testing

```bash
# Run everything locally (requires ML dependencies)
python run_tests.py all
```

## 🐳 Docker-Based Testing (Recommended)

### Prerequisites

- Docker and Docker Compose installed
- No need to install ML dependencies locally

### Available Docker Commands

#### 1. **Full Integration Test Suite** (⭐ Recommended)

```bash
./run_integration_tests.sh
```

- ✅ **24 tests** across API, Database, and E2E scenarios
- ⏱️ **~57 seconds** total execution time
- 🔒 **Memory-safe** with proper resource limits
- 🎯 **CI/CD optimized** for reliability
- 📝 **UI tests available separately** (139 additional tests)

#### 2. Individual Test Suites

```bash
# Database integration tests (8 tests, ~18s)
docker compose -f docker compose.test.yml run --rm integration-tests pytest tests/integration/test_database_integration.py

# API integration tests (11 tests, ~18s)
docker compose -f docker compose.test.yml run --rm integration-tests pytest tests/integration/test_api_integration.py

# End-to-end tests (5 tests, ~18s)
docker compose -f docker compose.test.yml run --rm integration-tests pytest tests/integration/test_end_to_end.py
```

#### 3. Quick Unit Tests

```bash
# Lightweight unit tests without ML dependencies
docker compose -f docker compose.test.yml run --rm unit-tests
```

## 🔧 Local Testing (Advanced)

### Prerequisites

You'll need ML dependencies installed locally:

```bash
pip install -r requirements-integration.txt
```

### Available Commands

#### Unit Tests Only

```bash
python run_tests.py unit
# ✅ 10 tests, ~0.04s
# Tests core business logic without external dependencies
```

#### UI Tests Only

```bash
python run_tests.py ui
# ✅ 139 tests, ~5s
# Tests all JavaScript components, services, and utilities
```

#### Integration Tests by Category

```bash
# API integration tests
python run_tests.py api

# Database integration tests
python run_tests.py database

# End-to-end integration tests
python run_tests.py e2e
```

#### All Tests with Coverage

```bash
python run_tests.py coverage
# Generates coverage report in htmlcov/index.html
```

#### Dependency Check

```bash
python run_tests.py check
# Verifies required packages are installed
```

## 📊 Test Architecture

### Current Test Status ✅

- **Python Unit Tests**: 10/10 passing (~0.04s)
- **UI Unit Tests**: 139/139 passing (~5s)
- **Database Integration**: 8/8 passing (~18s)
- **API Integration**: 11/11 passing (~18s)
- **End-to-End**: 5/5 passing (~18s)
- **Total**: 163 tests, 100% success rate

### Test Layers

1. **Python Unit Tests** (`tests/unit/`) - Fast, isolated logic tests
2. **UI Unit Tests** (`ui/assets/js/**/__tests__/`) - Component and service tests
3. **Integration Tests** (`tests/integration/`) - Real ML models and APIs
4. **End-to-End Tests** - Complete workflow validation

### Key Features

- **Session-scoped ML models** - Load once, reuse across tests
- **Database isolation** - Clean state for each test
- **Memory optimization** - Prevents container kills
- **Real integration testing** - No mocks, actual components

## 🚨 Troubleshooting

### Common Issues

#### "ML dependencies missing"

**Solution**: Use Docker-based testing (recommended)

```bash
./run_integration_tests.sh
```

#### "Container killed (exit code -9)"

**Solution**: Already fixed! Our memory-optimized approach prevents this.

#### "Tests timing out"

**Solution**: Use the optimized test runner:

```bash
./run_integration_tests.sh
```

#### "Import errors in integration tests"

**Solution**: Already fixed! All import paths are corrected.

### Performance Expectations

- **Unit tests**: < 1 second
- **Integration tests**: ~57 seconds total
- **Individual test files**: ~18 seconds each

## 🎯 CI/CD Integration

### GitHub Actions

The project includes `.github/workflows/` with:

- Automated testing on push/PR
- Multi-architecture Docker builds
- Release automation with semantic versioning

### Local CI Simulation

```bash
# Simulate what CI/CD runs
./run_integration_tests.sh
```

## 📈 Test Coverage

Current coverage:

- **Python Unit Tests**: Core business logic (10 tests)
- **UI Unit Tests**: All components, services, and utilities (139 tests)
- **Integration Tests**:
  - Database operations (8 tests)
  - API endpoints (11 tests)
  - End-to-end workflows (5 tests)
- **Total**: 163 tests with comprehensive coverage

## 🔍 Debugging Tests

### Verbose Output

```bash
# More detailed test output
docker compose -f docker compose.test.yml run --rm integration-tests pytest tests/integration/ -v
```

### Single Test

```bash
# Run specific test
docker compose -f docker compose.test.yml run --rm integration-tests pytest tests/integration/test_api_integration.py::TestFaceRecognitionAPIIntegration::test_ping_endpoint_integration -v
```

### Test Logs

```bash
# Show print statements and logs
docker compose -f docker compose.test.yml run --rm integration-tests pytest tests/integration/ -s
```

## 📁 Test File Structure

```
tests/
├── unit/
│   └── test_simple.py          # Python unit tests (10 tests)
├── integration/
│   ├── conftest.py             # Test fixtures and setup
│   ├── test_api_integration.py      # API tests (11 tests)
│   ├── test_database_integration.py # DB tests (8 tests)
│   └── test_end_to_end.py          # E2E tests (5 tests)
├── pytest.ini                 # Base pytest configuration
├── pytest-unit.ini            # Unit test configuration
└── pytest-integration.ini     # Integration test configuration

ui/assets/js/
├── components/__tests__/       # Component tests
├── services/__tests__/         # Service tests
├── utils/__tests__/           # Utility tests
├── package.json               # npm dependencies and scripts
└── jest.config.js            # Jest configuration
```

## ⚙️ Configuration Files

- `run_tests.py` - Main test runner with dependency detection
- `run_integration_tests.sh` - Optimized Docker-based test runner
- `docker compose.test.yml` - Test containers configuration
- `requirements-integration.txt` - ML dependencies for local testing

---

## ✅ Summary for You

**🎯 Just run this command for most use cases:**

```bash
./run_integration_tests.sh
```

This gives you:

- Complete Python test coverage (24 tests)
- Reliable execution (~57 seconds)
- No dependency management headaches
- CI/CD ready results

**🔧 For development:**

```bash
python run_tests.py unit  # Fast Python feedback
python run_tests.py ui    # Fast UI feedback
```

**📊 For coverage analysis:**

```bash
python run_tests.py coverage
```

The testing infrastructure is complete, documented, and ready for professional use! 🎉
