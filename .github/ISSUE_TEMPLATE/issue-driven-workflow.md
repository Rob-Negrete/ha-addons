---
name: Issue-Driven TDD Workflow
about: Standard template for all issues following our 8-step Test-Driven Development workflow
title: "[feat/fix/docs/ci]: [Brief description]"
labels: []
assignees: ""
---

# Issue-Driven Test-Driven Development (TDD) Workflow

<!-- This template ensures every issue follows our complete 8-step TDD-enhanced development workflow -->
<!-- 🎯 Core TDD Principle: Every change starts with tests - Red → Green → Refactor -->

## 🎯 Step 1: Problem & Solution Definition

### Problem Statement

**What is the issue or opportunity?**

<!-- Clear description of the problem, bug, or feature need -->

**Impact on users:**

<!-- How does this affect the user experience or system functionality? -->

**Type of Change:**

- [ ] 🚀 **New Feature** - Adding new functionality
- [ ] 🐛 **Bug Fix** - Fixing existing functionality
- [ ] 📚 **Documentation** - Updating docs, guides, or comments
- [ ] 🔧 **Technical Debt** - Refactoring, optimization, or maintenance
- [ ] 🏗️ **Infrastructure** - CI/CD, deployment, or tooling changes

### Current vs Expected Behavior

**Current State ❌:**

<!-- How does the system currently behave? -->

**Expected State ✅:**

<!-- What should the system do instead? -->

### Proposed Solution

**High-level approach:**

<!-- Your proposed solution or fix -->

**Technical components involved:**

<!-- List the main technical areas this will touch -->

**Alternative approaches considered:**

<!-- Any other solutions you evaluated -->

### 🧪 TDD Test Strategy Planning

**Test types required for this change:**

- [ ] **Unit Tests** (`tests/unit/`) - Business logic testing
- [ ] **UI Tests** (`ui/assets/js/**/__tests__/`) - Frontend component testing
- [ ] **Integration Tests** (`tests/integration/`) - API and database testing
- [ ] **End-to-End Tests** - Complete workflow testing

**Test scenarios to implement:**

- [ ] Happy path scenarios
- [ ] Error handling and edge cases
- [ ] Performance and boundary conditions
- [ ] Regression tests for existing functionality

---

## 🔧 Step 2: TDD Implementation Plan

### Architecture & Design

**System components affected:**

<!-- Which parts of the system will change? -->

**API changes:**

<!-- Any new or modified endpoints, functions, or interfaces -->

**Database/Storage changes:**

<!-- Any schema, data structure, or storage modifications -->

**UI/Frontend changes:**

<!-- Any user interface or user experience changes -->

### TDD Implementation Phases

#### Phase 1: RED - Write Failing Tests (X-Y hours)

**🔴 Create failing tests that define expected behavior:**

- [ ] Write unit tests for new functionality (should fail initially)
- [ ] Write integration tests for API changes (should fail initially)
- [ ] Write UI tests for frontend changes (should fail initially)
- [ ] Run test suites to confirm failures: `python run_tests.py unit`
- [ ] Commit failing tests: `test: add failing tests for [feature]`

**TDD Commands for this phase:**

```bash
# Fast feedback during test creation
python run_tests.py unit    # Unit tests (~0.04s)
python run_tests.py ui      # UI tests (~5s)
```

#### Phase 2: GREEN - Minimal Implementation (X-Y hours)

**🟢 Write minimal code to make tests pass:**

- [ ] Implement minimal functionality to pass unit tests
- [ ] Implement minimal API changes to pass integration tests
- [ ] Implement minimal UI changes to pass frontend tests
- [ ] Run tests frequently to confirm progress
- [ ] Commit when tests pass: `feat: implement [feature] to pass tests`

#### Phase 3: REFACTOR - Improve & Optimize (X-Y hours)

**🔵 Improve code quality while keeping tests green:**

- [ ] Refactor implementation for better design
- [ ] Optimize performance while maintaining test passes
- [ ] Add comprehensive error handling
- [ ] Enhance code readability and maintainability
- [ ] Run full test suite: `./run_integration_tests.sh`
- [ ] Commit improvements: `refactor: improve [component] implementation`

#### Phase 4: Comprehensive Validation & Documentation (X-Y hours)

- [ ] Run complete test suite (163 tests): `./run_integration_tests.sh`
- [ ] Verify test coverage meets requirements: `python run_tests.py coverage`
- [ ] Update documentation reflecting new behavior
- [ ] Validate all acceptance criteria met

