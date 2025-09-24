#!/usr/bin/env python3
"""
Coverage Health Check Script for ha-addons repository.

This script analyzes test coverage and provides health status indicators:
- 🟢 Green: Coverage maintained or improved (≥67%)
- 🟡 Amber: Minor coverage decrease (60-66%)
- 🔴 Red: Significant coverage drop (<60%)
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional, Tuple


class CoverageHealthChecker:
    def __init__(self, baseline_coverage: float = 67.0):
        """
        Initialize coverage health checker.

        Args:
            baseline_coverage: The baseline coverage percentage to maintain
        """
        self.baseline = baseline_coverage
        self.green_threshold = baseline_coverage  # ≥67%
        self.amber_threshold = 60.0  # 60-66%
        # Red threshold < 60%

    def parse_coverage_xml(self, xml_path: Path) -> Optional[Dict]:
        """
        Parse coverage.xml file and extract coverage data.

        Returns:
            Dict with coverage information or None if parsing fails
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Get overall coverage
            coverage_attr = root.attrib
            lines_covered = int(coverage_attr.get("lines-covered", 0))
            lines_valid = int(coverage_attr.get("lines-valid", 1))
            line_rate = float(coverage_attr.get("line-rate", 0.0)) * 100

            # Get per-package coverage
            packages = {}
            for package in root.findall(".//package"):
                package_name = package.get("name", "unknown")
                package_line_rate = float(package.get("line-rate", 0.0)) * 100
                packages[package_name] = package_line_rate

            return {
                "line_rate": line_rate,
                "lines_covered": lines_covered,
                "lines_valid": lines_valid,
                "packages": packages,
            }
        except Exception as e:
            print(f"❌ Error parsing coverage XML: {e}")
            return None

    def parse_coverage_json(self, json_path: Path) -> Optional[Dict]:
        """
        Parse coverage.json file and extract coverage data.

        Returns:
            Dict with coverage information or None if parsing fails
        """
        try:
            with open(json_path, "r") as f:
                data = json.load(f)

            # Extract summary data
            summary = data.get("totals", {})
            covered_lines = summary.get("covered_lines", 0)
            num_statements = summary.get("num_statements", 1)
            percent_covered = summary.get("percent_covered", 0.0)

            # Extract file-level coverage
            files = {}
            for filepath, file_data in data.get("files", {}).items():
                file_summary = file_data.get("summary", {})
                files[filepath] = file_summary.get("percent_covered", 0.0)

            return {
                "line_rate": percent_covered,
                "lines_covered": covered_lines,
                "lines_valid": num_statements,
                "files": files,
            }
        except Exception as e:
            print(f"❌ Error parsing coverage JSON: {e}")
            return None

    def get_health_status(self, coverage_rate: float) -> Tuple[str, str, str]:
        """
        Determine health status based on coverage rate.

        Returns:
            Tuple of (emoji, color, status_text)
        """
        if coverage_rate >= self.green_threshold:
            return "🟢", "green", "PASS"
        elif coverage_rate >= self.amber_threshold:
            return "🟡", "amber", "WARNING"
        else:
            return "🔴", "red", "FAIL"

    def calculate_coverage_delta(self, current: float, baseline: float) -> float:
        """Calculate coverage delta (current - baseline)."""
        return current - baseline

    def generate_health_report(
        self, current_coverage: Dict, baseline_coverage: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive coverage health report.

        Args:
            current_coverage: Current coverage data
            baseline_coverage: Baseline coverage data (optional)

        Returns:
            Dict containing health report
        """
        current_rate = current_coverage["line_rate"]
        emoji, color, status = self.get_health_status(current_rate)

        # Calculate delta if baseline provided
        delta = 0.0
        baseline_rate = self.baseline
        if baseline_coverage:
            baseline_rate = baseline_coverage["line_rate"]
            delta = self.calculate_coverage_delta(current_rate, baseline_rate)

        # Determine if delta is significant
        delta_status = "maintained"
        if delta > 1.0:
            delta_status = "improved"
        elif delta < -5.0:
            delta_status = "decreased significantly"
        elif delta < 0:
            delta_status = "decreased slightly"

        return {
            "status": status,
            "emoji": emoji,
            "color": color,
            "current_coverage": round(current_rate, 2),
            "baseline_coverage": round(baseline_rate, 2),
            "delta": round(delta, 2),
            "delta_status": delta_status,
            "lines_covered": current_coverage["lines_covered"],
            "lines_total": current_coverage["lines_valid"],
            "should_fail_ci": current_rate < self.amber_threshold,  # Fail CI if < 60%
            "packages": current_coverage.get("packages", {}),
            "files": current_coverage.get("files", {}),
        }

    def generate_markdown_summary(self, report: Dict) -> str:
        """Generate markdown summary for PR comments."""
        emoji = report["emoji"]
        status = report["status"]
        current = report["current_coverage"]
        baseline = report["baseline_coverage"]
        delta = report["delta"]
        delta_status = report["delta_status"]

        delta_sign = "+" if delta >= 0 else ""

        summary = f"""## {emoji} Coverage Health Check: {status}

**Current Coverage:** {current}%
**Baseline Coverage:** {baseline}%
**Coverage Delta:** {delta_sign}{delta}% ({delta_status})

**Lines Covered:** {report['lines_covered']}/{report['lines_total']}

### Status Thresholds
- 🟢 **Green (Pass):** ≥ {self.green_threshold}%
- 🟡 **Amber (Warning):** {self.amber_threshold}% - {self.green_threshold-0.01}%
- 🔴 **Red (Fail):** < {self.amber_threshold}%
"""

        # Add package breakdown if available
        if report.get("packages"):
            summary += "\n### Package Coverage\n"
            for package, coverage in report["packages"].items():
                package_emoji, _, _ = self.get_health_status(coverage)
                summary += f"- {package_emoji} **{package}**: {coverage:.1f}%\n"

        # Add guidance based on status
        if report["status"] == "FAIL":
            summary += f"""
### ⚠️ Action Required
Coverage has dropped below the critical threshold of {self.amber_threshold}%. Please:
1. Add tests for new code
2. Review untested code paths
3. Consider refactoring complex functions
"""
        elif report["status"] == "WARNING":
            summary += f"""
### 💡 Recommendation
Coverage is below target ({self.green_threshold}%). Consider adding tests.
"""
        else:
            summary += "\n### ✅ Great job maintaining test coverage!"

        return summary

    def set_github_output(self, report: Dict):
        """Set GitHub Actions output variables."""
        outputs = {
            "status": report["status"],
            "emoji": report["emoji"],
            "color": report["color"],
            "coverage": str(report["current_coverage"]),
            "delta": str(report["delta"]),
            "should_fail": str(report["should_fail_ci"]).lower(),
        }

        # Set outputs for GitHub Actions using new format
        import os

        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                for key, value in outputs.items():
                    f.write(f"{key}={value}\n")
        else:
            # Fallback for local testing
            for key, value in outputs.items():
                print(f"{key}={value}")

    def create_status_check_data(
        self, report: Dict, context: str = "coverage/health"
    ) -> Dict:
        """Create data for GitHub status check API."""
        state_map = {
            "PASS": "success",
            "WARNING": "success",  # Don't fail CI for amber
            "FAIL": "failure",
        }

        return {
            "state": state_map[report["status"]],
            "target_url": None,  # Could link to coverage report
            "description": (
                f"Coverage: {report['current_coverage']}% "
                f"(Δ{report['delta']:+.1f}%) - {report['status']}"
            ),
            "context": context,
        }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python coverage-health.py <coverage-file> [baseline-file]")
        print("Supported formats: coverage.xml, coverage.json")
        sys.exit(1)

    coverage_file = Path(sys.argv[1])
    baseline_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not coverage_file.exists():
        print(f"❌ Coverage file not found: {coverage_file}")
        sys.exit(1)

    # Initialize checker with baseline from environment or default
    import os

    baseline_percentage = float(os.getenv("BASELINE_COVERAGE", "67.0"))
    checker = CoverageHealthChecker(baseline_percentage)

    # Parse current coverage
    current_coverage = None
    if coverage_file.suffix == ".xml":
        current_coverage = checker.parse_coverage_xml(coverage_file)
    elif coverage_file.suffix == ".json":
        current_coverage = checker.parse_coverage_json(coverage_file)
    else:
        print(f"❌ Unsupported coverage file format: {coverage_file.suffix}")
        sys.exit(1)

    if not current_coverage:
        print("❌ Failed to parse coverage data")
        sys.exit(1)

    # Parse baseline if provided
    baseline_coverage = None
    if baseline_file and baseline_file.exists():
        if baseline_file.suffix == ".xml":
            baseline_coverage = checker.parse_coverage_xml(baseline_file)
        elif baseline_file.suffix == ".json":
            baseline_coverage = checker.parse_coverage_json(baseline_file)

    # Generate health report
    report = checker.generate_health_report(current_coverage, baseline_coverage)

    # Output results
    print("📊 Coverage Health Report")
    print("=" * 50)
    print(f"Status: {report['emoji']} {report['status']}")
    print(f"Coverage: {report['current_coverage']}%")
    print(f"Delta: {report['delta']:+.2f}%")
    print(f"Should fail CI: {report['should_fail_ci']}")

    # Generate markdown for GitHub
    markdown = checker.generate_markdown_summary(report)

    # Write markdown to file for GitHub Actions
    with open("coverage-report.md", "w") as f:
        f.write(markdown)

    # Set GitHub outputs
    checker.set_github_output(report)

    # Create status check data
    status_data = checker.create_status_check_data(report)
    with open("status-check.json", "w") as f:
        json.dump(status_data, f, indent=2)

    print("\n📝 Generated files:")
    print("- coverage-report.md (for PR comments)")
    print("- status-check.json (for status checks)")

    # Exit with error code if coverage is critically low
    sys.exit(1 if report["should_fail_ci"] else 0)


if __name__ == "__main__":
    main()
