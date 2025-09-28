---
description: "Systematically improve test coverage using comprehensive unit+integration testing strategy"
usage: "/bump-coverage {target_percentage} [file] [method/endpoint] [additional_context]"
examples:
  - "/bump-coverage 60"
  - "/bump-coverage 55 app.py"
  - "/bump-coverage 65 integration"
  - "/bump-coverage 60 app.py /recognize endpoint"
  - "/bump-coverage 70 clasificador.py extract_face_crops method"
  - "/bump-coverage 55 qdrant_adapter.py health_check error_scenarios"
  - "/bump-coverage 50 app.py static_files serving"
---

# Test Coverage Improvement Workflow

I'll systematically improve test coverage to **$ARGUMENTS** using the comprehensive testing strategy developed for face-rekon.

This automated workflow will execute a proven 8-step coverage improvement process:

## 📋 **CRITICAL: Test File Organization Guidelines**

**⚠️ IMPORTANT: These test organization rules are MANDATORY and must be strictly followed:**

### **🚫 DO NOT CREATE NEW ENTRY TEST FILES**

**Forbidden Actions:**

- ❌ Creating new standalone test entry files (e.g., `test_new_feature.py`)
- ❌ Creating multiple entry scripts for the same test category
- ❌ Bypassing existing test organization structure
- ❌ Adding tests directly to the root test directory

### **✅ REQUIRED: Use Existing Entry Points + Helper Files**

**Mandatory Structure:**

```
tests/
├── unit/
│   ├── test_unit.py              # 📍 SINGLE ENTRY POINT for unit tests
│   ├── test_clasificador.py      # ✅ Helper file imported by test_unit.py
│   ├── test_app_endpoints.py     # ✅ Helper file for app.py endpoint tests
│   └── mocks/                    # ✅ Reusable test data and fixtures
│       ├── mock_embeddings.py
│       ├── mock_images.py
│       └── test_data.json
├── integration/
│   ├── test_integration.py       # 📍 SINGLE ENTRY POINT for integration tests
│   ├── test_recognize_endpoint.py # ✅ Helper file imported by test_integration.py
│   ├── test_recognize_mocks.py   # ✅ Test utilities and fixtures
│   └── test_full_pipeline.py     # ✅ End-to-end workflow tests
```

### **🎯 Implementation Rules**

1. **Entry Point Pattern**:

   ```python
   # In test_integration.py (ENTRY POINT)
   from .test_recognize_endpoint import TestRecognizeEndpointCoverage
   from .test_full_pipeline import TestFullPipelineIntegration

   # Tests are automatically discovered through imports
   ```

2. **Helper File Organization**:

   - **By Endpoint**: `test_recognize_endpoint.py`, `test_classify_endpoint.py`
   - **By Method**: `test_clasificador_extract_faces.py`, `test_clasificador_embeddings.py`
   - **By Component**: `test_qdrant_operations.py`, `test_image_processing.py`

3. **Reusable Test Infrastructure**:

   - **Mock Data**: `test_recognize_mocks.py`, `test_pipeline_fixtures.py`
   - **Test Utilities**: Helper functions, assertions, setup/teardown
   - **Fixtures**: Reusable test images, embeddings, database states

4. **Naming Conventions**:
   - Helper files: `test_{component}_{feature}.py`
   - Mock files: `test_{component}_mocks.py` or `mocks_{data_type}.py`
   - Entry points: `test_unit.py`, `test_integration.py` (FIXED NAMES)

### **🔄 Adding New Tests - REQUIRED Process**

1. **Identify Target**: Determine if unit or integration test needed
2. **Find/Create Helper**: Use existing helper file or create appropriately named helper
3. **Create Test Infrastructure**: Add mocks, fixtures, utilities to helper files
4. **Import in Entry Point**: Add import statement to appropriate entry file
5. **Verify Discovery**: Ensure tests are discovered through entry point imports

### **📝 Example: Adding /recognize Endpoint Tests**