---

## ⚡ Step 3: TDD Acceptance Criteria

### ✅ Test-First Development Requirements

- [ ] **All functionality is test-defined**: Every requirement has corresponding failing tests before implementation
- [ ] **Red-Green-Refactor cycle followed**: Evidence of TDD cycle in commit history
- [ ] **Test coverage maintained**: >90% coverage for all new/modified code
- [ ] **Tests as documentation**: Tests clearly describe expected behavior

### ✅ Core Functionality (Test-Defined)

- [ ] [Specific functional requirement 1] - **Test file:** `tests/unit/test_[feature].py`
- [ ] [Specific functional requirement 2] - **Test file:** `tests/integration/test_[feature].py`
- [ ] [Specific functional requirement 3] - **Test file:** `ui/assets/js/**/__tests__/[feature].test.js`
- [ ] Error handling for edge cases - **Test scenarios defined and implemented**
- [ ] Performance meets requirements - **Performance tests written and passing**

### ✅ Code Quality & Standards (Test-Enforced)

- [ ] Code follows project conventions and style - **Enforced by linting tests**
- [ ] Proper error handling and logging - **Error scenarios have dedicated tests**
- [ ] Security considerations addressed - **Security tests implemented**
- [ ] Memory and performance optimized - **Performance benchmarks in tests**
- [ ] Backward compatibility maintained - **Regression tests demonstrate compatibility**

---

## 📝 Step 4: TDD Testing Implementation (Mandatory)

### ✅ TDD Unit Testing (RED → GREEN → REFACTOR)

**🔴 RED Phase - Write Failing Tests First:**

- [ ] **Write failing unit tests** for all new functionality before implementation
- [ ] **Test scenarios include:**
  - [ ] Normal operation with valid inputs (should fail initially)
  - [ ] Error handling with invalid inputs (should fail initially)
  - [ ] Edge cases and boundary conditions (should fail initially)
  - [ ] Performance with realistic data volumes (should fail initially)
- [ ] **Run and confirm test failures**: `python run_tests.py unit`

**🟢 GREEN Phase - Minimal Implementation:**

- [ ] **Write minimal code** to make unit tests pass
- [ ] **Iteratively run tests** during implementation: `python run_tests.py unit`
- [ ] **All unit tests passing** before moving to refactor phase

**🔵 REFACTOR Phase - Improve Quality:**

- [ ] **Modified Functionality Tests**: Update existing tests for changed functions
- [ ] **Test Coverage Validation**: Maintain >90% coverage: `python run_tests.py coverage`
- [ ] **Performance Optimization**: Tests continue passing after improvements

### ✅ TDD Integration Testing

**🔴 RED Phase - Write Failing Integration Tests:**

- [ ] **API Integration**: Write failing tests for endpoint interactions and data flow
- [ ] **Database Integration**: Write failing tests for data persistence and retrieval
- [ ] **Component Integration**: Write failing tests for system part interactions
- [ ] **End-to-End Workflows**: Write failing tests for complete user journeys
- [ ] **Performance Testing**: Write failing tests for load conditions

**🟢 GREEN Phase - Implementation:**

- [ ] **Build integration functionality** to pass integration tests
- [ ] **Run integration tests**: `python run_tests.py api`, `python run_tests.py database`
- [ ] **Validate API endpoints** with realistic data flows

**🔵 REFACTOR Phase - Full Suite Validation:**

- [ ] **Run complete integration suite**: `./run_integration_tests.sh` (24 tests, ~57s)
- [ ] **Performance benchmarks met** under realistic conditions

### ✅ TDD Frontend Testing (if applicable)

**🔴 RED Phase - Write Failing UI Tests:**

- [ ] **Component Tests**: Write failing tests for UI component rendering and behavior
- [ ] **User Interaction Tests**: Write failing tests for user actions and state changes
- [ ] **Error Handling Tests**: Write failing tests for UI error states and recovery
- [ ] **Responsive Design Tests**: Write failing tests for different screen sizes
- [ ] **Accessibility Tests**: Write failing tests for keyboard navigation and screen readers

**🟢 GREEN Phase - UI Implementation:**

- [ ] **Build minimal UI components** to pass frontend tests
- [ ] **Run UI tests**: `python run_tests.py ui` (139 tests, ~5s)
- [ ] **Iterative development** with frequent test running

