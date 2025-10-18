#!/usr/bin/env python3
"""
Centralized Coverage Configuration Module

This module provides a single source of truth for all coverage thresholds
and baselines used across the project. All values are loaded from the
centralized YAML configuration file.

Usage:
    from coverage_config import CoverageConfig

    config = CoverageConfig()
    baseline = config.baseline_coverage
    green_threshold = config.green_threshold
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML not installed, using default values", file=sys.stderr)
    yaml = None


class CoverageConfig:
    """
    Centralized coverage configuration with fallback defaults.

    All configuration values are loaded from .github/config/coverage-thresholds.yml.
    If the file is not found or YAML parsing fails, sensible defaults are used.
    """

    # Default configuration (fallback if YAML file not found)
    DEFAULT_CONFIG = {
        "baseline_coverage": 80.0,
        "thresholds": {
            "green_min": 80.0,
            "amber_min": 70.0,
            "amber_max": 79.9,
            "red_max": 69.9,
        },
        "file_priorities": {
            "high_priority_max": 60.0,
            "medium_priority_max": 80.0,
        },
        "target_selection": {
            "max_coverage_threshold": 80.0,
            "min_lines": 5,
        },
        "display": {
            "decimal_places": 2,
            "status_emojis": {
                "green": "🟢",
                "amber": "🟡",
                "red": "🔴",
            },
        },
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize coverage configuration.

        Args:
            config_path: Path to coverage-thresholds.yml (auto-detected if None)
        """
        self._config = self._load_config(config_path)

    def _load_config(self, config_path: Optional[Path] = None) -> Dict:
        """Load configuration from YAML file with fallback to defaults."""
        if config_path is None:
            # Auto-detect config file location
            script_dir = Path(__file__).parent
            config_path = script_dir / "../config/coverage-thresholds.yml"

        config_path = Path(config_path).resolve()

        # Try to load from YAML file
        if yaml and config_path.exists():
            try:
                with open(config_path) as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        return loaded_config
            except Exception as e:
                print(
                    f"⚠️  Failed to load {config_path}: {e}. Using defaults.",
                    file=sys.stderr,
                )

        # Fallback to defaults
        return self.DEFAULT_CONFIG.copy()

    # Baseline coverage
    @property
    def baseline_coverage(self) -> float:
        """Primary baseline coverage percentage."""
        # Check environment variable first (for backward compatibility)
        env_baseline = os.getenv("BASELINE_COVERAGE")
        if env_baseline:
            return float(env_baseline)
        return self._config.get("baseline_coverage", 80.0)

    # Status thresholds
    @property
    def green_threshold(self) -> float:
        """Minimum coverage for green/pass status."""
        return self._config.get("thresholds", {}).get("green_min", 80.0)

    @property
    def amber_threshold(self) -> float:
        """Minimum coverage for amber/warning status."""
        return self._config.get("thresholds", {}).get("amber_min", 70.0)

    @property
    def amber_max(self) -> float:
        """Maximum coverage for amber/warning status."""
        return self._config.get("thresholds", {}).get("amber_max", 79.9)

    @property
    def red_threshold(self) -> float:
        """Maximum coverage for red/fail status."""
        return self._config.get("thresholds", {}).get("red_max", 69.9)

    # File priority thresholds
    @property
    def high_priority_threshold(self) -> float:
        """Maximum coverage for HIGH priority files."""
        return self._config.get("file_priorities", {}).get("high_priority_max", 60.0)

    @property
    def medium_priority_threshold(self) -> float:
        """Maximum coverage for MEDIUM priority files."""
        return self._config.get("file_priorities", {}).get("medium_priority_max", 80.0)

    # Target selection thresholds
    @property
    def max_coverage_threshold(self) -> float:
        """Maximum coverage for smart target selection."""
        return self._config.get("target_selection", {}).get(
            "max_coverage_threshold", 80.0
        )

    @property
    def min_lines(self) -> int:
        """Minimum lines for target selection."""
        return self._config.get("target_selection", {}).get("min_lines", 5)

    # Display settings
    @property
    def decimal_places(self) -> int:
        """Decimal places for coverage percentages."""
        return self._config.get("display", {}).get("decimal_places", 2)

    @property
    def green_emoji(self) -> str:
        """Emoji for green/pass status."""
        return (
            self._config.get("display", {}).get("status_emojis", {}).get("green", "🟢")
        )

    @property
    def amber_emoji(self) -> str:
        """Emoji for amber/warning status."""
        return (
            self._config.get("display", {}).get("status_emojis", {}).get("amber", "🟡")
        )

    @property
    def red_emoji(self) -> str:
        """Emoji for red/fail status."""
        return self._config.get("display", {}).get("status_emojis", {}).get("red", "🔴")

    def get_status_emoji(self, coverage: float) -> str:
        """
        Get status emoji for a given coverage percentage.

        Args:
            coverage: Coverage percentage

        Returns:
            Appropriate emoji (green, amber, or red)
        """
        if coverage >= self.green_threshold:
            return self.green_emoji
        elif coverage >= self.amber_threshold:
            return self.amber_emoji
        else:
            return self.red_emoji

    def get_file_priority(self, coverage: float) -> str:
        """
        Get priority level for a file based on coverage.

        Args:
            coverage: File coverage percentage

        Returns:
            Priority string with emoji (e.g., "🔴 HIGH", "🟡 MEDIUM", "🟢 LOW")
        """
        if coverage < self.high_priority_threshold:
            return f"{self.red_emoji} HIGH"
        elif coverage < self.medium_priority_threshold:
            return f"{self.amber_emoji} MEDIUM"
        else:
            return f"{self.green_emoji} LOW"

    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"CoverageConfig(baseline={self.baseline_coverage}%, "
            f"green≥{self.green_threshold}%, "
            f"amber={self.amber_threshold}-{self.amber_max}%, "
            f"red<{self.amber_threshold}%)"
        )


# Singleton instance for easy import
_default_config = None


def get_config() -> CoverageConfig:
    """
    Get the default coverage configuration instance.

    Returns:
        Singleton CoverageConfig instance
    """
    global _default_config
    if _default_config is None:
        _default_config = CoverageConfig()
    return _default_config


if __name__ == "__main__":
    # Test/demo the configuration
    config = get_config()
    print("📊 Coverage Configuration")
    print("=" * 50)
    print(f"Baseline Coverage: {config.baseline_coverage}%")
    print("\nStatus Thresholds:")
    print(f"  {config.green_emoji} Green (Pass):    ≥{config.green_threshold}%")
    print(
        f"  {config.amber_emoji} Amber (Warning): "
        f"{config.amber_threshold}% - {config.amber_max}%"
    )
    print(f"  {config.red_emoji} Red (Fail):      <{config.amber_threshold}%")
    print("\nFile Priority Thresholds:")
    print(f"  {config.red_emoji} HIGH:   <{config.high_priority_threshold}%")
    print(f"  {config.amber_emoji} MEDIUM: <{config.medium_priority_threshold}%")
    print(f"  {config.green_emoji} LOW:    ≥{config.medium_priority_threshold}%")
    print("\nTarget Selection:")
    print(f"  Max coverage: {config.max_coverage_threshold}%")
    print(f"  Min lines: {config.min_lines}")
    print("\n" + str(config))
