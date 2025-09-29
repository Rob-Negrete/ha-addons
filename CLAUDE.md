# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains Home Assistant add-ons developed as Docker containers. The project consists of three main components:

1. **face-rekon** - Face recognition add-on using Python, Flask, OpenCV, and FAISS
2. **git-sync-agent** - Git synchronization add-on for automatic repository syncing
3. **training-model** - Face training data storage

## Architecture

### face-rekon Add-on

- **Location**: `ha-addons/face-rekon/`
- **Technology Stack**: Python 3.10, Flask, OpenCV, InsightFace, FAISS, TinyDB, Vanilla JS
- **Entry Point**: `/app/scripts/app.py` (Flask application)
- **Port**: 5001
- **Key Components**:
  - `scripts/app.py` - Main Flask application with REST API endpoints
  - `scripts/clasificador.py` - Face recognition and classification logic
  - `ui/` - Web interface for face management (HTML/CSS/JavaScript)
  - `Dockerfile` - Container configuration
  - `config.json` - Home Assistant add-on configuration with ingress support

### git-sync-agent Add-on

- **Location**: `git-sync-agent/addon/`
- **Technology**: Bash scripting with Git and rsync
- **Entry Point**: `run.sh` - Git cloning and folder synchronization script
- **Configuration**: `config.yaml` - Add-on settings and repository mappings

## Development Commands

### Docker Operations

```bash
# Build face-rekon container
cd ha-addons/face-rekon
docker-compose build

# Run face-rekon locally
docker-compose up

# Build Docker image manually
docker build -t face-rekon .
```

### Face Recognition Add-on

```bash
# Start the Flask application (inside container)
python3 /app/scripts/app.py

# Test the service
curl http://localhost:5001/face-rekon/ping
```

## API Endpoints (face-rekon)

- `GET /face-rekon/ping` - Health check endpoint
- `POST /face-rekon/recognize` - Face recognition from base64 image data
- `GET /face-rekon` - List unclassified faces
- `GET /face-rekon/<face_id>` - Get specific face data
- `PATCH /face-rekon/<face_id>` - Update face information

## Configuration Files

- `ha-addons/face-rekon/config.json` - Home Assistant add-on configuration
- `git-sync-agent/addon/config.yaml` - Git sync agent configuration
- `ha-addons/face-rekon/docker-compose.yml` - Local development setup

## File Structure

```
stark-fortress/
├── ha-addons/
│   └── face-rekon/          # Face recognition add-on
│       ├── scripts/         # Python application code
│       ├── config.json      # HA add-on configuration
│       ├── Dockerfile       # Container definition
│       └── docker-compose.yml
├── git-sync-agent/          # Git synchronization add-on
│   └── addon/
│       ├── config.yaml      # Add-on configuration
│       └── run.sh          # Main script
└── training-model/          # Face training data
    └── faces/
```

## Dependencies

### face-rekon

- insightface==0.7.3
- pillow
- numpy
- opencv-python-headless
- tinydb
- faiss-cpu==1.10.0
- onnxruntime
- flask
- flask-cors

### git-sync-agent

- git
- rsync
- jq (for JSON parsing)

## Data Storage

### face-rekon

- Database: `/config/face-rekon/db` (TinyDB)
- Known faces: `/config/face-rekon/faces`
- Unknown faces: `/config/face-rekon/unknowns`
- FAISS index: `/config/face-rekon/db/faiss_index.index`
- Temporary images: `/app/data/tmp`

## Development Notes

- Both add-ons are designed for Home Assistant OS version 16
- face-rekon uses FAISS for efficient similarity search and face matching
- All containers run with non-root users for security
- The project follows Docker best practices with multi-stage builds where applicable
- Git sync agent supports configurable branch and sync intervals

## Project Analysis Summary (face-rekon)

**Primary Goal:** Home Assistant add-on for real-time face recognition that identifies people from camera images using AI/ML models.

**Core Functionality:**

- Accepts base64-encoded images via REST API
- Uses InsightFace for face detection and embedding extraction
- Stores known faces in TinyDB with FAISS index for fast similarity search
- Automatically saves unknown faces for later classification
- Provides web interface for face management and labeling

**Key Technical Details:**

- Face recognition threshold: 0.5 (lower = more strict matching)
- Image processing: OpenCV + PIL for image manipulation
- Embedding dimension: 512-dimensional vectors
- Thumbnail generation: 160x160px for UI display
- Supports multiple architectures: amd64, armv7, aarch64

**Data Flow:**