```python
# ✅ CORRECT: Create helper file
# File: tests/integration/test_recognize_endpoint.py
class TestRecognizeEndpointCoverage:
    def test_recognize_missing_image_base64(self): ...
    def test_recognize_invalid_format(self): ...

# File: tests/integration/test_recognize_mocks.py
class RecognizeTestData:
    @staticmethod
    def create_test_image(): ...

# ✅ CORRECT: Import in entry point
# File: tests/integration/test_integration.py
from .test_recognize_endpoint import TestRecognizeEndpointCoverage  # ✅

# ❌ WRONG: Creating new entry file
# File: tests/integration/test_recognize.py (standalone) # ❌ FORBIDDEN
```

### **🚨 Validation Requirements**

Before implementing any tests, you MUST:

1. **Check existing structure**: Verify entry points exist
2. **Identify helper file**: Find appropriate existing helper or plan new one
3. **Plan import strategy**: Ensure entry point will import new tests
4. **Validate naming**: Follow established conventions
5. **Confirm no duplication**: Ensure no overlapping test implementations

**Violation of these rules will result in immediate rejection and rework requirement.**

---

## 🧪 **MANDATORY: Local Testing Validation Before Commit**

**⚠️ CRITICAL REQUIREMENT: All tests MUST pass locally before any commit is made.**

### **🚨 PRE-COMMIT VALIDATION CHECKLIST**

**Before committing ANY changes, you MUST:**

1. **✅ Run Complete Test Suite Locally**:

   ```bash
   # Unit Tests (MUST PASS 100%)
   QDRANT_PATH=/tmp/test_qdrant_unit FACE_REKON_BASE_PATH=/tmp/test_faces \
   FACE_REKON_UNKNOWN_PATH=/tmp/test_unknowns FACE_REKON_THUMBNAIL_PATH=/tmp/test_thumbnails \
   FACE_REKON_USE_EMBEDDED_QDRANT=true python -m pytest tests/unit/ -c pytest-unit.ini -v

   # Integration Tests (MUST PASS 100%)
   QDRANT_PATH=/tmp/test_qdrant_integration FACE_REKON_BASE_PATH=/tmp/test_faces \
   FACE_REKON_UNKNOWN_PATH=/tmp/test_unknowns FACE_REKON_THUMBNAIL_PATH=/tmp/test_thumbnails \
   FACE_REKON_USE_EMBEDDED_QDRANT=true python -m pytest tests/integration/ -c pytest-integration.ini -v
   ```

2. **✅ Verify Coverage Improvement**:

   ```bash
   # Generate coverage report (MUST show improvement)
   QDRANT_PATH=/tmp/test_qdrant_combined FACE_REKON_BASE_PATH=/tmp/test_faces \
   FACE_REKON_UNKNOWN_PATH=/tmp/test_unknowns FACE_REKON_THUMBNAIL_PATH=/tmp/test_thumbnails \
   FACE_REKON_USE_EMBEDDED_QDRANT=true python -m pytest tests/unit/ tests/integration/ \
   --cov=scripts --cov-report=term-missing --tb=short -q
   ```

3. **✅ Environment Consistency Check**:
   - Ensure local test environment matches CI exactly
   - Same Python version, dependencies, and environment variables
   - Same test discovery patterns and coverage configuration
   - Identical pytest configuration files (pytest-unit.ini, pytest-integration.ini)

### **🚫 ZERO TOLERANCE POLICY**

**❌ ABSOLUTELY FORBIDDEN:**

- Committing with any failing tests (even if "just one test")
- Committing without running the complete test suite
- Committing with coverage regression (lower than baseline)
- Assuming "CI will catch it" - ALL validation MUST happen locally first
- Skipping tests due to "minor changes" - NO EXCEPTIONS

### **📊 REQUIRED VALIDATION OUTCOMES**

**Before commit is allowed, you MUST verify:**

1. **Test Results**: `PASSED` status for ALL tests

   ```
   ✅ Required: ===== X passed, 0 failed, Y skipped =====
   ❌ Forbidden: Any failed tests or errors
   ```

