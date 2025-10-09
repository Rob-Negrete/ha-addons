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
   ✅ Required: Total coverage ≥ previous baseline (e.g., 72.0% → 75.0%)
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
scripts/app.py            230     65   71.7%   [baseline: 72.0%] ✅
scripts/clasificador.py   265     73   72.5%   [baseline: 72.0%] ✅
scripts/qdrant_adapter.py 167     46   72.5%   [baseline: 72.0%] ✅
-----------------------------------------------------
TOTAL                     662    184   72.2%   [baseline: 72.0%] ✅

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

## 🔍 Step 1: Combined Coverage Analysis (CRITICAL: Use Docker Integration)

**⚠️ MANDATORY: Combined Analysis (Unit + Docker Integration) for TRUE Coverage Results**

**✅ CORRECT Combined Analysis Workflow:**

```bash
# Step 1a: Run unit tests locally for baseline coverage
cd ha-addons/face-rekon
QDRANT_PATH=/tmp/test_qdrant_unit FACE_REKON_BASE_PATH=/tmp/test_faces FACE_REKON_UNKNOWN_PATH=/tmp/test_unknowns FACE_REKON_THUMBNAIL_PATH=/tmp/test_thumbnails FACE_REKON_USE_EMBEDDED_QDRANT=true python -m pytest tests/unit/ -c pytest-unit.ini --cov=scripts --cov-report=xml:coverage-unit.xml

# Step 1b: Run integration tests in Docker with REAL ML STACK (CRITICAL!)
docker-compose -f docker-compose.test.yml run --rm integration-tests

# Step 1c: Use coverage-health.py with auto-discovery for COMBINED analysis (matches CI workflow)
python ../../.github/scripts/coverage-health.py coverage-unit.xml
# Script auto-discovers coverage-integration.xml and uses best coverage from all reports
```

**🔑 KEY PRINCIPLE: Combined Analysis with Docker Integration**

- **Unit Tests**: Fast baseline coverage (e.g., 41.1% overall project)
- **Docker Integration**: Real ML pipeline coverage (e.g., 71% scripts/app.py)
- **Combined Result**: Complete picture matching CI workflow (e.g., 44.8% best coverage)
- **Docker is MANDATORY**: Integration tests MUST run in Docker environment

**Why Combined Analysis with Docker Integration is Mandatory:**

- **Complete Coverage**: Unit + Docker integration gives comprehensive picture
- **Real ML Coverage**: Integration tests in Docker achieve 71% vs 41% unit-only
- **CI Workflow Parity**: Matches exactly what GitHub Actions reports
- **No ML Mocking**: Tests real InsightFace, OpenCV, ONNX behavior in Docker
- **Accurate Baselines**: Unit tests provide fast feedback, Docker provides real-world coverage

**Coverage Report Analysis Strategy:**

**Option A: Use Combined Coverage Results (Preferred)**

- Use coverage-health.py output for comprehensive analysis
- Parse auto-discovered coverage files (unit + integration + any cached files)
- Extract file-by-file coverage percentages and uncovered line numbers
- Use combined results for accurate gap identification
- Validate coverage report includes real ML pipeline coverage

**Option B: Parse Individual Coverage Files (Fallback)**

- Check for existing coverage-unit.xml and coverage-integration.xml
- Parse coverage data from both sources if coverage-health.py unavailable
- Manually combine results for comprehensive analysis
- Generate detailed coverage report with file-by-file breakdown

**Coverage Report Parsing:**

- Extract uncovered lines from XML/JSON reports (preferably combined analysis)
- Map uncovered lines to specific functions/methods/endpoints
- Identify critical paths that lack coverage (prioritize integration-tested paths)
- Generate focused improvement recommendations based on real ML pipeline coverage
- Document baseline metrics from Combined Analysis results

**Critical Validation: CI Parity with Combined Analysis**

- Validate CI workflow produces both unit and integration coverage
- Compare local Combined Analysis with latest CI artifacts to ensure consistency
- Verify Coverage Health Check workflow uses combined coverage methodology
- Check that Docker integration tests run successfully in CI environment
- Ensure coverage measurement methodology matches CI (Combined Analysis approach)
- Alert if significant discrepancies between local Combined Analysis and CI numbers

## 🎯 Step 1.5: Smart Target Selection with Validation (Auto Mode)

**⚠️ CRITICAL: Use select_coverage_target.py to prevent duplicate work**

**When to Use:** If NO specific file/endpoint/function specified in arguments (auto mode)

**Step 1.5a: Run Smart Selection Script**

```bash
cd face-rekon
python tests/utils/select_coverage_target.py --verbose --min-lines 5
```

**Selection Algorithm:**

