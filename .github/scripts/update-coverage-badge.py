#!/usr/bin/env python3
"""
Script to update coverage badge in README.md based on latest coverage data.
"""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


def parse_coverage_from_xml(xml_path: Path) -> Optional[float]:
    """Parse coverage percentage from coverage.xml file."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        line_rate = float(root.attrib.get("line-rate", 0.0)) * 100
        return round(line_rate, 1)
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return None


def parse_coverage_from_json(json_path: Path) -> Optional[float]:
    """Parse coverage percentage from coverage.json file."""
    try:
        with open(json_path, "r") as f:
            data = json.load(f)

        summary = data.get("totals", {})
        percent_covered = summary.get("percent_covered", 0.0)
        return round(percent_covered, 1)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None


def get_badge_color(coverage: float) -> str:
    """Get badge color based on coverage percentage."""
    if coverage >= 67:
        return "brightgreen"
    elif coverage >= 60:
        return "yellow"
    elif coverage >= 40:
        return "orange"
    else:
        return "red"


def update_readme_badge(readme_path: Path, coverage: float) -> bool:
    """Update coverage badge in README.md file."""
    try:
        with open(readme_path, "r") as f:
            content = f.read()

        color = get_badge_color(coverage)
        new_badge = (
            f"![Coverage](https://img.shields.io/badge/coverage-{coverage}%25-{color})"
        )

        # Try to find existing coverage badge
        coverage_badge_pattern = (
            r"!\[Coverage\]\(" r"https://img\.shields\.io/badge/coverage-[^)]+\)"
        )

        if re.search(coverage_badge_pattern, content):
            # Replace existing badge
            updated_content = re.sub(coverage_badge_pattern, new_badge, content)
            print(f"Updated existing coverage badge: {coverage}% ({color})")
        else:
            # Look for insertion point (after title, before first section)
            lines = content.split("\n")
            insert_line = 1  # Default to after title

            # Find a better insertion point
            for i, line in enumerate(lines):
                if line.startswith("##") and i > 0:  # First section header
                    insert_line = i
                    break
                elif "badges" in line.lower() or "status" in line.lower():
                    insert_line = i + 1
                    break

            # Insert badge
            lines.insert(insert_line, f"\n{new_badge}\n")
            updated_content = "\n".join(lines)
            print(f"Added new coverage badge: {coverage}% ({color})")

        with open(readme_path, "w") as f:
            f.write(updated_content)

        return True
    except Exception as e:
        print(f"Error updating README: {e}")
        return False


def main():
    """Main entry point."""
    # Look for coverage files
    coverage_files = [
        Path("face-rekon/coverage.xml"),
        Path("coverage.xml"),
        Path("face-rekon/coverage.json"),
        Path("coverage.json"),
    ]

    coverage = None
    for coverage_file in coverage_files:
        if coverage_file.exists():
            if coverage_file.suffix == ".xml":
                coverage = parse_coverage_from_xml(coverage_file)
            elif coverage_file.suffix == ".json":
                coverage = parse_coverage_from_json(coverage_file)

            if coverage is not None:
                print(f"Found coverage: {coverage}% from {coverage_file}")
                break

    if coverage is None:
        print("No coverage data found")
        return 1

    # Update README
    readme_path = Path("README.md")
    if readme_path.exists():
        success = update_readme_badge(readme_path, coverage)
        if success:
            print("✅ README.md updated successfully")
            return 0
        else:
            print("❌ Failed to update README.md")
            return 1
    else:
        print("README.md not found")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
