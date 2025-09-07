"""Enhanced version detection system for Python packages.

This module provides comprehensive version detection capabilities that handle
various build backends and dynamic versioning configurations, including:
- Static versions in pyproject.toml
- Dynamic versions with setuptools
- Dynamic versions with scikit-build-core
- Dynamic versions with setuptools-scm
- Various __version__.py file locations and formats
- Proper fallback mechanisms
"""

import re
import sys
import ast
import importlib
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass

from .utils import read_pyproject_toml, read_version_from_python_file


@dataclass
class VersionInfo:
    """Information about a detected version."""

    version: str
    source: str  # Where the version was found
    method: str  # How it was detected
    is_dynamic: bool = False
    build_backend: Optional[str] = None
    confidence: int = 100  # Confidence level (0-100)


@dataclass
class VersionDetectionResult:
    """Result of version detection process."""

    version_info: Optional[VersionInfo]
    attempts: List[str]  # List of detection methods attempted
    errors: List[str]  # List of errors encountered
    warnings: List[str]  # List of warnings


class EnhancedVersionDetector:
    """Enhanced version detector with support for multiple build backends."""

    def __init__(self, package_path: Path):
        self.package_path = package_path
        self.pyproject_path = package_path / "pyproject.toml"
        self.pyproject_data: Optional[Dict[str, Any]] = None

        # Load pyproject.toml if it exists
        if self.pyproject_path.is_file():
            self.pyproject_data = read_pyproject_toml(self.pyproject_path)

    def detect_version(self) -> VersionDetectionResult:
        """Detect version using all available methods."""
        attempts = []
        errors = []
        warnings = []

        # Method 1: Check for static version in pyproject.toml
        attempts.append("static_pyproject_version")
        if version_info := self._get_static_version():
            return VersionDetectionResult(version_info, attempts, errors, warnings)

        # Method 2: Check for dynamic version configuration
        attempts.append("dynamic_pyproject_version")
        if version_info := self._get_dynamic_version():
            return VersionDetectionResult(version_info, attempts, errors, warnings)

        # Method 3: Try importing the package directly
        attempts.append("import_package_version")
        try:
            if version_info := self._try_import_version():
                return VersionDetectionResult(version_info, attempts, errors, warnings)
        except Exception as e:
            errors.append(f"Import failed: {e}")

        # Method 4: Parse __version__.py files directly
        attempts.append("parse_version_files")
        if version_info := self._parse_version_files():
            return VersionDetectionResult(version_info, attempts, errors, warnings)

        # Method 5: Fallback to setuptools-scm if configured
        attempts.append("setuptools_scm_fallback")
        if version_info := self._try_setuptools_scm():
            return VersionDetectionResult(version_info, attempts, errors, warnings)

        return VersionDetectionResult(None, attempts, errors, warnings)

    def _get_static_version(self) -> Optional[VersionInfo]:
        """Get static version from pyproject.toml."""
        if not self.pyproject_data:
            return None

        project = self.pyproject_data.get("project", {})
        version = project.get("version")

        if version and isinstance(version, str):
            return VersionInfo(
                version=version,
                source="pyproject.toml",
                method="static",
                is_dynamic=False,
                confidence=100,
            )

        return None

    def _get_dynamic_version(self) -> Optional[VersionInfo]:
        """Get dynamic version from various build backend configurations."""
        if not self.pyproject_data:
            return None

        project = self.pyproject_data.get("project", {})
        dynamic = project.get("dynamic", [])

        if not isinstance(dynamic, list) or "version" not in dynamic:
            return None

        # Check different build backends
        tool = self.pyproject_data.get("tool", {})

        # 1. setuptools dynamic version
        if setuptools_version := self._get_setuptools_dynamic_version(tool):
            return setuptools_version

        # 2. scikit-build-core dynamic version
        if scikit_version := self._get_scikit_build_dynamic_version(tool):
            return scikit_version

        # 3. setuptools-scm dynamic version
        if scm_version := self._get_setuptools_scm_dynamic_version(tool):
            return scm_version

        # 4. flit dynamic version
        if flit_version := self._get_flit_dynamic_version(tool):
            return flit_version

        # 5. hatchling dynamic version
        if hatch_version := self._get_hatchling_dynamic_version(tool):
            return hatch_version

        return None

    def _get_setuptools_dynamic_version(
        self, tool: Dict[str, Any]
    ) -> Optional[VersionInfo]:
        """Get version from setuptools dynamic configuration."""
        setuptools_cfg = tool.get("setuptools", {})
        if not isinstance(setuptools_cfg, dict):
            return None

        dynamic_cfg = setuptools_cfg.get("dynamic", {})
        if not isinstance(dynamic_cfg, dict):
            return None

        version_cfg = dynamic_cfg.get("version")
        if not isinstance(version_cfg, dict):
            return None

        # Handle file-based version
        version_file = version_cfg.get("file")
        if isinstance(version_file, str):
            candidate = self.package_path / version_file
            if version := read_version_from_python_file(candidate):
                return VersionInfo(
                    version=version,
                    source=str(candidate),
                    method="setuptools_dynamic_file",
                    is_dynamic=True,
                    build_backend="setuptools",
                    confidence=95,
                )

        # Handle attribute-based version
        version_attr = version_cfg.get("attr")
        if isinstance(version_attr, str):
            if version := self._resolve_attribute_version(version_attr):
                return VersionInfo(
                    version=version,
                    source=f"attribute:{version_attr}",
                    method="setuptools_dynamic_attr",
                    is_dynamic=True,
                    build_backend="setuptools",
                    confidence=90,
                )

        return None

    def _get_scikit_build_dynamic_version(
        self, tool: Dict[str, Any]
    ) -> Optional[VersionInfo]:
        """Get version from scikit-build-core configuration."""
        scikit_cfg = tool.get("scikit-build", {})
        if not isinstance(scikit_cfg, dict):
            return None

        metadata_cfg = scikit_cfg.get("metadata", {})
        if not isinstance(metadata_cfg, dict):
            return None

        version_cfg = metadata_cfg.get("version")
        if not isinstance(version_cfg, dict):
            return None

        provider = version_cfg.get("provider")
        if provider == "scikit_build_core.metadata.regex":
            input_file = version_cfg.get("input")
            if isinstance(input_file, str):
                candidate = self.package_path / input_file
                if version := read_version_from_python_file(candidate):
                    return VersionInfo(
                        version=version,
                        source=str(candidate),
                        method="scikit_build_regex",
                        is_dynamic=True,
                        build_backend="scikit-build-core",
                        confidence=95,
                    )

        return None

    def _get_setuptools_scm_dynamic_version(
        self, tool: Dict[str, Any]
    ) -> Optional[VersionInfo]:
        """Get version from setuptools-scm configuration."""
        scm_cfg = tool.get("setuptools_scm", {})
        if scm_cfg or "setuptools_scm" in tool:
            # Try to get version from setuptools-scm
            try:
                from setuptools_scm import get_version

                version = get_version(root=str(self.package_path))
                if version:
                    return VersionInfo(
                        version=version,
                        source="setuptools-scm",
                        method="setuptools_scm",
                        is_dynamic=True,
                        build_backend="setuptools-scm",
                        confidence=90,
                    )
            except ImportError:
                pass
            except Exception:
                pass

        return None

    def _get_flit_dynamic_version(self, tool: Dict[str, Any]) -> Optional[VersionInfo]:
        """Get version from flit configuration."""
        flit_cfg = tool.get("flit", {})
        if not isinstance(flit_cfg, dict):
            return None

        module_cfg = flit_cfg.get("module", {})
        if isinstance(module_cfg, dict):
            name = module_cfg.get("name")
            if name:
                # Try to import the module and get __version__
                if version := self._try_import_module_version(name):
                    return VersionInfo(
                        version=version,
                        source=f"module:{name}",
                        method="flit_module",
                        is_dynamic=True,
                        build_backend="flit",
                        confidence=85,
                    )

        return None

    def _get_hatchling_dynamic_version(
        self, tool: Dict[str, Any]
    ) -> Optional[VersionInfo]:
        """Get version from hatchling configuration."""
        hatch_cfg = tool.get("hatch", {})
        if not isinstance(hatch_cfg, dict):
            return None

        version_cfg = hatch_cfg.get("version", {})
        if isinstance(version_cfg, dict):
            source = version_cfg.get("source")
            if source == "regex":
                path = version_cfg.get("path")
                if path:
                    candidate = self.package_path / path
                    if version := read_version_from_python_file(candidate):
                        return VersionInfo(
                            version=version,
                            source=str(candidate),
                            method="hatchling_regex",
                            is_dynamic=True,
                            build_backend="hatchling",
                            confidence=90,
                        )

        return None

    def _resolve_attribute_version(self, attr_path: str) -> Optional[str]:
        """Resolve version from attribute path like 'package.__version__.__version__'."""
        # Handle formats like: package.__version:__version__ or package:__version__
        attr_path = attr_path.replace(":", ".")
        module_path, _, var_name = attr_path.rpartition(".")

        if not module_path:
            return None

        # Try different file locations
        root = self.package_path
        src_root = root / "src"
        module_rel = Path(*module_path.split("."))

        # 1) Try module file: src/<module>.py
        candidate = src_root / module_rel.with_suffix(".py")
        if version := read_version_from_python_file(candidate):
            return version

        # 2) Try package __init__: src/<module>/__init__.py
        candidate = src_root / module_rel / "__init__.py"
        if version := read_version_from_python_file(candidate):
            return version

        # 3) Try sibling __version__.py inside package
        candidate = src_root / module_rel / "__version__.py"
        if version := read_version_from_python_file(candidate):
            return version

        # 4) Try root level module file
        candidate = root / module_rel.with_suffix(".py")
        if version := read_version_from_python_file(candidate):
            return version

        # 5) Try root level package
        candidate = root / module_rel / "__init__.py"
        if version := read_version_from_python_file(candidate):
            return version

        # 6) Try root level __version__.py
        candidate = root / module_rel / "__version__.py"
        if version := read_version_from_python_file(candidate):
            return version

        # 7) Fallback: try importing
        try:
            # Add package path to sys.path temporarily
            sys.path.insert(0, str(src_root))
            try:
                mod = importlib.import_module(module_path)
                value = getattr(mod, var_name, None)
                if isinstance(value, str):
                    return value
            finally:
                sys.path.pop(0)
        except Exception:
            pass

        return None

    def _try_import_version(self) -> Optional[VersionInfo]:
        """Try to import the package and get its __version__."""
        if not self.pyproject_data:
            return None

        project = self.pyproject_data.get("project", {})
        package_name = project.get("name")

        if not package_name:
            return None

        # Try importing the package
        try:
            # Add src directory to path if it exists
            src_path = self.package_path / "src"
            if src_path.exists():
                sys.path.insert(0, str(src_path))

            try:
                # Convert package name to module name (replace - with _)
                module_name = package_name.replace("-", "_")
                mod = importlib.import_module(module_name)
                version = getattr(mod, "__version__", None)

                if isinstance(version, str):
                    return VersionInfo(
                        version=version,
                        source=f"import:{module_name}",
                        method="import_package",
                        is_dynamic=False,
                        confidence=85,
                    )
            finally:
                if src_path.exists() and str(src_path) in sys.path:
                    sys.path.remove(str(src_path))

        except Exception:
            pass

        return None

    def _try_import_module_version(self, module_name: str) -> Optional[str]:
        """Try to import a specific module and get its __version__."""
        try:
            # Add src directory to path if it exists
            src_path = self.package_path / "src"
            if src_path.exists():
                sys.path.insert(0, str(src_path))

            try:
                mod = importlib.import_module(module_name)
                return getattr(mod, "__version__", None)
            finally:
                if src_path.exists() and str(src_path) in sys.path:
                    sys.path.remove(str(src_path))

        except Exception:
            pass

        return None

    def _parse_version_files(self) -> Optional[VersionInfo]:
        """Parse __version__.py files directly in common locations."""
        # Common version file patterns
        patterns = [
            "src/*/__version__.py",
            "src/*/version.py",
            "*/__version__.py",
            "*/version.py",
            "__version__.py",
            "version.py",
        ]

        for pattern in patterns:
            for version_file in self.package_path.glob(pattern):
                if version := read_version_from_python_file(version_file):
                    return VersionInfo(
                        version=version,
                        source=str(version_file),
                        method="parse_version_file",
                        is_dynamic=False,
                        confidence=80,
                    )

        return None

    def _try_setuptools_scm(self) -> Optional[VersionInfo]:
        """Try setuptools-scm as a fallback."""
        try:
            from setuptools_scm import get_version

            version = get_version(root=str(self.package_path))
            if version:
                return VersionInfo(
                    version=version,
                    source="setuptools-scm-fallback",
                    method="setuptools_scm_fallback",
                    is_dynamic=True,
                    build_backend="setuptools-scm",
                    confidence=70,
                )
        except ImportError:
            pass
        except Exception:
            pass

        return None


def detect_package_version(package_path: Path) -> VersionDetectionResult:
    """Detect version for a package using enhanced detection methods.

    Args:
        package_path: Path to the package directory

    Returns:
        VersionDetectionResult with version info and diagnostic data
    """
    detector = EnhancedVersionDetector(package_path)
    return detector.detect_version()


def get_package_version(package_path: Path) -> Optional[str]:
    """Get package version using enhanced detection (legacy interface).

    Args:
        package_path: Path to the package directory

    Returns:
        Version string if found, None otherwise
    """
    result = detect_package_version(package_path)
    return result.version_info.version if result.version_info else None
