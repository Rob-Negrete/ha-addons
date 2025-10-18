#!/usr/bin/env python3
"""
Smart coverage target selection for /bump-coverage workflow.

This script analyzes coverage data and validates that the selected function
truly has 0% coverage by checking against actual test execution results.

Usage:
    python scripts/select_coverage_target.py [--min-lines MIN] [--exclude PATTERN]
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def parse_coverage_json(json_path: Path) -> Dict:
    """Parse coverage JSON file."""
    with open(json_path) as f:
        return json.load(f)


def extract_functions_with_low_coverage(
    coverage_data: Dict, min_lines: int = 5, max_coverage: float = 80.0
) -> List[Dict]:
    """
    Extract functions with coverage below threshold.

    Args:
        coverage_data: Parsed coverage JSON
        min_lines: Minimum number of lines for a function to be considered
        max_coverage: Maximum coverage percentage to include (default: 80%)

    Returns:
        List of function dictionaries sorted by coverage (lowest first)
    """
    functions = []

    for file_path, file_data in coverage_data.get("files", {}).items():
        if "functions" not in file_data:
            continue

        for func_name, func_data in file_data["functions"].items():
            if func_name == "":  # Skip module-level code
                continue

            summary = func_data["summary"]
            coverage = summary["percent_covered"]
            lines = summary["num_statements"]
            missing = summary["missing_lines"]

            # Only include functions with enough lines and below threshold
            if lines >= min_lines and coverage <= max_coverage:
                functions.append(
                    {
                        "file": file_path.replace("scripts/", ""),
                        "function": func_name,
                        "coverage": coverage,
                        "lines": lines,
                        "missing_count": missing,
                        "missing_lines": func_data.get("missing_lines", []),
                    }
                )

    # Sort by coverage (lowest first), then by line count (more lines first)
    functions.sort(key=lambda x: (x["coverage"], -x["lines"]))

    return functions


def check_existing_tests(function_info: Dict) -> Tuple[bool, List[str]]:
    """
    Check if function already has test coverage by searching test files.

    Args:
        function_info: Dictionary with function information

    Returns:
        Tuple of (has_tests, list_of_test_files)
    """
    func_name = function_info["function"]

    # Extract endpoint path if it's a Flask route
    endpoint_path = None
    if "::" in func_name:
        # e.g., "Face.patch" -> check for "/face-rekon/<id>" patterns
        class_method = func_name.split("::")[-1]
        if "." in class_method:
            resource, method = class_method.rsplit(".", 1)
            if method.lower() in ["get", "post", "patch", "put", "delete"]:
                # This is likely a REST endpoint
                endpoint_path = f"/{resource.lower()}"

    test_files = []
    test_dir = Path("tests/integration")

    if not test_dir.exists():
        return False, []

    # Search patterns
    search_patterns = [
        f"test_{func_name.lower().replace('.', '_')}",  # Direct function name
        func_name.lower(),  # Function name in test
    ]

    if endpoint_path:
        # Add endpoint-specific patterns
        search_patterns.extend(
            [
                f'"{endpoint_path}',  # Exact endpoint path
                f"'{endpoint_path}",  # Alternate quotes
            ]
        )

    # Special handling for Flask REST resource methods
    if "." in func_name:
        parts = func_name.split(".")
        if len(parts) == 2:
            resource, method = parts
            # For Face.patch -> check for "client.patch" anywhere in tests
            search_patterns.append(f"client.{method.lower()}(")
            # Also check for update_face_endpoint (common naming pattern)
            if method.lower() == "patch":
                search_patterns.append("test_update_face_endpoint")

    # Search all integration test files
    for test_file in test_dir.glob("test_*.py"):
        try:
            content = test_file.read_text()

            # Check if any pattern matches
            for pattern in search_patterns:
                if pattern in content.lower():
                    test_files.append(str(test_file))
                    break

        except Exception as e:
            print(f"⚠️  Warning: Could not read {test_file}: {e}", file=sys.stderr)

    return len(test_files) > 0, test_files


def validate_with_actual_coverage(
    function_info: Dict, coverage_json_path: Path
) -> bool:
    """
    Validate that function truly has low coverage by checking the actual
    coverage report that includes both unit and integration tests.

    Args:
        function_info: Dictionary with function information
        coverage_json_path: Path to the coverage JSON to validate against

    Returns:
        True if function truly has low coverage, False if already covered
    """
    if not coverage_json_path.exists():
        print(
            f"⚠️  Warning: {coverage_json_path} not found, " "cannot validate coverage",
            file=sys.stderr,
        )
        return True  # Assume valid if we can't check

    try:
        data = parse_coverage_json(coverage_json_path)

        # Find the function in the coverage data
        for file_path, file_data in data.get("files", {}).items():
            if function_info["file"] not in file_path:
                continue

            if "functions" not in file_data:
                continue

            for func_name, func_data in file_data["functions"].items():
                if func_name == function_info["function"]:
                    actual_coverage = func_data["summary"]["percent_covered"]

                    # If actual coverage is > 80%, this function is already covered
                    if actual_coverage > 80.0:
                        print(
                            f"⚠️  {function_info['function']} shows "
                            f"{actual_coverage:.1f}% coverage in "
                            f"{coverage_json_path.name}",
                            file=sys.stderr,
                        )
                        return False

        return True

    except Exception as e:
        print(
            f"⚠️  Error validating coverage from {coverage_json_path}: {e}",
            file=sys.stderr,
        )
        return True  # Assume valid if validation fails


def select_target(
    min_lines: int = 5,
    exclude_pattern: Optional[str] = None,
    verbose: bool = False,
) -> Optional[Dict]:
    """
    Select the best coverage improvement target with validation.

    Args:
        min_lines: Minimum number of lines for consideration
        exclude_pattern: Regex pattern to exclude functions
        verbose: Print detailed progress

    Returns:
        Dictionary with function information or None if no suitable target
    """
    # Look for coverage files in priority order
    coverage_files = [
        Path(".coverage-results/coverage-integration.json"),
        Path("coverage-integration.json"),
        Path(".coverage-results/coverage-unit.json"),
        Path("coverage-unit.json"),
        Path("coverage.json"),
    ]

    coverage_data = None
    coverage_source = None

    for coverage_file in coverage_files:
        if coverage_file.exists():
            if verbose:
                print(f"📊 Found coverage file: {coverage_file}", file=sys.stderr)
            coverage_data = parse_coverage_json(coverage_file)
            coverage_source = coverage_file
            break

    if coverage_data is None:
        print("❌ No coverage JSON found. Run tests first.", file=sys.stderr)
        return None

    # Extract low-coverage functions
    candidates = extract_functions_with_low_coverage(
        coverage_data, min_lines=min_lines, max_coverage=80.0
    )

    if not candidates:
        print("✅ All functions have >80% coverage!", file=sys.stderr)
        return None

    if verbose:
        print(
            f"\n📋 Found {len(candidates)} functions with <80% coverage",
            file=sys.stderr,
        )

    # Filter by exclude pattern
    if exclude_pattern:
        pattern = re.compile(exclude_pattern, re.IGNORECASE)
        candidates = [
            c for c in candidates if not pattern.search(f"{c['file']}::{c['function']}")
        ]
        if verbose:
            print(f"   After exclusions: {len(candidates)} candidates", file=sys.stderr)

    # Validate each candidate
    for i, candidate in enumerate(candidates, 1):
        if verbose:
            print(
                f"\n{i}. Evaluating: {candidate['file']}::{candidate['function']} "
                f"({candidate['coverage']:.1f}%)",
                file=sys.stderr,
            )

        # Check for existing tests
        has_tests, test_files = check_existing_tests(candidate)
        if has_tests:
            if verbose:
                print(
                    f"   ⚠️  Found existing tests in: {', '.join(test_files)}",
                    file=sys.stderr,
                )
            continue

        # Validate against integration coverage if available
        integration_coverage = Path(".coverage-results/coverage-integration.json")
        if integration_coverage.exists() and integration_coverage != coverage_source:
            if not validate_with_actual_coverage(candidate, integration_coverage):
                if verbose:
                    print(
                        "   ⚠️  Already covered in integration tests", file=sys.stderr
                    )
                continue

        # This is a valid candidate!
        if verbose:
            print("   ✅ Valid target found!", file=sys.stderr)
        return candidate

    print(
        "❌ No suitable targets found. All low-coverage functions "
        "already have tests.",
        file=sys.stderr,
    )
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Select coverage improvement target with validation"
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=5,
        help="Minimum number of lines (default: 5)",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        help="Regex pattern to exclude functions",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed progress",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    target = select_target(
        min_lines=args.min_lines,
        exclude_pattern=args.exclude,
        verbose=args.verbose,
    )

    if target is None:
        sys.exit(1)

    # Output result
    if args.format == "json":
        print(json.dumps(target, indent=2))
    else:
        print(f"{target['file']}::{target['function']}")
        if args.verbose:
            print(
                f"\nCoverage: {target['coverage']:.1f}%",
                file=sys.stderr,
            )
            print(
                f"Lines: {target['lines']} " f"({target['missing_count']} missing)",
                file=sys.stderr,
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
