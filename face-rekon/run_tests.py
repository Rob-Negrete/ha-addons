#!/usr/bin/env python3
"""
Test runner script for face-rekon project.
Provides convenient commands for running different types of tests.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Command: {' '.join(command)}")
    print("-" * 60)

    try:
        result = subprocess.run(command, cwd=current_dir, check=True)
        print(f"✅ {description} completed successfully")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {command[0]}")
        return False


def run_unit_tests():
    """Run unit tests (fast, no external dependencies)"""
    command = [
        "python",
        "-m",
        "pytest",
        "tests/unit/test_simple.py",
        "-c",
        "pytest-unit.ini",
        "-v",
    ]
    return run_command(command, "Running Unit Tests")


def run_integration_tests():
    """Run integration tests (slower, requires more setup)"""
    # Check if we're in a container or have ML dependencies
    if os.environ.get("PYTHONPATH") == "/app":
        # We're in the test container - run in batches to manage memory
        test_batches = [
            ("API Integration Tests", "tests/integration/test_api_integration.py"),
            (
                "Database Integration Tests",
                "tests/integration/test_database_integration.py",
            ),
            ("End-to-End Integration Tests", "tests/integration/test_end_to_end.py"),
        ]

        all_passed = True
        for batch_name, batch_path in test_batches:
            print(f"\n🔧 Running {batch_name}")
            command = [
                "python",
                "-m",
                "pytest",
                batch_path,
                "-c",
                "pytest-integration.ini",
                "-v",
                "--tb=short",
            ]
            result = run_command(command, f"Running {batch_name}")
            if not result:
                all_passed = False
                break  # Stop on first failure to save resources

            # Force garbage collection between batches
            import gc

            gc.collect()

        return all_passed

    # Check if ML dependencies are available locally
    missing_ml_deps = []
    ml_deps = [
        ("insightface", "insightface"),
        ("opencv", "cv2"),
        ("faiss", "faiss"),
        ("tinydb", "tinydb"),
    ]

    for dep_name, import_name in ml_deps:
        try:
            __import__(import_name)
        except ImportError:
            missing_ml_deps.append(dep_name)

    if missing_ml_deps:
        print("\n⚠️  Integration tests require ML dependencies:")
        print(f"   Missing: {', '.join(missing_ml_deps)}")
        print("\n🐳 Run with Docker (recommended):")
        print("   docker compose -f docker compose.test.yml run integration-tests")
        print("\n📦 Or install locally:")
        print("   pip install -r requirements-integration.txt")
        print("\n🚀 Or run unit tests instead:")
        print("   python run_tests.py unit")
        return False

    command = [
        "python",
        "-m",
        "pytest",
        "tests/integration/",
        "-c",
        "pytest-integration.ini",
        "-v",
    ]
    return run_command(command, "Running Integration Tests")


def run_api_tests():
    """Run only API integration tests"""
    command = [
        "python",
        "-m",
        "pytest",
        "tests/integration/test_api_integration.py",
        "-c",
        "pytest-integration.ini",
        "-v",
    ]
    return run_command(command, "Running API Integration Tests")


def run_database_tests():
    """Run only database integration tests"""
    command = [
        "python",
        "-m",
        "pytest",
        "tests/integration/test_database_integration.py",
        "-c",
        "pytest-integration.ini",
        "-v",
    ]
    return run_command(command, "Running Database Integration Tests")


def run_e2e_tests():
    """Run end-to-end tests"""
    command = [
        "python",
        "-m",
        "pytest",
        "tests/integration/test_end_to_end.py",
        "-c",
        "pytest-integration.ini",
        "-v",
    ]
    return run_command(command, "Running End-to-End Tests")


def run_docker_tests():
    """Run tests in Docker containers"""
    command = [
        "docker compose",
        "-f",
        "docker compose.test.yml",
        "run",
        "--rm",
        "test-runner",
    ]
    return run_command(command, "Running Tests in Docker")


def run_docker_unit_tests():
    """Run unit tests in lightweight container"""
    command = [
        "docker compose",
        "-f",
        "docker compose.test.yml",
        "run",
        "--rm",
        "unit-tests",
    ]
    return run_command(command, "Running Unit Tests in Docker")


def run_docker_integration_tests():
    """Run integration tests in container"""
    command = [
        "docker compose",
        "-f",
        "docker compose.test.yml",
        "run",
        "--rm",
        "integration-tests",
    ]
    return run_command(command, "Running Integration Tests in Docker")


def run_ui_tests():
    """Run UI tests using npm"""
    command = ["npm", "test", "--prefix", "ui"]
    return run_command(command, "Running UI Tests")


def run_all_tests():
    """Run all tests in sequence"""
    print("🚀 Running Complete Test Suite")
    print("=" * 60)

    success = True

    # Run unit tests first (fastest)
    if not run_unit_tests():
        success = False

    # Run UI tests
    if not run_ui_tests():
        success = False

    # Run integration tests
    if not run_integration_tests():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check output above.")

    return success


def run_coverage():
    """Run tests with coverage report"""
    commands = [
        [
            "python",
            "-m",
            "pytest",
            "tests/unit/",
            "-c",
            "pytest-unit.ini",
            "--cov=scripts",
            "--cov-report=html",
            "--cov-report=term",
        ],
        [
            "python",
            "-m",
            "pytest",
            "tests/integration/",
            "-c",
            "pytest-integration.ini",
            "--cov=scripts",
            "--cov-append",
            "--cov-report=html",
            "--cov-report=term",
        ],
    ]

    success = True
    for command in commands:
        if not run_command(command, "Running Coverage Tests"):
            success = False

    if success:
        print("\n📊 Coverage report generated in htmlcov/index.html")

    return success


def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking Dependencies")
    print("-" * 30)

    required_packages = [
        ("pytest", "pytest"),
        ("flask", "flask"),
        ("pillow", "PIL"),
        ("numpy", "numpy"),
    ]

    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name.replace("-", "_"))
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - Missing")
            missing.append(package_name)

    if missing:
        print(f"\n⚠️  Install missing packages: pip install {' '.join(missing)}")
        return False

    print("\n✅ All required dependencies available")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Test runner for face-rekon project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py unit           # Run unit tests only
  python run_tests.py integration    # Run integration tests
  python run_tests.py api            # Run API tests only
  python run_tests.py e2e            # Run end-to-end tests
  python run_tests.py ui             # Run UI tests only
  python run_tests.py all            # Run all tests
  python run_tests.py coverage       # Run with coverage report
  python run_tests.py check          # Check dependencies
        """,
    )

    parser.add_argument(
        "test_type",
        choices=[
            "unit",
            "integration",
            "api",
            "database",
            "e2e",
            "ui",
            "all",
            "coverage",
            "check",
        ],
        help="Type of tests to run",
    )

    args = parser.parse_args()

    # Change to project directory
    os.chdir(current_dir)

    if args.test_type == "check":
        success = check_dependencies()
    elif args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "api":
        success = run_api_tests()
    elif args.test_type == "database":
        success = run_database_tests()
    elif args.test_type == "e2e":
        success = run_e2e_tests()
    elif args.test_type == "ui":
        success = run_ui_tests()
    elif args.test_type == "all":
        success = run_all_tests()
    elif args.test_type == "coverage":
        success = run_coverage()
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