2. **Coverage Metrics**: Improvement over baseline

   ```
   ✅ Required: Total coverage ≥ previous baseline (e.g., 47.9% → 52.3%)
   ❌ Forbidden: Coverage regression or unchanged coverage
   ```

3. **Test Suite Completeness**: All test categories executed
   ```
   ✅ Required: Both unit AND integration tests run successfully
   ❌ Forbidden: Running only partial test suite
   ```

### **🔧 Local Environment Setup Validation**

**Ensure your local environment matches CI:**

```bash
# Check Python version (must match CI)
python --version  # Should match CI Python version

# Verify dependencies
pip list | grep -E "(pytest|coverage|flask|opencv|insightface)"

# Validate test environment variables
echo $QDRANT_PATH $FACE_REKON_BASE_PATH  # Should be set correctly

# Test Docker availability (for integration tests)
docker --version && docker ps  # Should work without errors
```

### **⚡ FAST VALIDATION WORKFLOW**

**For quick pre-commit validation:**

```bash
# 1. Quick smoke test (30 seconds)
python -m pytest tests/unit/test_simple.py -v

# 2. Full validation (2-5 minutes)
./scripts/run-all-tests.sh  # If available, or manual commands above

# 3. Coverage check (additional 1 minute)
python -m pytest tests/unit/ tests/integration/ --cov=scripts --cov-report=term-missing -q
```

### **🚨 COMMIT BLOCKING CONDITIONS**

**Your commit WILL BE REJECTED if:**

- Any test fails locally (even if CI would theoretically pass)
- Coverage decreases from the established baseline
- You skip running the complete test suite locally
- Integration tests are not validated in proper environment
- Test suite execution differs from CI workflow methodology

### **✅ SUCCESSFUL VALIDATION EXAMPLE**

```bash
$ python -m pytest tests/unit/ tests/integration/ --cov=scripts --cov-report=term-missing -q

======================== test session starts ========================
tests/unit/test_simple.py ......                               [ 12%]
tests/unit/test_app.py ........                                [ 28%]
tests/integration/test_integration.py ....................      [100%]

---------- coverage: platform darwin, python 3.11.7-final-0 ----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
scripts/app.py            230    120   47.8%   [baseline: 47.9%] ✅
scripts/clasificador.py   265    148   44.2%   [baseline: 44.0%] ✅
scripts/qdrant_adapter.py 167     98   41.3%   [baseline: 41.0%] ✅
-----------------------------------------------------
TOTAL                     662    366   44.7%   [baseline: 44.5%] ✅

======================== 57 passed, 18 skipped ========================

✅ ALL CHECKS PASSED - COMMIT AUTHORIZED
```

**This validation ensures:**

- No CI surprises or failures
- Consistent quality standards
- Reliable coverage improvements
- Faster development cycles
- Maintainable test infrastructure

---

## 🔄 **MANDATORY: Post-Push CI Validation**

**⚠️ CRITICAL: After pushing to remote, you MUST verify ALL CI workflows succeed before considering the task complete.**

### **🚨 REQUIRED POST-PUSH VALIDATION CHECKLIST**

**After pushing your branch/PR, you MUST:**

1. **✅ Monitor CI Workflow Status**:

   ```bash
   # Check workflow runs for your branch/PR
   gh run list --branch your-branch-name --limit 5

   # Watch specific workflow run in real-time
   gh run watch WORKFLOW_RUN_ID

   # View workflow details if failed
   gh run view WORKFLOW_RUN_ID --log-failed
   ```

2. **✅ Verify Coverage Health Check Success**:

   ```bash
   # Check if Coverage Health Check workflow passed
   gh run list --workflow="Coverage Health Check" --limit 3

   # Ensure coverage validation succeeded
   gh run view COVERAGE_RUN_ID
   ```

3. **✅ Validate All Required Checks Pass**:
   - **Unit Tests CI** ✅ Must pass
   - **Integration Tests CI** ✅ Must pass
   - **Coverage Health Check** ✅ Must pass
   - **Linting/Formatting** ✅ Must pass
   - **Security Scans** ✅ Must pass

