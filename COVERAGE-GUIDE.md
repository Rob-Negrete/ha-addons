# Coverage Health Check Guide

This document explains the automated test coverage health check system for the ha-addons repository.

## 📊 Overview

The coverage health check system provides automated analysis of test coverage with intuitive status indicators:

- 🟢 **Green (Pass)**: Coverage maintained or improved (≥67%)
- 🟡 **Amber (Warning)**: Minor coverage decrease (60-66%)
- 🔴 **Red (Fail)**: Significant coverage drop (<60%)

## 🎯 Current Baseline

**Baseline Coverage**: **67%** (established from face-rekon addon unit tests)

This baseline represents the current test coverage state and serves as the target to maintain or improve.

## 🤖 Automated Workflows

### Coverage Health Check Workflow

**Trigger**: Pull Requests to `main` branch
**Workflow File**: `.github/workflows/coverage-health.yml`

**Process**:

1. Runs unit tests on PR branch with coverage collection
2. Runs unit tests on main branch for baseline comparison
3. Analyzes coverage delta and determines health status
4. Posts comprehensive report as PR comment
5. Creates GitHub status check with emoji indicator
6. Fails CI if coverage drops below critical threshold (60%)

### CI Integration

The main CI workflow (`.github/workflows/ci.yml`) has been enhanced to:

- Generate coverage reports in multiple formats (XML, JSON)
- Upload coverage data to Codecov
- Support the coverage health check analysis

## 📋 Status Indicators

### Health Status Colors

| Status       | Coverage Range | Color       | CI Impact         |
| ------------ | -------------- | ----------- | ----------------- |
| 🟢 **Green** | ≥67%           | brightgreen | ✅ Pass           |
| 🟡 **Amber** | 60-66%         | yellow      | ⚠️ Warning (Pass) |
| 🔴 **Red**   | <60%           | red         | ❌ Fail           |

### Badge Updates

The README.md coverage badge is automatically updated to reflect:

- Current coverage percentage
- Appropriate color based on health status
- Visual indication of project health

## 🛠️ Technical Implementation

### Core Components

1. **Coverage Health Script** (`.github/scripts/coverage-health.py`)

   - Parses coverage data from XML/JSON formats
   - Calculates coverage deltas between branches
   - Generates health reports and status indicators
   - Creates markdown summaries for PR comments

2. **Badge Update Script** (`.github/scripts/update-coverage-badge.py`)

   - Updates README.md coverage badge
   - Maintains color-coded visual indicators
   - Supports automatic badge insertion/replacement

3. **GitHub Actions Integration**
   - Automated workflow execution on PRs
   - Status check creation via GitHub API
   - PR comment management with detailed reports

### Coverage Calculation

Coverage is calculated from **unit tests only** to ensure:

- Fast execution (≈0.34s vs 57s for integration tests)
- Reliable CI performance without ML dependencies
- Focus on core business logic coverage

Integration tests are run separately in Docker containers with full ML dependencies.

## 📈 Usage Guide

### For Developers

**When Creating PRs**:

1. Review coverage health check comment on your PR
2. Ensure coverage maintains or improves baseline
3. Add tests if coverage drops significantly
4. Use coverage report to identify untested code paths

**Local Coverage Testing**:

```bash
cd face-rekon
python run_tests.py coverage
```

### For Maintainers

**Monitoring Coverage Health**:

- Check PR coverage status before merging
- Review coverage trends over time
- Adjust thresholds if needed via environment variables

**Manual Coverage Analysis**:

```bash
# Run coverage health check locally
python .github/scripts/coverage-health.py face-rekon/coverage.xml
```

## ⚙️ Configuration

### Environment Variables

| Variable            | Default | Description                         |
| ------------------- | ------- | ----------------------------------- |
| `BASELINE_COVERAGE` | `67.0`  | Target baseline coverage percentage |

### Threshold Customization

Modify thresholds in `.github/scripts/coverage-health.py`:

```python
class CoverageHealthChecker:
    def __init__(self, baseline_coverage: float = 67.0):
        self.baseline = baseline_coverage
        self.green_threshold = baseline_coverage  # ≥67%
        self.amber_threshold = 60.0              # 60-66%
        # Red threshold < 60%
```

## 📊 Coverage Reports

### PR Comments Include

- **Current coverage percentage**
- **Coverage delta** (comparison to main branch)
- **Health status** with emoji indicators
- **Lines covered** vs total lines
- **Package-level breakdown** (if available)
- **Actionable recommendations** based on status

### Artifact Storage

Coverage reports are stored as GitHub Actions artifacts for 30 days:

- `coverage-pr.xml/json` - PR branch coverage
- `coverage-main.xml/json` - Baseline coverage
- `coverage-report.md` - Markdown summary
- `status-check.json` - Status check data

## 🎯 Best Practices

### Maintaining Coverage

1. **Write tests for new code** before pushing
2. **Review coverage reports** in PR comments
3. **Focus on critical code paths** first
4. **Refactor complex functions** to improve testability

### When Coverage Drops

**🟡 Amber Status (60-66%)**:

- Consider adding tests for new functionality
- Review if critical paths are covered
- Generally acceptable for feature development

**🔴 Red Status (<60%)**:

- **Action required** - CI will fail
- Add comprehensive tests before merging
- Consider breaking down complex changes
- Ensure critical functionality is tested

## 🔗 Integration Points

### GitHub Status Checks

Coverage health appears as a status check on PRs:

- **Context**: `coverage/health`
- **Description**: Emoji + percentage + delta
- **Link**: Points to workflow run for details

### PR Comments

Automated comments include:

- Full coverage analysis
- Trend information
- Actionable guidance
- Package/file-level details

### Workflow Dependencies

The coverage health check runs independently but coordinates with:

- Main CI workflow for comprehensive testing
- Release automation for version management
- Code quality checks for holistic review

---

## 📞 Support

For questions or issues with the coverage health check system:

1. Check workflow logs in GitHub Actions
2. Review this guide for configuration options
3. Open an issue for system improvements
4. Refer to individual script documentation

**Generated Coverage Report Example**:

> ## 🟢 Coverage Health Check: PASS
>
> **Current Coverage:** 67.2%
> **Baseline Coverage:** 67.0%
> **Coverage Delta:** +0.2% (maintained)
>
> **Lines Covered:** 142/210
>
> ### ✅ Great job maintaining test coverage!
