"""Core publishing functionality for PyPI uploads."""

import subprocess
import sys
from pathlib import Path
from typing import Optional
import logging
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)


def build_package(project_path: Path) -> bool:
    """
    Build the Python package using python -m build.

    Args:
        project_path: Path to the project root

    Returns:
        True if build successful, False otherwise
    """
    console.print("🏗️ [yellow]Building package...[/yellow]")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "build"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            check=True,
        )
        console.print("✅ [green]Package built successfully[/green]")
        logger.info("Package built: %s", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"❌ [red]Build failed: {e.stderr}[/red]")
        logger.error("Build failed: %s", e.stderr)
        return False


def upload_package(
    token: str, repo_url: str, project_path: Path
) -> tuple[bool, Optional[str]]:
    """
    Upload package to PyPI using twine.

    Args:
        token: API token for authentication
        repo_url: Repository URL (Test PyPI or PyPI)
        project_path: Path to the project root

    Returns:
        Tuple of (success: bool, package_name: Optional[str])
    """
    dist_dir = project_path / "dist"
    if not dist_dir.exists():
        console.print("❌ [red]dist/ directory not found. Run build first.[/red]")
        return False, None

    # Find the package file (wheel or tar.gz)
    package_files = list(dist_dir.glob("*.whl")) + list(dist_dir.glob("*.tar.gz"))
    if not package_files:
        console.print("❌ [red]No package files found in dist/ directory.[/red]")
        return False, None

    # Extract package name and version from filename
    package_file = package_files[0]
    package_name = package_file.stem
    if package_file.suffix == ".whl":
        # For wheels: package_name-version-... .whl
        package_name = package_name.split("-")[0]
    else:
        # For tar.gz: package_name-version.tar.gz
        package_name = package_name.split("-")[0]

    console.print(f"📤 [yellow]Uploading {package_name} to {repo_url}...[/yellow]")
    try:
        # Use twine upload with token
        cmd = [
            sys.executable,
            "-m",
            "twine",
            "upload",
            "--repository-url",
            repo_url,
            "--username",
            "__token__",
            "--password",
            token,
            str(dist_dir / "*"),
        ]

        result = subprocess.run(
            cmd, cwd=str(project_path), capture_output=True, text=True, check=True
        )
        console.print("✅ [green]Package uploaded successfully[/green]")
        logger.info("Upload successful: %s", result.stdout)
        return True, package_name
    except subprocess.CalledProcessError as e:
        # Analyze the error and provide helpful suggestions
        repo_name = "Test PyPI" if "test.pypi.org" in repo_url else "PyPI"

        # Combine stdout and stderr for analysis
        full_error = (e.stdout + " " + e.stderr).strip()
        if not full_error:
            full_error = "Upload failed (no error details available)"

        error_explanation, suggestions = analyze_upload_error(full_error, repo_name)

        console.print(f"❌ [red]{error_explanation}[/red]")

        if e.stderr.strip():
            console.print(f"   [dim]Error details: {e.stderr.strip()}[/dim]")
        elif e.stdout.strip():
            console.print(f"   [dim]Output details: {e.stdout.strip()}[/dim]")

        console.print("\n💡 [yellow]Suggested solutions:[/yellow]")
        for i, suggestion in enumerate(suggestions, 1):
            console.print(f"   {i}. {suggestion}")

        logger.error("Upload failed: stdout=%s, stderr=%s", e.stdout, e.stderr)
        return False, None


def analyze_upload_error(error_output: str, repo_name: str) -> tuple[str, list[str]]:
    """
    Analyze upload error and provide helpful suggestions.

    Args:
        error_output: The error output from twine
        repo_name: Name of the repository (Test PyPI or PyPI)

    Returns:
        Tuple of (error_explanation, list_of_suggestions)
    """
    error_output = error_output.lower()

    # Common error patterns and solutions
    if (
        "file already exists" in error_output
        or "already exists" in error_output
        or "400" in error_output
        or "bad request" in error_output
    ):
        return (
            f"Package version already exists on {repo_name}",
            [
                "Increment version: khx-publish-pypi bump patch",
                "Check current version: khx-publish-pypi check",
                "Rebuild package: python -m build",
                "Upload with new version: khx-publish-pypi publish-test (or publish-prod)",
            ],
        )
    elif (
        "invalid token" in error_output
        or "unauthorized" in error_output
        or "403" in error_output
        or "forbidden" in error_output
        or "404" in error_output
        or "not found" in error_output
    ):
        return (
            f"Authentication failed for {repo_name} (invalid token or permissions)",
            [
                "Check your API token: khx-publish-pypi setup-tokens",
                "Verify token permissions on PyPI/Test PyPI",
                "Reconfigure tokens: khx-publish-pypi setup-tokens",
                "Ensure you're using the correct token for the target repository",
            ],
        )
    elif (
        "network" in error_output
        or "connection" in error_output
        or "timeout" in error_output
    ):
        return (
            f"Network connection issue with {repo_name}",
            [
                "Check internet connection",
                "Try again in a few minutes",
                "Verify repository URL is accessible",
            ],
        )
    elif (
        "invalid distribution" in error_output
        or "invalid package" in error_output
        or "invalid wheel" in error_output
    ):
        return (
            f"Package distribution files are invalid",
            [
                "Rebuild package: python -m build",
                "Check package structure: khx-publish-pypi check",
                "Verify pyproject.toml configuration",
            ],
        )
    else:
        # If no specific pattern matches, check if it's likely a version conflict
        # by looking for common indicators
        if "upload" in error_output and (
            "failed" in error_output or "error" in error_output
        ):
            return (
                f"Upload failed to {repo_name} (likely version conflict)",
                [
                    "Increment version: khx-publish-pypi bump patch",
                    "Check current version: khx-publish-pypi check",
                    "Rebuild package: python -m build",
                    "Upload with new version: khx-publish-pypi publish-test (or publish-prod)",
                    "Check repository status and try again",
                ],
            )
        else:
            return (
                f"Upload failed to {repo_name}",
                [
                    "Check error details above",
                    "Verify package files in dist/ directory",
                    "Try rebuilding: python -m build",
                    "Check repository status",
                ],
            )


def validate_package(project_path: Path) -> bool:
    """
    Validate package before upload.

    Args:
        project_path: Path to the project root

    Returns:
        True if validation passes, False otherwise
    """
    from .checks import run_prechecks

    console.print("🔍 [yellow]Validating package...[/yellow]")
    results = run_prechecks(project_path)

    if not results["summary"]["ready"]:
        console.print("❌ [red]Validation failed. Fix issues before publishing.[/red]")
        return False

    console.print("✅ [green]Package validation passed[/green]")
    return True


if __name__ == "__main__":
    # Simple test
    import tempfile

    test_path = Path(tempfile.mkdtemp())
    print(f"Testing build in {test_path}")
    # This would need a real package to test fully