1. Analyzes coverage JSON from `.coverage-results/coverage-integration.json`
2. Identifies functions with <50% coverage and ≥5 lines
3. Searches test files for existing test coverage patterns
4. Cross-validates against integration coverage reports
5. Returns first truly uncovered function

**Validation Checks:**

- ✅ Function has <50% coverage in combined analysis
- ✅ No existing tests found in test files (searches for patterns)
- ✅ Not already covered in integration tests (cross-check)
- ✅ Has sufficient lines of code (minimum 5 lines)

**Example Output:**

```
Analyzing coverage data...
Found 12 candidates with <50% coverage

1. Evaluating: app.py::Face.patch (0.0%)
   ⚠️  Found existing tests in: tests/integration/test_integration.py
   Lines: 161-182 (test_update_face_endpoint with client.patch call)
   ❌ Skipping - already covered

2. Evaluating: app.py::update_face (0.0%)
   ⚠️  Found existing tests in: tests/integration/test_integration.py
   ❌ Skipping - already covered

3. Evaluating: qdrant_adapter.py::QdrantAdapter._connect_with_retry (45.8%)
   ✅ No existing tests found
   ✅ Valid target found!

Selected target: qdrant_adapter.py::QdrantAdapter._connect_with_retry
Coverage: 45.8% (11/24 lines covered)
```

**Pattern Detection Logic:**

- **Flask REST Endpoints**: `Face.patch` → searches for `client.patch()` in test files
- **Common Naming**: `Face.patch` → searches for `test_update_face_endpoint`
- **Function References**: Direct function name matches in test files
- **HTTP Methods**: Endpoint paths with HTTP verbs (GET, POST, PATCH, DELETE)

**Why This Step is Critical:**

- ✅ **Prevents PR #135 Issue**: Avoids selecting already-covered functions
- ✅ **Ensures Positive Delta**: Only picks truly uncovered targets
- ✅ **Saves Resources**: No wasted CI runs with +0.00% coverage gain
- ✅ **Smart Validation**: Cross-checks coverage JSON against actual test files

**Fallback Strategy:**

If smart selection finds NO valid targets:

1. Review coverage reports manually
2. Check if project already meets coverage goals
3. Consider edge cases or error paths in existing functions
4. Update baseline if overall coverage is satisfactory

**Step 1.5b: Parse Selected Target Information**

Extract from script output:

- **Target File**: e.g., `qdrant_adapter.py`
- **Target Function**: e.g., `QdrantAdapter._connect_with_retry`
- **Current Coverage**: e.g., `45.8%`
- **Uncovered Lines**: Parse from coverage reports

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

## 📊 Step 6: Combined Coverage Validation & CI Integration

**MANDATORY: Combined Analysis Validation (Unit + Docker Integration)**

```bash
# Step 6a: Run unit tests locally for baseline validation
QDRANT_PATH=/tmp/test_qdrant_unit FACE_REKON_BASE_PATH=/tmp/test_faces FACE_REKON_UNKNOWN_PATH=/tmp/test_unknowns FACE_REKON_THUMBNAIL_PATH=/tmp/test_thumbnails FACE_REKON_USE_EMBEDDED_QDRANT=true python -m pytest tests/unit/ -c pytest-unit.ini --cov=scripts --cov-report=xml:coverage-unit.xml --cov-report=term-missing

# Step 6b: Run Docker integration tests for comprehensive validation (CRITICAL!)
docker-compose -f docker-compose.test.yml run --rm integration-tests

# Step 6c: Run Combined Analysis validation (matches CI workflow)
python ../../.github/scripts/coverage-health.py coverage-unit.xml
```

**Combined Coverage Validation Requirements:**

- ✅ **Unit Tests Pass**: All unit tests must pass locally
- ✅ **Docker Integration Tests Pass**: All 66 integration tests pass in Docker environment
- ✅ **Combined Coverage Improvement**: coverage-health.py shows improvement over baseline
- ✅ **Real ML Pipeline Coverage**: Integration tests contribute meaningful coverage (71% scripts/app.py)
- ✅ **Auto-Discovery Success**: Script finds and combines all coverage files
- ✅ **CI Parity**: Local Combined Analysis matches expected CI behavior

**Expected Combined Analysis Results:**

- **Unit Coverage**: ~41.1% overall project baseline
- **Docker Integration**: ~71% scripts/app.py coverage
- **Combined Result**: Best coverage from auto-discovery (target: >44.8%)
- **Improvement Validation**: New coverage > previous baseline

**CI/Local Coherence Validation with Combined Analysis:**

- Download latest CI coverage artifacts from recent successful runs
- Compare local Combined Analysis results with CI Combined Analysis workflow
- Ensure identical Combined Analysis methodology:
  - Same unit test environment and coverage generation
  - Same Docker integration test environment (docker-compose.test.yml)
  - Same coverage-health.py auto-discovery behavior
  - Same coverage file discovery patterns (coverage-\*.xml)
