# Coverage Configuration

This directory contains centralized configuration for all coverage-related thresholds and baselines used across the project.

## Files

### `coverage-thresholds.yml`

**Single source of truth** for all coverage thresholds. Update this file to change coverage requirements project-wide.

**Configuration Sections:**

1. **`baseline_coverage`** (80.0)

   - Primary baseline coverage percentage
   - Used by CI/CD and all coverage tools

2. **`thresholds`**

   - `green_min`: Minimum for PASS status (≥80%)
   - `amber_min`: Minimum for WARNING status (≥70%)
   - `amber_max`: Maximum for WARNING status (<80%)
   - `red_max`: Maximum for FAIL status (<70%)

3. **`file_priorities`**

   - `high_priority_max`: Files below this are HIGH priority (<60%)
   - `medium_priority_max`: Files below this are MEDIUM priority (<80%)

4. **`target_selection`**

   - `max_coverage_threshold`: Max coverage for improvement targets (80%)
   - `min_lines`: Minimum lines for a function to be worth improving (5)

5. **`display`**
   - `decimal_places`: Decimal places in coverage reports (2)
   - `status_emojis`: Emojis for status indicators (🟢🟡🔴)

## Usage

### Python Scripts

All Python scripts automatically load configuration from this file:

```python
from coverage_config import get_config

config = get_config()
baseline = config.baseline_coverage  # 80.0
green_threshold = config.green_threshold  # 80.0
```

### GitHub Actions Workflows

The configuration is automatically loaded by coverage scripts. No environment variables needed!

```yaml
- name: Run coverage health analysis
  run: |
    # Automatically reads from .github/config/coverage-thresholds.yml
    python .github/scripts/coverage-health.py coverage.xml
```

## Scripts Using This Configuration

1. **`.github/scripts/coverage-health.py`**

   - Coverage health check for CI/CD
   - Uses: baseline, thresholds, file priorities, display settings

2. **`face-rekon/tests/utils/select_coverage_target.py`**

   - Smart target selection for `/bump-coverage`
   - Uses: max_coverage_threshold, min_lines

3. **`.github/workflows/coverage-health.yml`**
   - GitHub Actions workflow
   - Automatically uses values from config file

## How to Change Coverage Baseline

**Old Way (Multi-file updates):**

```bash
# Had to update baseline in 4+ different files:
.github/workflows/coverage-health.yml  # BASELINE_COVERAGE: "72.0"
.github/scripts/coverage-health.py     # baseline_coverage: float = 72.0
face-rekon/tests/utils/select_coverage_target.py  # max_coverage: float = 50.0
# ... and update all documentation examples
```

**New Way (Single file update):**

```bash
# Edit ONE file:
vim .github/config/coverage-thresholds.yml

# Change baseline_coverage: 80.0 to desired value
# All scripts and workflows automatically use the new value!
```

## Benefits

✅ **Single Source of Truth** - Update one file to change baseline everywhere
✅ **No Code Changes** - Change thresholds without modifying Python scripts
✅ **Self-Documenting** - YAML config is clear and readable
✅ **Backward Compatible** - Scripts still work with BASELINE_COVERAGE env var
✅ **Type-Safe** - Python module provides typed properties
✅ **Fallback Defaults** - Works even if YAML file is missing

## Testing Configuration Changes

```bash
# Test the configuration module
python .github/scripts/coverage_config.py

# Test coverage-health script
python .github/scripts/coverage-health.py face-rekon/coverage-unit.xml

# Test smart target selection
cd face-rekon && python tests/utils/select_coverage_target.py --verbose
```

## Example: Raising Baseline from 80% to 85%

```yaml
# 1. Edit .github/config/coverage-thresholds.yml
baseline_coverage: 85.0

thresholds:
  green_min: 85.0 # Update to match baseline
  amber_min: 75.0 # baseline - 10.0
  amber_max: 84.9 # baseline - 0.1
  red_max: 74.9 # amber_min - 0.1

file_priorities:
  high_priority_max: 65.0 # Can adjust as needed
  medium_priority_max: 85.0 # Match baseline

target_selection:
  max_coverage_threshold: 85.0 # Match baseline
```

```bash
# 2. Test the changes
python .github/scripts/coverage_config.py

# 3. Commit and push
git add .github/config/coverage-thresholds.yml
git commit -m "chore: raise coverage baseline from 80% to 85%"
```

That's it! All scripts, workflows, and documentation now use the new 85% baseline.