### **🚫 WORKFLOW COMPLETION BLOCKERS**

**❌ DO NOT consider task complete if:**

- Any CI workflow shows "Failed" status
- Coverage Health Check reports regression or failure
- Required status checks are not green
- PR auto-merge is blocked due to failing checks
- Integration tests fail in CI environment (even if they passed locally)

### **🔧 CI FAILURE RESPONSE PROTOCOL**

**If CI workflows fail after push:**

1. **Immediate Investigation**:

   ```bash
   # Get failure details
   gh run view FAILED_RUN_ID --log-failed

   # Check specific job failures
   gh run view FAILED_RUN_ID --job JOB_ID
   ```

2. **Environment Discrepancy Analysis**:

   - Compare local vs CI environment differences
   - Check for missing dependencies or environment variables
   - Verify Docker image compatibility and ML library versions
   - Validate pytest configuration consistency

3. **Fix and Re-validate**:
   ```bash
   # Fix issues locally first
   # Run complete local validation again
   # Push fixes and monitor CI again
   gh run watch NEW_RUN_ID
   ```

### **🎯 COMPLETE WORKFLOW VALIDATION**

**Only consider your bump-coverage task successful when:**

1. ✅ **Local validation passes** (all tests, coverage improvement)
2. ✅ **Push/PR created successfully** (proper branch workflow)
3. ✅ **ALL CI workflows pass** (no failures, no regressions)
4. ✅ **Coverage Health Check succeeds** (baseline validation)
5. ✅ **PR auto-merge completes** (if applicable)

**This ensures the complete circle of quality validation from local → CI → production readiness.**

---

## 🔍 Step 1: Analyze Current Coverage State

**Smart Coverage Analysis Strategy:**

**Option A: Use Existing Local Coverage Reports (Preferred)**

- Check for local coverage reports: `coverage.xml`, `coverage.json`, `htmlcov/index.html`
- Parse existing coverage data to identify gaps without running tests
- Extract file-by-file coverage percentages and uncovered line numbers
- Use cached coverage for faster analysis and gap identification
- Validate coverage report freshness (warn if outdated)

**Option B: Generate Fresh Coverage Analysis**

- Run comprehensive coverage analysis (unit + integration tests) if no reports found
- Generate detailed coverage report with file-by-file breakdown
- Cache results locally for future `/bump-coverage` runs

**Coverage Report Parsing:**

- Extract uncovered lines from XML/JSON reports
- Map uncovered lines to specific functions/methods/endpoints
- Identify critical paths that lack coverage
- Generate focused improvement recommendations
- Document baseline metrics and improvement targets

**Critical Validation: Local vs CI Coherence**

- Validate CI workflow is producing both unit and integration coverage
- Compare local coverage reports with latest CI artifacts to ensure consistency
- Verify Coverage Health Check workflow is using combined coverage (not just unit)
- Check that local test environment matches CI test configuration
- Ensure coverage measurement methodology is identical (same test paths, same exclusions)
- Alert if significant discrepancies between local and CI coverage numbers

## 📊 Step 2: Targeted Coverage Gap Analysis

**Parse Arguments for Specific Targeting:**

- **Target**: Extract target percentage from arguments
- **File Focus**: If file specified (e.g., `app.py`), analyze only that file's coverage
- **Method/Endpoint Focus**: If method/endpoint specified (e.g., `/recognize endpoint`), target specific functions
- **Context**: Use additional context for focused test scenarios

**Analysis Strategy (Using Local Coverage Data):**

- Parse existing coverage reports to identify specific uncovered lines in target areas
- Cross-reference uncovered lines with source code to identify functions/methods
- If endpoint specified: Find Flask route handlers and map uncovered lines to request/response flows
- If method specified: Locate exact function definition and identify uncovered branches/conditions
- If file specified: Extract all uncovered lines for comprehensive file-level analysis
- If general: Rank files by coverage gap impact (lines uncovered × complexity score)

