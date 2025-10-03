#!/usr/bin/env python3
"""
Coverage Health Check Script for ha-addons repository.

This script analyzes test coverage and provides health status indicators:
- 🟢 Green: Coverage maintained or improved (≥72%)
- 🟡 Amber: Minor coverage decrease (65-71%)
- 🔴 Red: Significant coverage drop (<65%)
"""

import ast
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CoverageHealthChecker:
    def __init__(self, baseline_coverage: float = 72.0):
        """
        Initialize coverage health checker.

        Args:
            baseline_coverage: The baseline coverage percentage to maintain
        """
        self.baseline = baseline_coverage
        self.green_threshold = baseline_coverage  # ≥baseline%
        self.amber_threshold = max(65.0, baseline_coverage - 7.0)  # 7% below baseline
        # Red threshold < amber%

    def extract_functions_from_source(self, filepath: Path) -> List[Dict]:
        """
        Extract function definitions from Python source file.

        Returns:
            List of dicts with function name, start_line, end_line
        """
        try:
            with open(filepath, "r") as f:
                source = f.read()

            tree = ast.parse(source, str(filepath))
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    start_line = node.lineno
                    end_line = start_line
                    if node.body:
                        for stmt in node.body:
                            if hasattr(stmt, "end_lineno") and stmt.end_lineno:
                                end_line = max(end_line, stmt.end_lineno)

                    functions.append(
                        {
                            "name": node.name,
                            "start_line": start_line,
                            "end_line": end_line,
                        }
                    )

            return functions
        except Exception:
            # Silently skip files that can't be parsed (not Python, etc.)
            return []

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

            # Get per-file coverage for merging
            files = {}
            for package in root.findall(".//package"):
                for class_elem in package.findall(".//class"):
                    filename = class_elem.get("filename", "unknown")
                    line_rate_file = float(class_elem.get("line-rate", 0.0)) * 100

                    # Calculate lines_covered and lines_valid from <lines>
                    lines = class_elem.findall(".//line")
                    lines_valid_file = len(lines)
                    lines_covered_file = sum(
                        1 for line in lines if int(line.get("hits", "0")) > 0
                    )

                    # Store covered/uncovered line numbers for function analysis
                    covered_lines = set(
                        int(line.get("number"))
                        for line in lines
                        if int(line.get("hits", "0")) > 0
                    )
                    all_lines = set(int(line.get("number")) for line in lines)

                    files[filename] = {
                        "lines_covered": lines_covered_file,
                        "lines_valid": lines_valid_file,
                        "line_rate": line_rate_file,
                        "covered_lines": covered_lines,
                        "all_lines": all_lines,
                    }

            return {
                "line_rate": line_rate,
                "lines_covered": lines_covered,
                "lines_valid": lines_valid,
                "packages": packages,
                "files": files,
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

    def combine_coverage_data(self, coverage_list: list) -> Optional[Dict]:
        """
        Combine multiple coverage data dictionaries into one comprehensive result.

        Args:
            coverage_list: List of coverage data dictionaries from different test runs

        Returns:
            Combined coverage data dictionary or None if combination fails
        """
        if not coverage_list:
            return None

        if len(coverage_list) == 1:
            return coverage_list[0]

        try:
            # Initialize combined data with first coverage
            combined = coverage_list[0].copy()
            combined_files = {}
            combined_packages = {}

            # Process each coverage file
            for coverage_data in coverage_list:
                # Accumulate file-level coverage
                for filepath, file_data in coverage_data.get("files", {}).items():
                    if isinstance(file_data, dict):
                        # From XML format - take MAX coverage for each file
                        # (since tests cover the same code, we want best result)
                        if filepath not in combined_files:
                            combined_files[filepath] = file_data.copy()
                        else:
                            # Keep the file_data with higher coverage rate
                            existing = combined_files[filepath]
                            if file_data.get("line_rate", 0) > existing.get(
                                "line_rate", 0
                            ):
                                combined_files[filepath] = file_data.copy()
                    else:
                        # From JSON format (percentage value)
                        if filepath not in combined_files:
                            combined_files[filepath] = {"line_rate": file_data}
                        else:
                            # Take the max coverage for each file
                            existing_rate = combined_files[filepath].get("line_rate", 0)
                            if isinstance(existing_rate, dict):
                                existing_rate = existing_rate.get("line_rate", 0)
                            combined_files[filepath]["line_rate"] = max(
                                file_data, existing_rate
                            )

                # Accumulate package-level coverage
                for pkg_name, pkg_coverage in coverage_data.get("packages", {}).items():
                    if pkg_name not in combined_packages:
                        combined_packages[pkg_name] = pkg_coverage
                    else:
                        # Take the max coverage for each package
                        combined_packages[pkg_name] = max(
                            pkg_coverage, combined_packages[pkg_name]
                        )

            # Calculate true combined coverage from file-level data
            # by aggregating lines_covered and lines_valid from all files
            total_lines_covered = 0
            total_lines_valid = 0

            for filepath, file_data in combined_files.items():
                if isinstance(file_data, dict):
                    # From XML format with detailed file data
                    lines_cov = file_data.get("lines_covered", 0)
                    lines_val = file_data.get("lines_valid", 0)
                    total_lines_covered += lines_cov
                    total_lines_valid += lines_val
                else:
                    # From JSON format (percentage only) - skip
                    # We'll use XML data which has actual line counts
                    continue

            # Calculate overall coverage percentage from aggregated data
            if total_lines_valid > 0:
                combined_line_rate = (total_lines_covered / total_lines_valid) * 100
                combined["line_rate"] = combined_line_rate
                combined["lines_covered"] = total_lines_covered
                combined["lines_valid"] = total_lines_valid

                print(
                    "   📊 Calculated true combined coverage: "
                    f"{combined_line_rate:.2f}%"
                )
                print(f"   📈 Lines: " f"{total_lines_covered}/{total_lines_valid}")
            else:
                # Fallback: if no file-level data, use best single report
                best_coverage_rate = 0.0
                best_coverage_data = None

                for coverage_data in coverage_list:
                    if coverage_data.get("line_rate", 0) > best_coverage_rate:
                        best_coverage_rate = coverage_data.get("line_rate", 0)
                        best_coverage_data = coverage_data

                if best_coverage_data:
                    combined["line_rate"] = best_coverage_data["line_rate"]
                    combined["lines_covered"] = best_coverage_data["lines_covered"]
                    combined["lines_valid"] = best_coverage_data["lines_valid"]
                else:
                    combined["line_rate"] = combined.get("line_rate", 0)
                    combined["lines_covered"] = combined.get("lines_covered", 0)
                    combined["lines_valid"] = combined.get("lines_valid", 1)

            combined["files"] = combined_files
            combined["packages"] = combined_packages

            print(f"🔄 Combined {len(coverage_list)} coverage files:")
            print(f"   📊 Final coverage: {combined['line_rate']:.2f}%")
            lines_covered = combined["lines_covered"]
            lines_valid = combined["lines_valid"]
            print(f"   📈 Lines covered: {lines_covered}/{lines_valid}")

            return combined

        except Exception as e:
            print(f"❌ Error combining coverage data: {e}")
            return None

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

    def generate_markdown_summary(
        self,
        report: Dict,
        unit_coverage: Optional[Dict] = None,
        integration_coverage: Optional[Dict] = None,
    ) -> str:
        """
        Generate markdown summary for PR comments.

        Includes separate unit/integration tracking when available.
        """
        emoji = report["emoji"]
        status = report["status"]
        current = report["current_coverage"]
        baseline = report["baseline_coverage"]
        delta = report["delta"]

        delta_sign = "+" if delta >= 0 else ""

        summary = f"""## {emoji} Coverage Health Check: {status}

**Overall Coverage:** {current}% ({delta_sign}{delta}% vs baseline {baseline}%)
**Lines Covered:** {report['lines_covered']}/{report['lines_total']}

*📖 [Coverage Metrics Guide](../COVERAGE-GUIDE.md#understanding-coverage-metrics)*

"""

        # Add unit vs integration breakdown if both are available
        if unit_coverage and integration_coverage:
            unit_rate = unit_coverage["line_rate"]
            integration_rate = integration_coverage["line_rate"]

            # Calculate deltas if baseline exists
            unit_delta = unit_rate - baseline if baseline else 0.0
            integration_delta = integration_rate - baseline if baseline else 0.0

            unit_delta_sign = "+" if unit_delta >= 0 else ""
            integration_delta_sign = "+" if integration_delta >= 0 else ""

            summary += "### 📊 Coverage by Test Type\n\n"
            summary += "| Test Type | Coverage | Delta | Lines Covered |\n"
            summary += "|-----------|----------|-------|---------------|\n"
            summary += (
                f"| 🧪 **Unit Tests** | {unit_rate:.1f}% | "
                f"{unit_delta_sign}{unit_delta:.1f}% | "
                f"{unit_coverage['lines_covered']}/"
                f"{unit_coverage['lines_valid']} |\n"
            )
            summary += (
                f"| 🐳 **Integration Tests** | {integration_rate:.1f}% | "
                f"{integration_delta_sign}{integration_delta:.1f}% | "
                f"{integration_coverage['lines_covered']}/"
                f"{integration_coverage['lines_valid']} |\n"
            )
            summary += (
                f"| 📈 **Best Coverage** | {current}% | "
                f"{delta_sign}{delta:.1f}% | "
                f"{report['lines_covered']}/{report['lines_total']} |\n\n"
            )
            summary += (
                "*Best coverage represents the maximum coverage "
                "achieved across all test types*\n\n"
            )

        # Add undercovered files and functions section
        files = report.get("files", {})
        if files:
            undercovered = []
            for filepath, file_data in files.items():
                if isinstance(file_data, dict):
                    file_rate = file_data.get("line_rate", 0)
                    if file_rate < 70.0:  # Below 70% threshold
                        lines_covered = file_data.get("lines_covered", 0)
                        lines_valid = file_data.get("lines_valid", 1)
                        covered_lines = file_data.get("covered_lines", set())
                        all_lines = file_data.get("all_lines", set())

                        undercovered.append(
                            {
                                "file": filepath,
                                "coverage": file_rate,
                                "lines_covered": lines_covered,
                                "lines_valid": lines_valid,
                                "covered_lines": covered_lines,
                                "all_lines": all_lines,
                            }
                        )

            if undercovered:
                # Sort by coverage (lowest first)
                undercovered.sort(key=lambda x: x["coverage"])

                summary += "### 🎯 Priority: Undercovered Files (< 70%)\n\n"
                summary += (
                    "| File | Function | Coverage | Lines Missing | " "Priority |\n"
                )
                summary += (
                    "|------|----------|----------|---------------|" "----------|\n"
                )

                # Process each undercovered file
                for item in undercovered[:5]:  # Top 5 file priorities
                    file_name = item["file"]
                    file_coverage = item["coverage"]
                    file_missing = item["lines_valid"] - item["lines_covered"]
                    covered_lines = item["covered_lines"]
                    all_lines = item["all_lines"]

                    # Determine file-level priority
                    if file_coverage < 50:
                        file_priority = "🔴 HIGH"
                    elif file_coverage < 65:
                        file_priority = "🟡 MEDIUM"
                    else:
                        file_priority = "🟢 LOW"

                    # Try to find source file and extract functions
                    source_path = Path.cwd() / "scripts" / file_name
                    if not source_path.exists():
                        # Try without scripts prefix
                        source_path = Path.cwd() / file_name

                    functions = []
                    if source_path.exists():
                        functions = self.extract_functions_from_source(source_path)

                    if functions:
                        # Calculate coverage for each function
                        func_coverage_list = []
                        for func in functions:
                            func_lines = set(
                                range(func["start_line"], func["end_line"] + 1)
                            )
                            # Only count lines that are in coverage data
                            func_executable = func_lines & all_lines
                            func_covered = func_lines & covered_lines

                            if func_executable:
                                func_rate = (
                                    len(func_covered) / len(func_executable)
                                ) * 100
                                func_missing = len(func_executable) - len(func_covered)

                                # Only show functions with < 70% coverage
                                if func_rate < 70.0:
                                    func_coverage_list.append(
                                        {
                                            "name": func["name"],
                                            "coverage": func_rate,
                                            "missing": func_missing,
                                        }
                                    )

                        if func_coverage_list:
                            # Sort by coverage (lowest first)
                            func_coverage_list.sort(key=lambda x: x["coverage"])

                            # Show top 3 undercovered functions per file
                            for idx, func_item in enumerate(func_coverage_list[:3]):
                                func_name = func_item["name"]
                                func_cov = func_item["coverage"]
                                func_miss = func_item["missing"]

                                # Determine function priority
                                if func_cov < 30:
                                    func_priority = "🔴 HIGH"
                                elif func_cov < 50:
                                    func_priority = "🟡 MEDIUM"
                                else:
                                    func_priority = "🟢 LOW"

                                # Show file name only on first row
                                display_file = f"`{file_name}`" if idx == 0 else ""

                                summary += (
                                    f"| {display_file} | `{func_name}()` | "
                                    f"{func_cov:.1f}% | {func_miss} lines | "
                                    f"{func_priority} |\n"
                                )
                        else:
                            # No undercovered functions, show file-level
                            summary += (
                                f"| `{file_name}` | *(overall)* | "
                                f"{file_coverage:.1f}% | {file_missing} "
                                f"lines | {file_priority} |\n"
                            )
                    else:
                        # Can't parse functions, show file-level only
                        summary += (
                            f"| `{file_name}` | *(overall)* | "
                            f"{file_coverage:.1f}% | {file_missing} lines | "
                            f"{file_priority} |\n"
                        )

                summary += "\n"

        summary += "### Status Thresholds\n"
        summary += f"- 🟢 **Green (Pass):** ≥ {self.green_threshold}%\n"
        summary += (
            f"- 🟡 **Amber (Warning):** {self.amber_threshold}% - "
            f"{self.green_threshold-0.01}%\n"
        )
        summary += f"- 🔴 **Red (Fail):** < {self.amber_threshold}%\n"

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
        print(
            "Usage: python coverage-health.py <primary-coverage-file> "
            "[baseline-file]"
        )
        print("Supported formats: coverage.xml, coverage.json")
        print("Will automatically discover and combine additional coverage files.")
        sys.exit(1)

    primary_coverage_file = Path(sys.argv[1])
    baseline_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not primary_coverage_file.exists():
        print(f"❌ Primary coverage file not found: {primary_coverage_file}")
        sys.exit(1)

    # Initialize checker with baseline from environment or default
    import os

    baseline_percentage = float(os.getenv("BASELINE_COVERAGE", "72.0"))
    checker = CoverageHealthChecker(baseline_percentage)

    # Discover all available coverage files for comprehensive analysis
    current_dir = Path.cwd()
    discovered_files = set()

    # Always include the primary file
    discovered_files.add(primary_coverage_file.resolve())

    # Auto-discover additional coverage files (prioritize XML over JSON for same name)
    additional_patterns = ["coverage-*.xml", "*-coverage.xml"]

    for pattern in additional_patterns:
        for file_path in current_dir.glob(pattern):
            if file_path.suffix == ".xml":
                resolved_path = file_path.resolve()
                if resolved_path != primary_coverage_file.resolve():
                    discovered_files.add(resolved_path)

    # Convert to sorted list for consistent processing
    coverage_files = sorted(discovered_files)

    print(f"📊 Discovered {len(coverage_files)} coverage file(s):")
    for file_path in coverage_files:
        print(f"   • {file_path.name}")

    # Parse all coverage files and track unit vs integration separately
    coverage_data_list = []
    unit_coverage = None
    integration_coverage = None

    for coverage_file in coverage_files:
        print(f"🔄 Parsing {coverage_file.name}...")

        coverage_data = None
        if coverage_file.suffix == ".xml":
            coverage_data = checker.parse_coverage_xml(coverage_file)
        elif coverage_file.suffix == ".json":
            coverage_data = checker.parse_coverage_json(coverage_file)
        else:
            print(f"⚠️  Skipping unsupported format: {coverage_file.suffix}")
            continue

        if coverage_data:
            print(f"   ✅ Parsed: {coverage_data['line_rate']:.2f}% coverage")
            coverage_data_list.append(coverage_data)

            # Identify unit vs integration coverage by filename
            file_name = coverage_file.name.lower()
            if "unit" in file_name:
                unit_coverage = coverage_data
                print("   🧪 Identified as: Unit test coverage")
            elif "integration" in file_name:
                integration_coverage = coverage_data
                print("   🐳 Identified as: Integration test coverage")
        else:
            print(f"   ❌ Failed to parse {coverage_file.name}")

    if not coverage_data_list:
        print("❌ No valid coverage data found")
        sys.exit(1)

    # Combine multiple coverage files into comprehensive result
    print("🔄 Combining coverage data...")
    current_coverage = checker.combine_coverage_data(coverage_data_list)

    if not current_coverage:
        print("❌ Failed to combine coverage data")
        sys.exit(1)

    # Parse baseline if provided
    baseline_coverage = None
    if baseline_file and baseline_file.exists():
        print(f"🔄 Parsing baseline file: {baseline_file.name}")
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

    # Generate markdown for GitHub with unit/integration breakdown
    markdown = checker.generate_markdown_summary(
        report, unit_coverage=unit_coverage, integration_coverage=integration_coverage
    )

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
