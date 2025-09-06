from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

from .utils import (
    read_pyproject_toml,
    find_package_folder,
    read_version_from_python_file,
    is_valid_semver,
)


@dataclass
class CheckResult:
    label: str
    ok: bool
    detail: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {"label": self.label, "ok": self.ok, "detail": self.detail}


def run_prechecks(pkg_path: Path) -> Dict[str, Any]:
    """Run minimal pre-checks on a package path.

    Returns a dict with granular check results and a summary.
    """
    checks: list[CheckResult] = []

    # 1) Path exists
    path_ok = pkg_path.exists()
    checks.append(CheckResult("Package path", path_ok, str(pkg_path)))

    pyproject_path = pkg_path / "pyproject.toml"
    readme_path = pkg_path / "README.md"
    license_path = pkg_path / "LICENSE"

    # 2) Files existence / content
    checks.append(CheckResult("pyproject.toml", pyproject_path.is_file()))
    checks.append(CheckResult("README.md", readme_path.is_file()))
    # LICENSE is recommended, not required → must be non-empty to be OK
    license_ok = license_path.is_file() and license_path.stat().st_size > 0
    checks.append(CheckResult("LICENSE (recommended)", license_ok))

    # 3) Package folder detection (either src layout or flat package)
    pkg_folder = find_package_folder(pkg_path)
    checks.append(
        CheckResult(
            "Package folder",
            pkg_folder is not None,
            str(pkg_folder) if pkg_folder else None,
        )
    )

    # 4) Parse pyproject -> minimal metadata (supports static or dynamic version)
    version_ok = False
    project_name: Optional[str] = None
    version_val: Optional[str] = None
    invalid_semver = False
    name_folder_warning: Optional[str] = None
    if pyproject_path.is_file():
        data = read_pyproject_toml(pyproject_path)
        if data is not None:
            project = data.get("project", {})
            project_name = project.get("name")
            version_val = project.get("version")

            # If version is declared dynamic, attempt to resolve from tool.setuptools.dynamic
            if (
                not version_val
                and isinstance(project.get("dynamic"), list)
                and "version" in project.get("dynamic", [])
            ):
                tool = data.get("tool", {}) or {}
                setuptools_cfg = (
                    tool.get("setuptools", {}) if isinstance(tool, dict) else {}
                )
                dynamic_cfg = (
                    setuptools_cfg.get("dynamic", {})
                    if isinstance(setuptools_cfg, dict)
                    else {}
                )
                version_cfg = (
                    dynamic_cfg.get("version")
                    if isinstance(dynamic_cfg, dict)
                    else None
                )

                if isinstance(version_cfg, dict):
                    version_file = version_cfg.get("file")
                    version_attr = version_cfg.get("attr")
                    if isinstance(version_file, str):
                        candidate = pyproject_path.parent / version_file
                        version_val = read_version_from_python_file(candidate)
                    elif isinstance(version_attr, str):
                        # Handle formats like: khx_publish_pypi.__version:__version__ or khx_publish_pypi:__version__
                        attr_path = version_attr.replace(":", ".")
                        module_path, _, _var = attr_path.rpartition(".")
                        if module_path:
                            root = pyproject_path.parent
                            src_root = root / "src"
                            module_rel = Path(*module_path.split("."))

                            # 1) Try module file: src/<module>.py
                            candidate = src_root / module_rel.with_suffix(".py")
                            version_val = read_version_from_python_file(candidate)

                            # 2) Try package __init__: src/<module>/__init__.py
                            if not version_val:
                                candidate = src_root / module_rel / "__init__.py"
                                version_val = read_version_from_python_file(candidate)

                            # 3) Try sibling __version__.py inside package
                            if not version_val:
                                candidate = src_root / module_rel / "__version__.py"
                                version_val = read_version_from_python_file(candidate)

                            # 4) Fallback: import module and get attribute
                            if not version_val:
                                try:
                                    import importlib

                                    mod = importlib.import_module(module_path)
                                    value = getattr(mod, _var, None)
                                    if isinstance(value, str):
                                        version_val = value
                                except Exception:
                                    version_val = None
                            if not version_val:
                                # Fallback: import module and read attribute
                                try:
                                    import importlib

                                    mod = importlib.import_module(module_path)
                                    version_val = getattr(mod, _var, None)
                                except Exception:
                                    version_val = None

            # Validate semver if present
            if version_val and not is_valid_semver(version_val):
                invalid_semver = True
            version_ok = bool(version_val)

    checks.append(CheckResult("Project name", bool(project_name), project_name))
    checks.append(CheckResult("Version", version_ok, version_val))

    # 5) Name vs folder check (warning represented in detail if mismatch)
    if project_name and pkg_folder is not None:
        expected = pkg_folder.name.replace("-", "_")
        if project_name.replace("-", "_") != expected:
            name_folder_warning = f"project '{project_name}' vs folder '{expected}'"

    # Derive summary flags
    required_ok = all(
        c.ok
        for c in checks
        if c.label
        in {
            "Package path",
            "pyproject.toml",
            "README.md",
            "Package folder",
            "Project name",
            "Version",
        }
    )

    summary = {
        "ready": required_ok,
        "package_name": project_name,
        "version": version_val,
        "package_folder": str(pkg_folder) if pkg_folder else None,
        "invalid_semver": invalid_semver,
        "name_folder_warning": name_folder_warning,
    }

    return {
        "checks": [c.as_dict() for c in checks],
        "summary": summary,
        "root": str(pkg_path),
    }
