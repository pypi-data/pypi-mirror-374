#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced version detection capabilities of khx-publish-pypi.

This script creates various test package scenarios and shows how the enhanced
version detection handles different build backends and dynamic versioning configurations.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Add the current package to the path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from khx_publish_pypi.version_detection import detect_package_version


def create_test_package(base_dir: Path, config: Dict[str, Any]) -> Path:
    """Create a test package with the given configuration."""
    package_dir = base_dir / config["name"]
    package_dir.mkdir(exist_ok=True)

    # Create pyproject.toml
    pyproject_content = config["pyproject_toml"]
    (package_dir / "pyproject.toml").write_text(pyproject_content)

    # Create package structure
    if "package_structure" in config:
        for file_path, content in config["package_structure"].items():
            full_path = package_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

    # Create basic README
    (package_dir / "README.md").write_text(
        f"# {config['name']}\n\nTest package for version detection."
    )

    return package_dir


def test_enhanced_version_detection():
    """Test the enhanced version detection with various configurations."""

    # Test configurations
    test_configs = [
        {
            "name": "static_version_test",
            "description": "Static version in pyproject.toml",
            "pyproject_toml": """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "static-version-test"
version = "1.2.3"
description = "Test package with static version"
""",
        },
        {
            "name": "setuptools_dynamic_test",
            "description": "Setuptools dynamic version with attr",
            "pyproject_toml": """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "setuptools-dynamic-test"
dynamic = ["version"]
description = "Test package with setuptools dynamic version"

[tool.setuptools.dynamic]
version = {attr = "setuptools_dynamic_test.__version__"}
""",
            "package_structure": {
                "src/setuptools_dynamic_test/__init__.py": """from .__version__ import __version__\n__all__ = ["__version__"]""",
                "src/setuptools_dynamic_test/__version__.py": """__version__ = "2.0.0\"""",
            },
        },
        {
            "name": "scikit_build_test",
            "description": "Scikit-build-core dynamic version",
            "pyproject_toml": """[build-system]
requires = ["scikit-build-core"]
build-backend = "scikit_build_core.build"

[project]
name = "scikit-build-test"
dynamic = ["version"]
description = "Test package with scikit-build-core dynamic version"

[tool.scikit-build.metadata.version]
provider = "scikit_build_core.metadata.regex"
input = "src/scikit_build_test/__version__.py"
""",
            "package_structure": {
                "src/scikit_build_test/__init__.py": """from .__version__ import __version__\n__all__ = ["__version__"]""",
                "src/scikit_build_test/__version__.py": """__version__ = "3.1.4\"""",
            },
        },
        {
            "name": "version_file_test",
            "description": "Version in standalone __version__.py",
            "pyproject_toml": """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "version-file-test"
dynamic = ["version"]
description = "Test package with version in separate file"
""",
            "package_structure": {
                "src/version_file_test/__init__.py": "# Empty init file",
                "src/version_file_test/__version__.py": """__version__ = "4.5.6\"""",
            },
        },
        {
            "name": "no_version_test",
            "description": "Package with no detectable version",
            "pyproject_toml": """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "no-version-test"
dynamic = ["version"]
description = "Test package with no detectable version"
""",
            "package_structure": {
                "src/no_version_test/__init__.py": "# No version here",
            },
        },
    ]

    print("🧪 Enhanced Version Detection Test Suite")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        for config in test_configs:
            print(f"\n📦 Testing: {config['description']}")
            print("-" * 40)

            try:
                # Create test package
                package_path = create_test_package(temp_path, config)

                # Test version detection
                result = detect_package_version(package_path)

                print(f"📍 Package: {config['name']}")
                print(f"📁 Path: {package_path}")
                print(f"🔍 Detection attempts: {', '.join(result.attempts)}")

                if result.version_info:
                    print(f"✅ Version detected: {result.version_info.version}")
                    print(f"📄 Source: {result.version_info.source}")
                    print(f"🛠️  Method: {result.version_info.method}")
                    print(f"🔄 Dynamic: {result.version_info.is_dynamic}")
                    if result.version_info.build_backend:
                        print(f"🏗️  Backend: {result.version_info.build_backend}")
                    print(f"🎯 Confidence: {result.version_info.confidence}%")
                else:
                    print("❌ No version detected")
                    if result.errors:
                        print(f"🔥 Errors: {'; '.join(result.errors)}")

                if result.warnings:
                    print(f"⚠️  Warnings: {'; '.join(result.warnings)}")

            except Exception as e:
                print(f"💥 Test failed with error: {e}")

    print("\n" + "=" * 60)
    print("🎉 Enhanced version detection test completed!")

    print("\n📋 Summary of Enhanced Capabilities:")
    print("✅ Static versions in pyproject.toml")
    print("✅ Dynamic versions with setuptools")
    print("✅ Dynamic versions with scikit-build-core")
    print("✅ Version detection from __version__.py files")
    print("✅ Fallback import-based detection")
    print("✅ Comprehensive error reporting")
    print("✅ Build backend identification")
    print("✅ Confidence scoring")


if __name__ == "__main__":
    test_enhanced_version_detection()