- Validate Coverage Health Check workflow compatibility:
  - Confirm auto-discovery finds both coverage files (unit + integration)
  - Verify realistic baseline expectations based on Combined Analysis
  - Test coverage-health.py produces same results locally as in CI
  - Ensure workflow uses Combined Analysis, not individual coverage reports

**Discrepancy Detection for Combined Analysis:**

- Alert if local Combined Analysis vs CI Combined Analysis differs by >2%
- Check Docker integration test success rate (should be >90% like CI)
- Identify root causes: Docker environment differences, ML dependency versions, etc.
- Validate coverage-health.py auto-discovery consistency between local and CI
- Provide recommendations to align local Combined Analysis with CI workflow
- Document Combined Analysis improvements and validation results

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

## ✅ Step 8: Wait for Coverage Health Check & Verify Gain

### **🎯 CRITERIA OF DONE (MANDATORY)**

**⚠️ CRITICAL: A coverage improvement task is NOT complete until ALL of these conditions are met:**

#### **Step 8.1: Monitor Coverage Health Check Workflow**

After all CI checks pass (Code Quality, Docker Build, Test Face Rekon), the Coverage Health Check workflow triggers automatically.

**Monitor the workflow:**

```bash
# Wait for Coverage Health Check to trigger (2-5 minutes after CI passes)
gh run list --workflow="coverage-health.yml" --limit=1

# Watch the workflow run
gh run watch <RUN_ID>

# Check completion status
gh run view <RUN_ID> --json status,conclusion
```

**Required:** Workflow must complete with `conclusion: "success"`

#### **Step 8.2: Verify Positive Coverage Delta**

**How to verify:**

```bash
# View the coverage report in workflow logs
gh run view <RUN_ID> --log | grep -A 30 "Coverage Health Report"

# Or check PR comments for Coverage Health Check report
gh pr view <PR_NUMBER> --json comments \
  --jq '.comments[] | select(.body | contains("Coverage Health")) | .body'
```

**Required Indicators:**

- ✅ Status: 🟢 PASS (not 🔴 FAIL)
- ✅ Delta: **POSITIVE number** (e.g., +2.72%, NOT +0.00%)
- ✅ Coverage: Above baseline (e.g., 77.56% when baseline is 72%)

**Example SUCCESS (Meets Criteria):**

```
📊 Coverage Health Report
==================================================
Status: 🟢 PASS
Coverage: 77.56%
Delta: +2.72%          ← MUST BE POSITIVE!
Should fail CI: False
```

**Example FAILURE (Does NOT meet criteria):**

```
📊 Coverage Health Report
==================================================
Status: 🟢 PASS
Coverage: 75.80%
Delta: +0.00%          ← NO GAIN - NOT DONE!
Should fail CI: False
```

#### **Step 8.3: What If No Gain or Failure?**

**If Delta is 0.00% or negative:**

1. **Investigate:** Tests may not be running in CI properly
2. **Check:** Are integration tests being executed? Check CI logs
3. **Fix:** Add more tests or fix test execution configuration
4. **Re-run:** Push fixes and wait for new Coverage Health Check
5. **Repeat:** Until positive delta is achieved

**If Workflow Fails:**

1. **Check Logs:** `gh run view <RUN_ID> --log`
2. **Common Issues:**
   - Coverage files not uploaded (check "Upload coverage artifacts" step)
   - Baseline comparison error (verify coverage-health.py)
   - Permissions issue (check GitHub Actions settings)
3. **Fix:** Address root cause and re-run workflow

**DO NOT MERGE** until positive delta is confirmed!

#### **Step 8.4: Merge Only After Criteria Met**

**Final Merge Checklist:**

- [ ] Coverage Health Check workflow: ✅ SUCCESS
- [ ] Coverage delta: ✅ POSITIVE (e.g., +2.72%)
- [ ] All CI checks: ✅ GREEN
- [ ] Function coverage: ✅ 100%
- [ ] PR approved and ready

**Merge Command:**

```bash
# Only run this after FULL criteria met
gh pr merge <PR_NUMBER> --squash --delete-branch
```

**Why This Matters:**

- Prevents merging PRs that don't actually improve coverage
- Ensures Coverage Health Check validation works correctly
- Maintains progressive baseline improvement (ratcheting effect)
- Guarantees real, measurable impact on project quality

#### **Step 8.5: Timeline Expectations**

**Typical Flow:**

1. PR created → CI starts (0 min)
2. CI passes → Coverage Health Check triggers (2-5 min)
3. Coverage Health Check completes (1-2 min)
4. **Total:** 3-7 minutes from PR to criteria verification

**If Coverage Health Check doesn't trigger:**