**🔵 REFACTOR Phase - UI Polish:**

- [ ] **Enhance user experience** while maintaining test passes
- [ ] **Cross-browser validation** and responsive design improvements

### ✅ TDD Regression Testing

**🔴 RED Phase - Identify Potential Regressions:**

- [ ] **Write tests for existing functionality** that might be affected
- [ ] **Define regression scenarios** based on change impact analysis

**🟢 GREEN Phase - Prevent Regressions:**

- [ ] **Existing Unit Tests**: All existing tests continue to pass
- [ ] **Integration Test Suite**: Full integration test suite passes (163 total tests)
- [ ] **Performance Benchmarks**: Performance metrics maintained
- [ ] **Breaking Change Analysis**: No unintended breaking changes

**🔵 REFACTOR Phase - Comprehensive Validation:**

- [ ] **Full test suite execution**: `./run_integration_tests.sh`
- [ ] **Memory and performance optimization** with tests validating improvements

---

## 🚀 Step 5: Documentation Requirements (Mandatory)

### ✅ Code Documentation

- [ ] **Function Documentation**: Docstrings for all new/modified functions
- [ ] **Type Hints**: Complete type annotations for parameters and returns
- [ ] **Inline Comments**: Complex logic explained with clear comments
- [ ] **Code Examples**: Usage examples in docstrings where helpful

### ✅ API Documentation

- [ ] **Endpoint Documentation**: Complete API reference for new/changed endpoints
- [ ] **Request/Response Schemas**: Document all data structures
- [ ] **Error Response Documentation**: Document error codes and messages
- [ ] **Authentication Documentation**: Update auth requirements if changed

### ✅ Architecture Documentation

- [ ] **System Design Updates**: Update architecture diagrams if needed
- [ ] **Data Flow Documentation**: Document how data moves through the system
- [ ] **Configuration Documentation**: Document new configuration options
- [ ] **Deployment Documentation**: Update deployment guides if needed

### ✅ User Documentation

- [ ] **User Guide Updates**: Update user-facing documentation
- [ ] **Tutorial Updates**: Update or create tutorials for new features
- [ ] **Troubleshooting Guide**: Add common issues and solutions
- [ ] **FAQ Updates**: Add frequently asked questions

### ✅ Change Documentation

- [ ] **CHANGELOG.md**: Add entry describing the change
- [ ] **Migration Guide**: Document upgrade steps if needed
- [ ] **Breaking Changes**: Document any breaking changes
- [ ] **Release Notes**: Prepare release note content

---

## 🧪 Step 6: TDD Quality Validation

### ✅ TDD Pre-Merge Checklist

**🔴🟢🔵 TDD Cycle Validation:**

- [ ] **TDD process followed**: Commit history shows Red → Green → Refactor pattern
- [ ] **Test-first evidence**: All tests were written before implementation code
- [ ] **Tests define behavior**: Tests clearly document expected functionality

**🧪 Test Suite Validation:**

- [ ] **All tests pass**: Complete test suite (163 tests) passes
  ```bash
  ./run_integration_tests.sh  # 24 integration tests (~57s)
  python run_tests.py unit    # 10 unit tests (~0.04s)
  python run_tests.py ui      # 139 UI tests (~5s)
  ```
- [ ] **Code coverage exceeds threshold**: >90% coverage maintained
  ```bash
  python run_tests.py coverage  # Generate coverage report
  ```
- [ ] **Performance benchmarks met**: All performance tests passing
- [ ] **Regression tests pass**: No existing functionality broken

**🔍 Code Quality Validation:**

- [ ] Linting and formatting checks pass
- [ ] Security scan passes (no critical vulnerabilities)
- [ ] Documentation is complete and accurate

### ✅ TDD Code Review Requirements

**🧪 Test Quality Review:**

- [ ] **Tests are readable and maintainable**: Test names clearly describe expected behavior
- [ ] **Test coverage is comprehensive**: All code paths covered by tests
- [ ] **Tests run fast**: Unit tests complete in <1 second, integration tests <60 seconds
- [ ] **Tests are isolated**: Each test can run independently without side effects
- [ ] **Edge cases covered**: Tests include boundary conditions and error scenarios

**💡 Implementation Quality Review:**

