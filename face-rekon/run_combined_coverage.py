#!/usr/bin/env python3
"""
Combined Coverage Report Generator

This script runs both unit and integration tests and combines their coverage reports
to provide a comprehensive view of code coverage.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def setup_environment():
    """Set up test environment variables."""
    os.environ.update(
        {
            "QDRANT_PATH": "/tmp/test_qdrant_combined",
            "FACE_REKON_BASE_PATH": "/tmp/test_faces",
            "FACE_REKON_UNKNOWN_PATH": "/tmp/test_unknowns",
            "FACE_REKON_THUMBNAIL_PATH": "/tmp/test_thumbnails",
            "FACE_REKON_USE_EMBEDDED_QDRANT": "true",
        }
    )


def cleanup_old_reports():
    """Clean up old coverage reports."""
    coverage_files = [
        "coverage.xml",
        "coverage.json",
        "coverage-integration.xml",
        "coverage-integration.json",
        ".coverage",
        ".coverage.*",
    ]

    for pattern in coverage_files:
        run_command(f"rm -f {pattern}", f"Cleaning up {pattern}")


def run_unit_tests():
    """Run unit tests with coverage."""
    command = (
        "python -m pytest tests/unit/ "
        "-c pytest-unit.ini "
        "--cov=scripts "
        "--cov-report=xml:coverage-unit.xml "
        "--cov-report=json:coverage-unit.json "
        "--cov-report=term-missing "
        "-v"
    )
    return run_command(command, "Running unit tests with coverage")


def run_integration_tests():
    """Run integration tests with coverage."""
    command = "python -m pytest tests/integration/ " "-c pytest-integration.ini " "-v"
    return run_command(command, "Running integration tests with coverage")


def combine_coverage_reports():
    """Combine unit and integration coverage reports."""
    print("\n🔄 Combining coverage reports...")

    # Check if coverage files exist
    unit_coverage = Path("coverage-unit.xml")
    integration_coverage = Path("coverage-integration.xml")

    if not unit_coverage.exists():
        print("⚠️ Unit test coverage report not found")
        return False

    if not integration_coverage.exists():
        print("⚠️ Integration test coverage report not found")
        return False

    # Use coverage combine to merge data files
    combine_cmd = "python -m coverage combine"
    if not run_command(combine_cmd, "Combining coverage data"):
        return False

    # Generate combined reports
    report_commands = [
        (
            "python -m coverage xml -o coverage-combined.xml",
            "Generating combined XML report",
        ),
        (
            "python -m coverage json -o coverage-combined.json",
            "Generating combined JSON report",
        ),
        (
            "python -m coverage html -d htmlcov-combined",
            "Generating combined HTML report",
        ),
        (
            "python -m coverage report --show-missing",
            "Displaying combined coverage report",
        ),
    ]

    for cmd, desc in report_commands:
        if not run_command(cmd, desc):
            return False

    return True


def display_coverage_summary():
    """Display coverage summary from combined report."""
    print("\n📊 Combined Coverage Summary:")
    print("=" * 50)

    try:
        import json

        with open("coverage-combined.json", "r") as f:
            data = json.load(f)

        total_coverage = data["totals"]["percent_covered"]
        print(f"🎯 Overall Coverage: {total_coverage:.1f}%")

        print("\n📁 File Coverage:")
        for filename, file_data in data["files"].items():
            coverage = file_data["summary"]["percent_covered"]
            missing_lines = len(file_data["missing_lines"])
            print(f"  {filename}: {coverage:.1f}% ({missing_lines} lines missing)")

    except Exception as e:
        print(f"⚠️ Could not parse combined coverage report: {e}")
        run_command("python -m coverage report", "Fallback coverage display")


def main():
    """Main function to run combined coverage analysis."""
    print("🧪 Running Combined Coverage Analysis")
    print("=" * 50)

    setup_environment()
    cleanup_old_reports()

    # Run tests
    unit_success = run_unit_tests()
    integration_success = run_integration_tests()

    if not unit_success and not integration_success:
        print("❌ Both unit and integration tests failed")
        sys.exit(1)
    elif not unit_success:
        print("⚠️ Unit tests failed, but integration tests passed")
    elif not integration_success:
        print("⚠️ Integration tests failed, but unit tests passed")
    else:
        print("✅ Both unit and integration tests passed")

    # Combine coverage reports if possible
    if unit_success or integration_success:
        if combine_coverage_reports():
            display_coverage_summary()
            print("\n🎉 Combined coverage analysis completed successfully!")
            print("📄 Reports generated:")
            print("  - coverage-combined.xml (XML format)")
            print("  - coverage-combined.json (JSON format)")
            print("  - htmlcov-combined/ (HTML format)")
        else:
            print("⚠️ Failed to combine coverage reports")

    # Return appropriate exit code
    if unit_success and integration_success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
