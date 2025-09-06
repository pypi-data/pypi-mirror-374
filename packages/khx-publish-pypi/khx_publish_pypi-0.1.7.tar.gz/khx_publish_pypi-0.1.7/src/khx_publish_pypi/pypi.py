"""Production PyPI publishing functionality."""

from pathlib import Path
from typing import Optional
from rich.console import Console

from .config import get_token
from .publish import build_package, upload_package, validate_package

console = Console()


def publish_to_pypi(
    project_path: Path, skip_build: bool = False
) -> tuple[bool, Optional[str]]:
    """
    Publish package to production PyPI.

    Args:
        project_path: Path to the project root
        skip_build: Skip building if dist/ already exists

    Returns:
        Tuple of (success: bool, package_name: Optional[str])
    """
    console.print("🚀 [bold cyan]Publishing to PyPI[/bold cyan]")
    console.print(
        "⚠️ [yellow]This will upload to production PyPI. Proceed with caution![/yellow]"
    )

    # Validate package
    if not validate_package(project_path):
        return False, None

    # Build package if needed
    if not skip_build:
        if not build_package(project_path):
            return False, None

    # Get token
    try:
        token = get_token("pypi")
    except ValueError as e:
        console.print(f"❌ [red]{e}[/red]")
        return False, None

    # Upload
    repo_url = "https://upload.pypi.org/legacy/"
    success, package_name = upload_package(token, repo_url, project_path)
    if success:
        console.print("🎉 [bold green]Successfully published to PyPI![/bold green]")
        return True, package_name
    else:
        return False, None


if __name__ == "__main__":
    # Simple test
    import sys

    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1])
    else:
        project_path = Path.cwd()

    success = publish_to_pypi(project_path)
    sys.exit(0 if success else 1)