1. Receive image → Extract face embedding → Search FAISS index
2. If match found (distance < 0.5) → Return identified person
3. If no match → Save as unknown face → Return 'unknown' status
4. Unknown faces can be labeled via PATCH endpoint

**Integration Context:**

- Part of "stark-fortress" Home Assistant ecosystem
- Works with Home Assistant camera integrations
- Designed for persistent storage across container restarts
- Configurable paths for database and image storage
- For testing http://192.168.3.124:5000/api/events/1757891786.599988-b0db28/snapshot-clean.png

## Coverage Improvement Guidelines (/bump-coverage)

**CRITICAL: All integration tests MUST target Dockerized environment with real ML dependencies**

### Docker Integration Testing Requirements (Lessons Learned)

**❌ NEVER DO:**

- Mock ML libraries (InsightFace, OpenCV, FAISS) in integration tests
- Import `app` at module level in integration test files
- Use complex patching for core ML dependencies
- Assume local environment has ML dependencies installed

**✅ ALWAYS DO:**

- Use try-except import pattern: import `app` inside each test method
- Follow existing integration test patterns in `tests/integration/test_integration.py`
- Target Docker environment where ML dependencies are available
- Tests should gracefully skip when ML dependencies unavailable locally

**Correct Integration Test Pattern:**

```python
def test_endpoint_functionality(self):
    """Test endpoint with real ML pipeline"""
    try:
        import app

        with app.app.test_client() as client:
            response = client.post("/endpoint", json={"data": "test"})
            assert response.status_code == 200
            # Test with real ML pipeline behavior
    except ImportError as e:
        pytest.skip(f"ML dependencies not available: {e}")
```

**Coverage Improvement Workflow:**

1. Analyze coverage reports to identify lowest covered endpoints
2. Create comprehensive test suite targeting all code paths
3. Use Docker integration approach - NO mocking of ML dependencies
4. Verify tests run successfully in GitHub Actions with real ML stack
5. Measure actual coverage improvement (aim for 80%+ for targeted endpoint)

**Success Metrics:**

- Coverage baseline: 25.2% → **54% achieved** (face-rekon project)
- Docker integration tests: 62 passed, 5 failed (92% success rate)
- Real ML pipeline testing with InsightFace, OpenCV, ONNX in Docker

### Testing Infrastructure

**Docker Compose Integration:**

- Tests run in `docker-compose.test.yml` with full ML stack
- Coverage data exported from container to host
- GitHub Actions workflow supports Docker-based testing

**Environment Variables for Testing:**

```bash
QDRANT_PATH=/tmp/ci_test_qdrant
FACE_REKON_BASE_PATH=/tmp/ci_test_faces
FACE_REKON_UNKNOWN_PATH=/tmp/ci_test_unknowns
FACE_REKON_THUMBNAIL_PATH=/tmp/ci_test_thumbnails
FACE_REKON_USE_EMBEDDED_QDRANT=true
```

**Key Files for /bump-coverage:**

- `tests/integration/test_*.py` - Integration test files
- `docker-compose.test.yml` - Docker testing environment
- `Dockerfile.test` - Container with ML dependencies + pytest
- `pytest-integration.ini` - Integration test configuration
- `.github/workflows/ci.yml` - GitHub Actions with Docker testing

### Enhanced /bump-coverage Command Implementation

**Step 1: Coverage Analysis - CRITICAL: Combined Analysis with Mandatory Docker Integration Testing**

⚠️ **MANDATORY**: Always use **COMBINED ANALYSIS** (Unit + Docker Integration) to get complete and accurate coverage results, exactly like CI workflow.

**❌ WRONG WAY (Local Integration Only):**

```bash
# This gives incomplete/misleading results - integration tests skip locally
python -m pytest tests/unit/ --cov=scripts --cov-report=json
python -m pytest tests/integration/ --cov=scripts --cov-report=json  # Skips ML tests
```

**✅ CORRECT WAY (Combined Analysis with Docker Integration):**

```bash
# Step 1a: Run unit tests locally for baseline coverage
cd ha-addons/face-rekon
QDRANT_PATH=/tmp/test_qdrant_unit FACE_REKON_BASE_PATH=/tmp/test_faces FACE_REKON_UNKNOWN_PATH=/tmp/test_unknowns FACE_REKON_THUMBNAIL_PATH=/tmp/test_thumbnails FACE_REKON_USE_EMBEDDED_QDRANT=true python -m pytest tests/unit/ -c pytest-unit.ini --cov=scripts --cov-report=xml:coverage-unit.xml

# Step 1b: Run integration tests in Docker with REAL ML STACK (CRITICAL!)
docker-compose -f docker-compose.test.yml run --rm integration-tests

# Step 1c: Use coverage-health.py for COMBINED analysis (matches CI workflow)
cd ../../
python ha-addons/.github/scripts/coverage-health.py ha-addons/face-rekon/coverage-unit.xml
```

