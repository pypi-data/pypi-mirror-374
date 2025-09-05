#!/usr/bin/env python3
"""
PyPI Setup script for PromptLifter.

This script helps set up PyPI credentials and environment for releases.
"""

import os
import sys
from pathlib import Path


def create_pypirc_template():
    """Create a .pypirc template file."""
    pypirc_content = """[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = your-pypi-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your-testpypi-token-here
"""

    pypirc_path = Path.home() / ".pypirc"

    if pypirc_path.exists():
        print(f"⚠️  .pypirc already exists at {pypirc_path}")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != "y":
            print("Skipping .pypirc creation")
            return

    with open(pypirc_path, "w") as f:
        f.write(pypirc_content)

    print(f"✅ Created .pypirc template at {pypirc_path}")
    print(
        "📝 Please edit the file and replace the token placeholders with your actual tokens"
    )


def check_environment():
    """Check if the environment is properly set up."""
    print("🔍 Checking environment...")

    # Check Python version
    python_version = sys.version_info
    print(
        f"  Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
    )

    if python_version < (3, 8):
        print("  ❌ Python 3.8+ required")
        return False
    else:
        print("  ✅ Python version OK")

    # Check required packages
    required_packages = ["build", "twine", "setuptools", "wheel"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} installed")
        except ImportError:
            print(f"  ❌ {package} missing")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        import subprocess

        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + missing_packages, check=True
        )

    # Check project structure
    required_files = ["pyproject.toml", "README.md", "LICENSE"]
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file} found")
        else:
            print(f"  ❌ {file} missing")
            return False

    return True


def setup_github_secrets():
    """Provide instructions for setting up GitHub secrets."""
    print("\n🔐 GitHub Secrets Setup")
    print("=" * 40)
    print("To enable automated releases via GitHub Actions, add these secrets:")
    print()
    print("1. Go to your GitHub repository")
    print("2. Navigate to Settings > Secrets and variables > Actions")
    print("3. Add the following repository secrets:")
    print()
    print("   PYPI_TOKEN")
    print("   - Your PyPI API token")
    print("   - Get it from: https://pypi.org/manage/account/token/")
    print()
    print("   TEST_PYPI_TOKEN")
    print("   - Your TestPyPI API token")
    print("   - Get it from: https://test.pypi.org/manage/account/token/")
    print()
    print("   Optional secrets for testing:")
    print("   - OPENAI_API_KEY")
    print("   - ANTHROPIC_API_KEY")
    print("   - TAVILY_API_KEY")
    print("   - PINECONE_API_KEY")
    print("   - PINECONE_INDEX")


def main():
    """Main setup process."""
    print("🚀 PromptLifter PyPI Setup")
    print("=" * 40)

    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)

    print("\n✅ Environment check passed!")

    # Create .pypirc template
    create_pypirc_template()

    # Setup instructions
    setup_github_secrets()

    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Edit ~/.pypirc with your PyPI tokens")
    print("2. Test the release process:")
    print("   python scripts/release.py test")
    print("3. When ready, release to PyPI:")
    print("   python scripts/release.py release")


if __name__ == "__main__":
    main()