**Smart Gap Identification:**

```python
# Example: Parse coverage.xml for /recognize endpoint gaps
uncovered_lines = parse_coverage_xml("coverage.xml", file="app.py", lines=[156, 158, 162-167, 171])
endpoint_gaps = map_lines_to_functions(uncovered_lines, target="/recognize")
# Result: Missing error handling for invalid image format (lines 162-167)
#         Missing request validation for missing parameters (line 171)
```

**Prioritization Matrix:**

- Critical business logic paths in target area
- Error handling scenarios for specified endpoints/methods
- Integration touchpoints for target components
- Edge cases and boundary conditions
- Performance and concurrency scenarios

## 🔧 Step 3: Create Development Branch

- Generate semantic branch name: `feat/improve-coverage-to-{target}%`
- Create and checkout new branch from main
- Ensure clean starting point with current test infrastructure

## 📝 Step 4: Enhance Test Infrastructure

**Integration Test Strategy (Docker-First):**

- Verify Docker-based integration test setup for ML dependencies
- Ensure proper test isolation with separate environments
- Validate coverage collection from containerized tests
- Fix any integration test infrastructure issues

**Unit Test Enhancements:**

- Add missing unit test cases for uncovered lines
- Improve test scenarios for edge cases and error handling
- Mock complex dependencies appropriately
- Ensure proper test organization and naming

## 🧪 Step 5: Implement Targeted Test Cases

**Specific Targeting Based on Arguments:**

**If Endpoint Specified (e.g., `/recognize endpoint`):**

- Test all HTTP methods (GET, POST, PUT, DELETE) if applicable
- Request validation: missing params, invalid data types, malformed JSON
- Response scenarios: success, validation errors, server errors
- Authentication/authorization if applicable
- Rate limiting and concurrent request handling
- Integration with underlying service methods

**If Method Specified (e.g., `extract_face_crops method`):**

- Unit tests for all code paths and branches
- Parameter validation: edge cases, null values, type mismatches
- Return value scenarios: success, empty results, error conditions
- Exception handling and error propagation
- Performance testing with various input sizes
- Mock dependencies and integration points

**If File Specified (e.g., `app.py`):**

- Comprehensive file-level coverage improvement
- All uncovered functions and methods
- Static analysis to identify missing test scenarios
- Class initialization and teardown
- Module-level constants and configurations

**General Focus Areas (based on lessons learned):**

- **app.py**: Flask routes, error handling, static file serving, API endpoints
- **clasificador.py**: Face processing pipelines, data validation, ML workflows
- **qdrant_adapter.py**: Vector operations, health checks, error scenarios
- **models.py**: API model validation and serialization

**Test Implementation Strategy:**

- Unit tests for isolated functionality
- Integration tests for endpoint-to-backend workflows
- Error simulation and recovery testing
- Data validation and sanitization
- Concurrent request handling
- Resource cleanup and management

## 📊 Step 6: Coverage Validation & CI Integration

**Local Coverage Validation:**

- Run comprehensive test suite locally (unit + integration)
- Verify both coverage improvements match expected targets
- Generate fresh coverage reports in coverage-reports/ directory
- Compare new results with baseline reports

**CI/Local Coherence Validation:**

- Download latest CI coverage artifacts from recent successful runs
- Compare local coverage methodology with CI workflow configuration
- Ensure identical test environments:
  - Same Python version and dependencies
  - Same coverage configuration (.coveragerc)
  - Same test file discovery patterns
  - Same coverage exclusions and inclusions
- Validate Coverage Health Check workflow compatibility:
  - Confirm auto-discovery finds both coverage files (unit + integration)
  - Verify realistic baseline expectations (47.9% comprehensive baseline)
  - Test non-PR event handling works correctly
  - Ensure workflow uses combined coverage, not just unit tests

**Discrepancy Detection:**

- Alert if local vs CI coverage differs by >2%
- Identify root causes: environment differences, test configurations, etc.
- Provide recommendations to align local and CI environments
- Document coverage improvements and validation results