- [ ] Code follows established patterns and conventions **as enforced by tests**
- [ ] Error handling is comprehensive and appropriate **with dedicated error tests**
- [ ] Security best practices are followed **with security test validation**
- [ ] Performance is optimized for expected usage **with performance test benchmarks**
- [ ] Documentation is clear and helpful **with tests serving as behavioral documentation**

**🔄 TDD Process Review:**

- [ ] **Commit history shows TDD cycle**: Evidence of Red → Green → Refactor commits
- [ ] **Tests were written first**: Timestamps and commit messages confirm test-first approach
- [ ] **Refactoring improved design**: Code quality enhanced without changing behavior

---

## ✅ Step 7: TDD Success Metrics

### 🧪 TDD Process Metrics

- [ ] **Test-First Adherence**: 100% of functionality implemented after tests
- [ ] **TDD Cycle Completion**: Evidence of Red → Green → Refactor in commit history
- [ ] **Test Execution Speed**: Unit tests <1s, integration tests <60s
- [ ] **Test Reliability**: Zero flaky tests, 100% consistent pass rate

### 📊 Functional Metrics (Test-Validated)

- [ ] [Specific measurable outcome 1] - **Validated by**: `tests/unit/test_[outcome1].py`
- [ ] [Specific measurable outcome 2] - **Validated by**: `tests/integration/test_[outcome2].py`
- [ ] [Specific measurable outcome 3] - **Validated by**: End-to-end test scenarios

### 🎯 Quality Metrics (Test-Enforced)

- [ ] **Test coverage**: >90% for new/modified code (verified by `python run_tests.py coverage`)
- [ ] **Test suite health**: All 163+ tests passing consistently
- [ ] **Zero critical security vulnerabilities**: Validated by security tests
- [ ] **Documentation coverage**: 100% of public APIs with test examples
- [ ] **Performance requirements met**: Benchmarked by performance tests

### 👥 User Experience Metrics (Test-Measured)

- [ ] **Loading time improvements**: Measured by performance test benchmarks
- [ ] **Error rate reductions**: Tracked by error handling test scenarios
- [ ] **User satisfaction improvements**: Validated by end-to-end user workflow tests

### 🔍 TDD Quality Indicators

- [ ] **Regression prevention**: Zero bugs caught in production that weren't caught by tests
- [ ] **Refactoring confidence**: Successfully improved code design without breaking functionality
- [ ] **Test documentation value**: Tests serve as clear examples of expected behavior
- [ ] **Development speed**: Faster development cycles due to immediate feedback from tests

---

## 📋 Step 8: Implementation Tracking

### Development Branch

**Branch Name:** `[feat/fix/docs]/[brief-description]`
**Based on:** `main`

### TDD Files to Create/Modify

<!-- List test files FIRST (TDD principle), then implementation files -->

**🔴 Test Files (Created First):**

- [ ] `tests/unit/test_[feature].py` - [Unit test scenarios for new functionality]
- [ ] `tests/integration/test_[feature].py` - [Integration test scenarios]
- [ ] `ui/assets/js/**/__tests__/[feature].test.js` - [UI component tests]

**🟢 Implementation Files (Created After Tests):**

- [ ] `path/to/file1.py` - [Description of changes to pass tests]
- [ ] `path/to/file2.js` - [Description of changes to pass tests]

**🔵 Documentation Files (Updated During Refactor):**

- [ ] `docs/` - [Documentation updates reflecting new behavior]
- [ ] `README.md` - [Updates to usage examples if needed]

### TDD Pull Request Checklist

- [ ] **PR Title**: Follows semantic format (feat:, fix:, docs:, etc.) and mentions TDD approach
- [ ] **PR Description**:
  - [ ] Links to this issue and summarizes changes
  - [ ] Documents TDD process followed (Red → Green → Refactor)
  - [ ] Shows test results and coverage improvements
- [ ] **TDD Evidence**:
  - [ ] Commit history shows test-first development
  - [ ] All acceptance criteria met and tested
  - [ ] Test coverage report included
- [ ] **Testing Validation**:
  - [ ] All 163+ tests passing: `./run_integration_tests.sh`
  - [ ] Coverage >90%: `python run_tests.py coverage`
  - [ ] Performance benchmarks met
- [ ] **Documentation**: All documentation requirements completed with test examples
- [ ] **Code Review**: At least one review from team member (including TDD process review)
- [ ] **CI/CD**: All automated checks pass

---

## 🔄 TDD Issue Lifecycle

### Ready for TDD Development

