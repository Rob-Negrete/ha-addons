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