## 🚀 Step 7: Commit, Push & Create PR

**Semantic Commit Format:**

```
test: improve coverage to {target}% with comprehensive test strategy

- Add targeted unit tests for uncovered {focus_areas}
- Enhance integration test coverage for {workflows}
- Implement Docker-first testing for ML dependencies
- Achieve {actual}% coverage (+{improvement} percentage points)

Closes #{issue_number}
```

**PR Strategy:**

- Create comprehensive PR with detailed coverage analysis
- Include before/after coverage comparison
- Link to coverage improvement issue
- Document testing strategy and infrastructure changes

## ✅ Step 8: Merge & Update Baselines

**Merge and Validation:**

- Merge PR after all coverage checks pass
- Verify solution works as expected in production environment
- Confirm no regressions introduced in functionality or performance

**Progressive Baseline Management:**

- **Baseline Update Logic**: If target was 60%, baseline was 47%, and achieved 55%:
  - New baseline = **55%** (actual achievement)
  - Or **54%** (with 1% safety margin to prevent flaky test regression)
- **Update Coverage Health Check workflow baseline**:
  - Change `BASELINE_COVERAGE` from "47.9" to "54.0" (or achieved %)
  - Update health check thresholds in PR comment template
  - Commit baseline update separately for clear tracking
- **Progressive Strategy**:
  - Each successful improvement becomes the new floor
  - Prevents coverage regression while being realistic
  - Creates sustainable "ratcheting up" effect

**Documentation and Closure:**

- Document new baseline and rationale in Coverage Health Check
- Update project documentation with new coverage expectations
- Record lessons learned and testing patterns for future improvements
- Close related coverage improvement issues with baseline update notes
- Verify CI workflows continue using comprehensive coverage methodology

---

## 🎯 **Coverage Improvement Best Practices** (Lessons Learned)

### **Docker-First Integration Testing**

- Use containerized tests for ML dependencies (InsightFace, OpenCV)
- Separate test environments prevent conflicts
- Ensure coverage collection from containers
- Integration tests target real-world workflows

### **Comprehensive Coverage Analysis**

- Always combine unit + integration coverage
- Use auto-discovery patterns (`coverage-*.xml`)
- Set realistic baselines based on actual achievable coverage
- Monitor both file-level and total coverage metrics

### **CI/CD Integration**

- Ensure Coverage Health Check uses combined coverage
- Handle both PR and non-PR workflow events
- Upload artifacts for cross-workflow coverage analysis
- Maintain proper baseline expectations

### **Test Consolidation Strategy**

- Remove duplicate test files
- Enhance existing test suites rather than creating new ones
- Follow established test patterns and conventions
- Ensure test isolation and cleanup

---

## 🗂️ **Local Coverage Report Setup**

**Recommended Directory Structure:**

```
face-rekon/
├── coverage-reports/          # Gitignored directory for local coverage cache
│   ├── coverage-unit.xml      # Unit test coverage (XML format)
│   ├── coverage-unit.json     # Unit test coverage (JSON format)
│   ├── coverage-integration.xml # Integration test coverage
│   ├── coverage-integration.json
│   ├── coverage-combined.xml  # Combined coverage report
│   └── last-updated.txt       # Timestamp for cache validation
├── htmlcov/                   # HTML coverage reports (gitignored)
└── .coveragerc               # Coverage configuration
```

**Quick Setup Commands:**

```bash
# Run comprehensive coverage and cache results
cd face-rekon
mkdir -p coverage-reports

# Generate unit coverage
QDRANT_PATH=/tmp/test_qdrant_unit python -m pytest tests/unit/ \
  --cov=scripts --cov-report=xml:coverage-reports/coverage-unit.xml \
  --cov-report=json:coverage-reports/coverage-unit.json

# Generate integration coverage (if Docker available)
QDRANT_PATH=/tmp/test_qdrant_integration python -m pytest tests/integration/ \
  --cov=scripts --cov-report=xml:coverage-reports/coverage-integration.xml \
  --cov-report=json:coverage-reports/coverage-integration.json

# Mark timestamp
date > coverage-reports/last-updated.txt
```

