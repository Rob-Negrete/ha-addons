# Coverage Health Check Guide

This document explains the automated test coverage health check system for the ha-addons repository.

## 📊 Overview

The coverage health check system provides automated analysis of test coverage with intuitive status indicators:

- 🟢 **Green (Pass)**: Coverage maintained or improved (≥41.2%)
- 🟡 **Amber (Warning)**: Minor coverage decrease (35-41.1%)
- 🔴 **Red (Fail)**: Significant coverage drop (<35%)

## 🎯 Current Baseline

**Baseline Coverage**: **41.2%** (established from face-rekon addon unit tests)

This baseline represents the current test coverage state and serves as the target to maintain or improve. The project has been steadily improving coverage through systematic testing efforts.

## 🤖 Automated Workflows

### Coverage Health Check Workflow

**Trigger**: Pull Requests to `main` branch (via `workflow_run` after CI completes)
**Workflow File**: `.github/workflows/coverage-health.yml`

**Process**:

1. **Artifact Download**: Downloads comprehensive coverage reports from CI workflow using enhanced cross-workflow artifact system
2. **Fallback Mechanism**: If artifacts unavailable, runs unit tests directly on PR branch with coverage collection
3. **Baseline Comparison**: Runs unit tests on main branch for baseline comparison
4. **Health Analysis**: Analyzes coverage delta and determines health status
5. **PR Integration**: Posts comprehensive report as PR comment with actionable insights
6. **Status Checks**: Creates GitHub status check with emoji indicator
7. **CI Integration**: Fails CI if coverage drops below critical threshold (35%)

### CI Integration

The main CI workflow (`.github/workflows/ci.yml`) has been enhanced to:

- **Comprehensive Testing**: Run both unit and integration tests with coverage collection
- **Multi-Format Reports**: Generate coverage reports in multiple formats (XML, JSON)
- **Artifact Upload**: Upload coverage artifacts for cross-workflow access using `actions/upload-artifact@v4`
- **Codecov Integration**: Upload coverage data to Codecov for historical tracking
- **Health Check Support**: Provide reliable coverage data for automated health analysis

## 📋 Status Indicators

### Health Status Colors

| Status       | Coverage Range | Color       | CI Impact         |
| ------------ | -------------- | ----------- | ----------------- |
| 🟢 **Green** | ≥41.2%         | brightgreen | ✅ Pass           |
| 🟡 **Amber** | 35-41.1%       | yellow      | ⚠️ Warning (Pass) |
| 🔴 **Red**   | <35%           | red         | ❌ Fail           |

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
| `BASELINE_COVERAGE` | `41.2`  | Target baseline coverage percentage |

### Threshold Customization

Modify thresholds in `.github/scripts/coverage-health.py`:

```python
class CoverageHealthChecker:
    def __init__(self, baseline_coverage: float = 41.2):
        self.baseline = baseline_coverage
        self.green_threshold = baseline_coverage  # ≥41.2%
        self.amber_threshold = 35.0              # 35-41.1%
        # Red threshold < 35%
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

**🟡 Amber Status (35-41.1%)**:

- Consider adding tests for new functionality
- Review if critical paths are covered
- Generally acceptable for feature development

**🔴 Red Status (<35%)**:

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

## 🛠️ Troubleshooting

### Common Workflow Issues

**Issue**: Coverage Health Check workflow fails with "Artifact not found"
**Solution**:
- The workflow uses `dawidd6/action-download-artifact@v3` for cross-workflow artifact downloads
- If artifacts are unavailable, the fallback mechanism automatically runs tests directly
- Check CI workflow completion and artifact upload status

**Issue**: File path errors during coverage processing
**Solution**:
- Coverage artifacts are extracted directly to `coverage-artifacts/` (no subdirectory)
- Ensure file copying uses correct paths: `coverage-artifacts/coverage.xml`
- Check workflow logs for directory structure debugging output

**Issue**: Coverage baseline mismatch
**Solution**:
- Current baseline is 41.2% (configured in `BASELINE_COVERAGE` environment variable)
- Update local testing to match workflow baseline
- Verify coverage calculation method matches unit test scope

### Workflow Debugging

**Enable Debug Output**:
The coverage health workflow includes comprehensive debugging:

```yaml
# Debug workflow run info
echo "🔍 Workflow run debugging info:"
echo "  Workflow Run ID: ${{ github.event.workflow_run.id }}"
echo "  Event Type: workflow_run"

# Show artifact contents
echo "📁 Contents of coverage-artifacts directory:"
ls -la coverage-artifacts/
```

**Check Artifact Status**:
```bash
# View workflow run details
gh run view <run-id>

# Check artifact availability
gh api repos/owner/repo/actions/runs/<run-id>/artifacts
```

### Recovery Procedures

**If Coverage Health Check Fails**:
1. Check CI workflow completion status
2. Verify artifact upload succeeded
3. Review coverage-health workflow logs
4. Use fallback mechanism if needed
5. Manually trigger workflow with `workflow_dispatch` if necessary

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
> **Current Coverage:** 41.4%
> **Baseline Coverage:** 41.2%
> **Coverage Delta:** +0.2% (improved)
>
> **Lines Covered:** 142/343
>
> ### ✅ Great job improving test coverage!
>
> The baseline coverage is set at **41.2%** based on the current codebase state.
> Coverage includes both unit and integration tests from CI workflow.