- [ ] Problem clearly defined with testable acceptance criteria
- [ ] Solution approach agreed upon with test strategy
- [ ] **TDD test scenarios identified** and documented
- [ ] Testing strategy defined (Unit → Integration → E2E)
- [ ] Documentation plan established

### 🔴 RED Phase - In Development (Tests First)

- [ ] Development branch created
- [ ] **Failing tests written first** for all requirements
- [ ] Test scenarios cover happy path, edge cases, and errors
- [ ] Tests run and confirmed to fail: `python run_tests.py unit`

### 🟢 GREEN Phase - In Development (Minimal Implementation)

- [ ] **Minimal implementation** written to pass tests
- [ ] Tests iteratively run during development
- [ ] All tests passing before moving to refactor
- [ ] Implementation focuses on making tests green, not perfection

### 🔵 REFACTOR Phase - In Development (Quality Improvement)

- [ ] Code quality improved while maintaining test passes
- [ ] Performance optimized with test validation
- [ ] Documentation being updated to reflect behavior
- [ ] Full test suite validates refactoring: `./run_integration_tests.sh`

### Ready for TDD Review

- [ ] **All acceptance criteria met and test-validated**
- [ ] **All 163+ tests passing** with >90% coverage
- [ ] **TDD process evidence** in commit history (Red → Green → Refactor)
- [ ] Documentation complete with test examples
- [ ] Pull request created with TDD summary

### Ready for TDD Merge

- [ ] Code review approved (including TDD process review)
- [ ] All CI/CD checks passing
- [ ] **Test suite demonstrates quality** and regression prevention
- [ ] Final validation complete

### Done with TDD Confidence

- [ ] Changes merged to main with comprehensive test coverage
- [ ] Issue closed with summary including test metrics
- [ ] Success metrics validated through automated tests
- [ ] **Future changes protected** by comprehensive test suite

---

## Technical Considerations

### Security

<!-- Any security implications, requirements, or considerations -->

### Performance

<!-- Performance requirements, benchmarks, or considerations -->

### Scalability

<!-- How this scales with increased usage or data -->

### Dependencies

<!-- New dependencies or changes to existing ones -->

### Risk Assessment

**High Risk:** <!-- Critical risks and mitigation strategies -->
**Medium Risk:** <!-- Moderate risks and monitoring plans -->
**Low Risk:** <!-- Minor risks for awareness -->

---

## Priority: [High/Medium/Low] | Effort: [Small/Medium/Large] (X-Y hours) | Impact: [High/Medium/Low]

<!-- Brief summary of why this is important and expected impact -->

---

**This issue follows our complete 8-step Issue-Driven TDD Workflow:**

1. ✅ **Document & Define** - Clear problem and solution definition with testable criteria
2. ✅ **TDD Plan & Design** - Technical implementation planning with test-first strategy
3. ✅ **TDD Develop** - Red → Green → Refactor cycle implementation
4. ✅ **TDD Test & Validate** - Test-driven comprehensive validation strategy
5. ✅ **Document & Review** - Complete documentation with test examples
6. ✅ **TDD Quality Assurance** - Pre-merge validation with test evidence
7. ✅ **Deploy & Measure** - Success metrics validated by automated tests
8. ✅ **Close & Retrospect** - Issue completion with test-driven learnings

## 🧪 TDD Quick Reference Commands

### Development Cycle (Fast Feedback)

```bash
# Write failing tests, run to confirm failure
python run_tests.py unit        # Unit tests (~0.04s)
python run_tests.py ui          # UI tests (~5s)

# Implement minimal code, run tests frequently
python run_tests.py unit        # Quick validation during GREEN phase
```

### Quality Validation (Comprehensive Testing)

```bash
# Full integration testing (24 tests, ~57s)
./run_integration_tests.sh     # Complete validation for REFACTOR phase

# Coverage analysis
python run_tests.py coverage   # Generate coverage reports

# Individual test categories
python run_tests.py api         # API integration tests
python run_tests.py database    # Database integration tests
python run_tests.py e2e         # End-to-end tests
```

### Success Criteria

- 🔴 **RED**: Tests fail initially (define expected behavior)
- 🟢 **GREEN**: Tests pass with minimal implementation
- 🔵 **REFACTOR**: Tests continue passing with improved code quality
- 📊 **COVERAGE**: Maintain >90% test coverage
- 🚀 **CONFIDENCE**: Deploy with comprehensive test validation