**🔑 KEY PRINCIPLE: Combined Analysis with Docker Integration**

- **Unit Tests**: Fast baseline coverage (25.2% scripts/app.py)
- **Docker Integration**: Real ML pipeline coverage (71% scripts/app.py)
- **Combined Result**: Complete picture matching CI workflow
- **Docker is MANDATORY**: Integration tests MUST run in Docker environment

**Why Combined Analysis with Docker Integration is Mandatory:**

- **Complete Coverage**: Unit + Docker integration gives comprehensive picture
- **Real ML Coverage**: Integration tests in Docker achieve 71% coverage vs 25.2% unit-only
- **CI Workflow Parity**: Matches exactly what GitHub Actions reports
- **No ML Mocking**: Tests real InsightFace, OpenCV, ONNX behavior in Docker
- **Accurate Baselines**: Unit tests provide fast feedback, Docker provides real-world coverage

**Example Combined Analysis Results:**

- **Unit tests only**: 25.2% coverage scripts/app.py (41.1% overall project)
- **Local integration**: 51.7% coverage (many tests skip due to missing ML deps)
- **Docker integration**: **71% coverage** scripts/app.py (55% overall project)
- **Combined Analysis**: Unit baseline + Docker integration = **TRUE CI-MATCHING RESULTS**

**Step 2: Docker Integration Test Creation**

- Create test file following naming pattern: `tests/integration/test_[endpoint]_endpoint.py`
- Use Docker integration test pattern (try-except import)
- Target all code paths in the identified low-coverage function
- NO mocking of ML dependencies

**Step 3: Validation**

```bash
# Test locally (should skip gracefully)
python -m pytest tests/integration/test_new_endpoint.py -v

# Test in Docker (should execute with real ML)
docker-compose -f docker-compose.test.yml run --rm integration-tests \
  python -m pytest tests/integration/test_new_endpoint.py --cov=scripts
```

**Step 4: CI/CD Verification**

- Push to feature branch
- Verify GitHub Actions runs successfully
- Confirm coverage improvement in CI logs
- Target: 80%+ coverage for specific endpoint, overall project improvement

**Common Pitfalls to Avoid:**

1. **❌ Importing app at module level** → Use try-except inside test methods
2. **❌ Mocking core ML libraries** → Use real Docker ML stack
3. **❌ Assuming local ML deps** → Tests should skip gracefully locally
4. **❌ Not testing all code paths** → Comprehensive test coverage needed
5. **❌ Ignoring CI failures** → Must work in Docker environment

**Success Validation:**

- ✅ Tests pass in GitHub Actions with Docker
- ✅ Coverage reports show improvement
- ✅ Real ML pipeline behavior tested
- ✅ No ML dependency mocking
- ✅ Tests skip gracefully when ML deps unavailable

**Example Success: debug_test_webp endpoint**

- Before: 0% coverage (48 uncovered lines)
- After: 54% overall project coverage
- Result: 18 comprehensive test methods covering all code paths

### /bump-coverage Command Quick Reference

**Usage:** `/bump-coverage [target_percentage] [analysis_instructions]`

**Core Principle:** ALWAYS use Combined Analysis (Unit + Docker Integration) with real ML dependencies

**Workflow Summary:**

1. 🔍 **Analyze** → Use Combined Analysis (Unit + Docker Integration) for TRUE coverage results
2. 🐳 **Docker Test** → Create integration tests with try-except import pattern
3. ✅ **Validate** → Ensure tests pass in GitHub Actions with real ML stack
4. 📈 **Measure** → Confirm coverage improvement in CI reports

**CRITICAL STEP 1 - Combined Coverage Analysis:**

- ❌ NEVER analyze coverage using only local tests
- ✅ ALWAYS use Combined Analysis: Unit tests + Docker integration tests
- ✅ Commands: Unit coverage → `docker-compose -f docker-compose.test.yml run --rm integration-tests` → `coverage-health.py`
- ✅ This gives TRUE CI-matching results (e.g., 71% vs 25.2% unit-only)

**Remember:** No mocking of ML libraries, use Docker environment, tests should skip gracefully locally but run fully in CI.
