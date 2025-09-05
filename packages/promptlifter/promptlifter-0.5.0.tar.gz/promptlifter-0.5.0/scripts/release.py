#!/usr/bin/env python3
"""
Release script for PromptLifter.

This script automates the process of building and uploading packages to PyPI.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True, capture_output=False):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, capture_output=capture_output, text=True)
    return result


def clean_build_artifacts():
    """Clean up build artifacts."""
    print("🧹 Cleaning build artifacts...")
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  Removed {path}")
            elif path.is_file():
                path.unlink()
                print(f"  Removed {path}")


def build_package():
    """Build the package."""
    print("🔨 Building package...")
    run_command([sys.executable, "-m", "build"])


def check_package():
    """Check the package for issues."""
    print("🔍 Checking package...")
    run_command([sys.executable, "-m", "twine", "check", "dist/*"])


def upload_to_test_pypi():
    """Upload to TestPyPI."""
    print("📤 Uploading to TestPyPI...")
    run_command(
        [
            sys.executable,
            "-m",
            "twine",
            "upload",
            "--repository",
            "testpypi",
            "--username",
            "__token__",
            "dist/*",
        ]
    )


def upload_to_pypi():
    """Upload to PyPI."""
    print("📤 Uploading to PyPI...")
    run_command(
        [sys.executable, "-m", "twine", "upload", "--username", "__token__", "dist/*"]
    )


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    run_command([sys.executable, "-m", "pytest", "tests/", "-v"])


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    required_packages = ["black", "flake8", "build", "twine"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package} installed")
        except ImportError:
            print(f"  ❌ {package} missing")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            run_command([sys.executable, "-m", "pip", "install", package])

    return True


def run_quality_checks():
    """Run quality checks."""
    print("✅ Running quality checks...")

    # Check formatting
    print("  Checking code formatting...")
    try:
        run_command([sys.executable, "-m", "black", "--check", "promptlifter", "tests"])
        print("  ✅ Code formatting OK")
    except subprocess.CalledProcessError:
        print(
            "  ⚠️  Code formatting issues found. Run 'black promptlifter tests' to fix."
        )
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            raise

    # Skip import sorting check for now due to isort/black conflicts
    print("  ⚠️  Skipping import sorting check (isort/black conflicts)")

    # Run linting
    print("  Running linter...")
    try:
        run_command(
            [
                sys.executable,
                "-m",
                "flake8",
                "promptlifter",
                "tests",
                "--max-line-length=88",
            ]
        )
        print("  ✅ Linting OK")
    except subprocess.CalledProcessError:
        print("  ⚠️  Linting issues found.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            raise


def main():
    """Main release process."""
    print("🚀 PromptLifter Release Process")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Are you in the project root?")
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python scripts/release.py [test|release]")
        print("  test    - Upload to TestPyPI")
        print("  release - Upload to PyPI")
        sys.exit(1)

    target = sys.argv[1].lower()

    if target not in ["test", "release"]:
        print("❌ Error: Invalid target. Use 'test' or 'release'")
        sys.exit(1)

    try:
        # Check dependencies
        check_dependencies()

        # Run quality checks
        run_quality_checks()

        # Run tests
        run_tests()

        # Clean build artifacts
        clean_build_artifacts()

        # Build package
        build_package()

        # Check package
        check_package()

        # Upload to appropriate PyPI
        if target == "test":
            upload_to_test_pypi()
            print("\n✅ Successfully uploaded to TestPyPI!")
            print("🔗 TestPyPI URL: https://test.pypi.org/project/promptlifter/")
        else:
            upload_to_pypi()
            print("\n✅ Successfully uploaded to PyPI!")
            print("🔗 PyPI URL: https://pypi.org/project/promptlifter/")

        print("\n🎉 Release completed successfully!")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Release failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Release cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