**Gitignore Additions:**

```gitignore
# Coverage reports (local cache)
coverage-reports/
htmlcov/
.coverage
.coverage.*
coverage.xml
coverage.json
```

---

## 💡 **Practical Usage Examples**

**General Coverage Improvement (Using Local Reports):**

```bash
/bump-coverage 60
# → Reads coverage-reports/coverage-combined.xml
# → Identifies: app.py (45% → 60%), clasificador.py (57% → 65%), qdrant_adapter.py (35% → 50%)
# → Targets highest-impact uncovered lines across all files
```

**File-Specific Improvement (Smart Gap Analysis):**

```bash
/bump-coverage 55 app.py
# → Parses coverage-reports/coverage-unit.xml for app.py specific gaps
# → Finds uncovered lines: 156-167 (error handling), 234-239 (cleanup), 345-350 (validation)
# → Creates targeted tests for exactly those missing scenarios
```

**Endpoint-Specific Testing (Precision Targeting):**

```bash
/bump-coverage 60 app.py /recognize endpoint
# → Maps /recognize route handler to lines 145-180 in app.py
# → Identifies uncovered lines: 162-167 (invalid image handling), 171 (param validation)
# → Creates tests for: POST with malformed image, missing Content-Type, invalid JSON
# → Tests integration touchpoints with clasificador.py (lines mapped from coverage)
```

**Method-Specific Coverage:**

```bash
/bump-coverage 70 clasificador.py extract_face_crops method
# → Focuses on extract_face_crops function specifically
# → Tests edge cases: empty images, invalid formats, multiple faces
# → Parameter validation, error handling, return value scenarios
```

**Complex Targeting:**

```bash
/bump-coverage 55 qdrant_adapter.py health_check error_scenarios
# → Targets health_check method with focus on error scenarios
# → Network timeouts, invalid responses, connection failures
# → Recovery mechanisms and fallback behaviors
```

**Validation Example (Local vs CI Coherence):**

```bash
/bump-coverage 60 app.py /recognize endpoint
# → Step 1: Reads local coverage-reports/coverage-combined.xml (Local: 47.2%)
# → Step 6: Downloads latest CI artifacts via gh run download
# → Compares: Local 47.2% vs CI 47.9% (0.7% difference - acceptable)
# → Validates: CI produces both coverage-unit.xml + coverage-integration.xml ✅
# → Confirms: Coverage Health Check uses 47.9% baseline ✅
# → Result: Environments are coherent, proceed with improvements
```

**Discrepancy Alert Example:**

```bash
/bump-coverage 65
# → Local reports: 48.1% coverage
# → CI reports: 42.3% coverage (5.8% difference - alert!)
# → Investigation: Local includes integration tests, CI integration tests failing
# → Recommendation: Fix CI integration test environment before proceeding
# → Action: Resolve Docker/ML dependency issues in CI first
```

**Progressive Baseline Management Example:**

```bash
# Iteration 1: Current baseline 47.9%
/bump-coverage 55 app.py /recognize endpoint
# → Target: 55%, Baseline: 47.9%, Achieved: 52.3%
# → Step 8: Update baseline to 52.3% (or 51% with safety margin)
# → Commit: "chore: update coverage baseline to 52% after /recognize improvements"

# Iteration 2: New baseline 52%
/bump-coverage 60 clasificador.py extract_face_crops method
# → Target: 60%, Baseline: 52%, Achieved: 57.8%
# → Step 8: Update baseline to 57.8% (or 57% with safety margin)

# Iteration 3: Progressive improvement continues
/bump-coverage 65 qdrant_adapter.py health_check error_scenarios
# → Target: 65%, Baseline: 57%, Achieved: 61.2%
# → New baseline: 61% → Sustainable ratcheting effect! 📈
```

---

**Starting coverage improvement for target:** $ARGUMENTS

Let me begin by parsing your specific targeting requirements and analyzing the current coverage state...
