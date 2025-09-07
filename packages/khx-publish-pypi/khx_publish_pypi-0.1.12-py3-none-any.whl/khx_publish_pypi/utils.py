from pathlib import Path
from typing import Optional, Dict, Any
import re


def read_pyproject_toml(pyproject_path: Path) -> Optional[Dict[str, Any]]:
    """Read pyproject.toml with tomllib (3.11+) or tomli fallback."""
    try:
        import tomllib

        with pyproject_path.open("rb") as f:
            return tomllib.load(f)
    except ModuleNotFoundError:
        import tomli

        with pyproject_path.open("rb") as f:
            return tomli.load(f)
    except Exception:
        return None


def find_package_folder(root: Path) -> Optional[Path]:
    """Detect a Python package folder (src layout or flat).

    Priority:
      1) src/<pkg>/__init__.py
      2) <pkg>/__init__.py at project root
    Returns the first match, else None.
    """
    src = root / "src"
    if src.is_dir():
        for child in src.iterdir():
            if child.is_dir() and (child / "__init__.py").is_file():
                return child

    # flat layout
    for child in root.iterdir():
        if child.is_dir() and (child / "__init__.py").is_file():
            return child

    return None


def read_version_from_python_file(file_path: Path) -> Optional[str]:
    """Extract __version__ value from a Python source file.

    Looks for a line like: __version__ = "1.2.3" (single or double quotes).
    Returns the version string if found, else None.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return None

    match = re.search(r'^__version__\s*=\s*[\'\"]([^\'\"]+)[\'\"]', content, flags=re.MULTILINE)
    return match.group(1) if match else None


def write_version_to_python_file(file_path: Path, new_version: str) -> bool:
    """Overwrite __version__ assignment in a Python file with new_version.

    Returns True on success, False otherwise.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return False

    new_content, count = re.subn(
        r'(^__version__\s*=\s*[\'\"][^\'\"]+[\'\"])',
        f'__version__ = "{new_version}"',
        content,
        flags=re.MULTILINE,
    )
    if count == 0:
        # If no existing assignment, append it
        new_content = content.rstrip() + f"\n__version__ = \"{new_version}\"\n"

    try:
        file_path.write_text(new_content, encoding="utf-8")
        return True
    except Exception:
        return False


def is_valid_semver(version: str) -> bool:
    """Validate SemVer 2.0.0 format.

    Accepts pre-release and build metadata.
    """
    semver_pattern = re.compile(
        r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
        r'(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?'
        r'(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    )
    return bool(semver_pattern.match(version))


def bump_version(version: str, part: str) -> Optional[str]:
    """Return a new version bumped at part: 'patch' | 'minor' | 'major'."""
    if not is_valid_semver(version):
        return None
    core = version.split("-")[0].split("+")[0]
    try:
        major_s, minor_s, patch_s = core.split(".")
        major, minor, patch = int(major_s), int(minor_s), int(patch_s)
    except Exception:
        return None

    if part == "patch":
        patch += 1
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        return None

    return f"{major}.{minor}.{patch}"