- Wait 5-10 minutes (sometimes delayed)
- Check GitHub Actions tab for workflow runs
- Manually trigger if needed: `gh workflow run coverage-health.yml`

---

**🔴 REMEMBER: Task is NOT DONE until Coverage Health Check shows POSITIVE delta! 🔴**

---

## ✅ Step 9: Progressive Baseline Management (After Merge)

**Only perform these steps AFTER Step 8 criteria are met and PR is merged.**

**Baseline Update Logic:**

If target was 60%, baseline was 72%, and achieved 77.56%:

- New baseline = **77.56%** (actual achievement from Coverage Health Check)
- Or **77%** (with 0.5% safety margin to prevent flaky test regression)

**Update Coverage Health Check workflow baseline:**

```bash
# Edit .github/workflows/coverage-health.yml
# Change BASELINE_COVERAGE from "72.0" to "77.0" (or achieved %)
```

**Progressive Strategy:**

- Each successful improvement becomes the new floor
- Prevents coverage regression while being realistic
- Creates sustainable "ratcheting up" effect

**Documentation and Closure:**

- Document new baseline and rationale in commit message
- Update project documentation with new coverage expectations
- Record lessons learned for future improvements
- Close related coverage improvement issues

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

**General Coverage Improvement (Using Combined Analysis):**

```bash
/bump-coverage 60
# → Step 1: Runs Combined Analysis (Unit + Docker Integration)
# → Uses coverage-health.py auto-discovery for comprehensive coverage
# → Identifies: app.py (71% Docker integration), overall project (44.8% combined)
# → Targets highest-impact uncovered lines across all files using real ML pipeline coverage
```

**File-Specific Improvement (Combined Analysis Gap Analysis):**

```bash
/bump-coverage 55 app.py
# → Step 1: Runs Combined Analysis specifically for app.py
# → Unit baseline (41.1%) + Docker integration (71%) = comprehensive gap analysis
# → Finds uncovered lines from real ML pipeline testing, not just unit tests
# → Creates targeted tests for Docker-validated missing scenarios
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

**Combined Analysis Validation Example (Local vs CI Coherence):**

```bash
/bump-coverage 60 app.py /recognize endpoint
# → Step 1: Runs Combined Analysis (Unit + Docker Integration)
# → Local Combined Analysis: 44.8% (from coverage-health.py auto-discovery)
# → Step 6: Downloads latest CI artifacts via gh run download
# → Compares: Local 44.8% vs CI 44.8% (0.0% difference - perfect coherence)
# → Validates: CI uses same Combined Analysis methodology ✅
# → Confirms: Coverage Health Check uses coverage-health.py auto-discovery ✅
# → Docker integration tests: 66 passed locally, same as CI ✅
# → Result: Combined Analysis environments are coherent, proceed with improvements
```

**Combined Analysis Discrepancy Alert Example:**

```bash
/bump-coverage 65
# → Local Combined Analysis: 44.8% coverage (Unit: 41.1% + Docker Integration: 71% app.py)
# → CI Combined Analysis: 38.2% coverage (5.6% difference - alert!)
# → Investigation: Local Docker integration tests pass, CI Docker integration tests failing
# → Root cause: CI Docker environment missing ML dependencies or outdated images
# → Recommendation: Fix CI Docker integration test environment before proceeding
# → Action: Update CI docker-compose.test.yml and ML dependency versions
```

**Progressive Baseline Management Example:**

```bash
# Iteration 1: Current Combined Analysis baseline 44.8%
/bump-coverage 50 app.py serve_face_image endpoint
# → Combined Analysis Target: 50%, Baseline: 44.8%, Achieved: 48.2%
# → Unit: 41.1% + Docker Integration: 75% app.py (improved from 71%)
# → Step 8: Update baseline to 48.2% (or 48% with safety margin)
# → Commit: "chore: update coverage baseline to 48% after serve_face_image improvements"

# Iteration 2: New Combined Analysis baseline 48%
/bump-coverage 55 clasificador.py extract_face_crops method
# → Combined Analysis Target: 55%, Baseline: 48%, Achieved: 52.1%
# → Real ML pipeline coverage improvements validated in Docker
# → Step 8: Update baseline to 52.1% (or 52% with safety margin)

# Iteration 3: Progressive Combined Analysis improvement continues
/bump-coverage 60 qdrant_adapter.py health_check error_scenarios
# → Combined Analysis Target: 60%, Baseline: 52%, Achieved: 56.8%
# → Docker integration tests validate real vector database operations
# → New baseline: 57% → Sustainable Combined Analysis ratcheting effect! 📈
```

---

**Starting coverage improvement for target:** $ARGUMENTS

Let me begin by parsing your specific targeting requirements and analyzing the current coverage state...
