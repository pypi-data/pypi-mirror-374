from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

from .utils import (
    read_pyproject_toml,
    find_package_folder,
    is_valid_semver,
)
from .version_detection import detect_package_version


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

    # 4) Enhanced version detection with comprehensive support for dynamic versioning
    version_ok = False
    project_name: Optional[str] = None
    version_val: Optional[str] = None
    invalid_semver = False
    name_folder_warning: Optional[str] = None
    version_detection_info: Optional[str] = None

    if pyproject_path.is_file():
        data = read_pyproject_toml(pyproject_path)
        if data is not None:
            project = data.get("project", {})
            project_name = project.get("name")

            # Use enhanced version detection
            detection_result = detect_package_version(pkg_path)

            if detection_result.version_info:
                version_val = detection_result.version_info.version
                version_ok = True

                # Create informative detail about how version was detected
                info_parts = [
                    f"v{version_val}",
                    f"({detection_result.version_info.method})",
                ]

                if detection_result.version_info.is_dynamic:
                    info_parts.append("dynamic")

                if detection_result.version_info.build_backend:
                    info_parts.append(
                        f"backend:{detection_result.version_info.build_backend}"
                    )

                version_detection_info = " ".join(info_parts)
            else:
                # Provide helpful diagnostic information
                attempted_methods = ", ".join(detection_result.attempts)
                version_detection_info = (
                    f"Failed to detect version. Tried: {attempted_methods}"
                )

                if detection_result.errors:
                    version_detection_info += (
                        f". Errors: {'; '.join(detection_result.errors[:2])}"
                    )

            # Validate semver if present
            if version_val and not is_valid_semver(version_val):
                invalid_semver = True
                version_detection_info += " (invalid semver format)"

    checks.append(CheckResult("Project name", bool(project_name), project_name))
    checks.append(
        CheckResult("Version", version_ok, version_detection_info or version_val)
    )

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
