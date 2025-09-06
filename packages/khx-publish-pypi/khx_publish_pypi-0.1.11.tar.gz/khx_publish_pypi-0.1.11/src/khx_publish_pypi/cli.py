from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
import time

from .checks import run_prechecks
from .report import print_banner, print_report
from .__version__ import __version__
from .utils import (
    read_pyproject_toml,
    read_version_from_python_file,
    write_version_to_python_file,
    bump_version,
)
from .config import setup_tokens as config_setup_tokens
from .test_pypi import publish_to_testpypi
from .pypi import publish_to_pypi
import subprocess
import shutil

console = Console()


def _update_tokens_non_interactive(
    test_token: str | None, prod_token: str | None
) -> None:
    """Update API tokens non-interactively."""
    import os
    import keyring

    username = os.getenv("USER") or os.getenv("USERNAME") or "default"
    service_name_test = "khx-publish-testpypi"
    service_name_prod = "khx-publish-pypi"

    updated = False

    if test_token:
        # For PyPI API tokens, username must always be __token__
        keyring.set_password(service_name_test, "__token__", test_token)
        console.print("✅ [green]Test PyPI token updated securely[/green]")
        updated = True

    if prod_token:
        # For PyPI API tokens, username must always be __token__
        keyring.set_password(service_name_prod, "__token__", prod_token)
        console.print("✅ [green]PyPI token updated securely[/green]")
        updated = True

    if not updated:
        console.print("ℹ️ [blue]No tokens provided to update[/blue]")
    else:
        console.print("\n🎉 [bold green]Token update complete![/bold green]")


def display_package_urls(package_name: str, published_to: list[str]) -> None:
    """
    Display package URLs in a nice banner format.

    Args:
        package_name: Name of the published package
        published_to: List of repositories where package was published
    """
    if not published_to:
        return

    console.print("\n" + "═" * 80, style="bold cyan", justify="center")
    console.print(
        "📦 [bold white]PACKAGE SUCCESSFULLY PUBLISHED![/bold white] 📦",
        justify="center",
    )
    console.print("═" * 80, style="bold cyan", justify="center")

    for repo in published_to:
        if repo == "testpypi":
            url = f"https://test.pypi.org/project/{package_name}/"
            console.print(
                f"🧪 [bold cyan]Test PyPI:[/bold cyan] {url}", justify="center"
            )
        elif repo == "pypi":
            url = f"https://pypi.org/project/{package_name}/"
            console.print(f"🚀 [bold green]PyPI:[/bold green] {url}", justify="center")

    console.print("═" * 80, style="bold cyan", justify="center")
    console.print("🎉 [bold yellow]Happy coding![/bold yellow]", justify="center")
    console.print("═" * 80, style="bold cyan", justify="center")


def show_version(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    """🎨 Display version with colorful, cool formatting"""
    if value:
        width = 50
        console.print()

        # Top border
        console.print("╔" + "═" * width + "╗", style="bold cyan")

        # Empty line
        console.print("║" + " " * width + "║", style="bold cyan")

        # Title
        title = "🚀 KHX-PUBLISH-PYPI 🚀"
        title_padding = (width - len(title)) // 2
        console.print(
            "[bold cyan]║[/bold cyan]"
            + " " * title_padding
            + title
            + " " * (width - len(title) - title_padding - 2)
            + "[bold cyan]║[/bold cyan]",
            style="bold yellow",
        )

        # Empty line
        console.print("║" + " " * width + "║", style="bold cyan")

        # Version
        version_text = f"Version {__version__}"
        version_padding = (width - len(version_text)) // 2
        console.print(
            "║"
            + " " * version_padding
            + version_text
            + " " * (width - len(version_text) - version_padding)
            + "║",
            style="bold cyan",
        )

        # Empty line
        console.print("║" + " " * width + "║", style="bold cyan")

        # Description
        desc = "✨ Interactive Python Publisher ✨"
        desc_padding = (width - len(desc)) // 2
        console.print(
            "[bold cyan]║[/bold cyan]"
            + " " * desc_padding
            + desc
            + " " * (width - len(desc) - desc_padding - 2)
            + "[bold cyan]║[/bold cyan]",
            style="bold green",
        )

        # Empty line
        console.print("║" + " " * width + "║", style="bold cyan")

        # Bottom border
        console.print("╚" + "═" * width + "╝", style="bold cyan")

        console.print()
        ctx.exit()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--version", is_flag=True, callback=show_version, expose_value=False, is_eager=True
)
def main() -> None:
    """🚀 Entry point for khx-publish-pypi - Interactive Python package publisher! 💫"""
    pass


@main.command()
@click.option(
    "--test-token",
    help="Set Test PyPI API token directly (non-interactive)",
)
@click.option(
    "--prod-token",
    help="Set PyPI API token directly (non-interactive)",
)
def setup_tokens(test_token: str | None, prod_token: str | None) -> None:
    """🔐 Setup or update Test PyPI and PyPI API tokens with secure storage.

    Run without options for interactive setup, or use --test-token/--prod-token
    for direct, non-interactive updates.
    """
    print_banner()

    if test_token or prod_token:
        # Non-interactive mode
        _update_tokens_non_interactive(test_token, prod_token)
    else:
        # Interactive mode
        config_setup_tokens()


def _update_tokens_interactive() -> None:
    """Interactively update API tokens."""
    import os
    import keyring

    # For PyPI API tokens, username must always be __token__
    username = "__token__"
    service_name_test = "khx-publish-testpypi"
    service_name_prod = "khx-publish-pypi"

    console.print("🔄 [bold cyan]Update API tokens[/bold cyan]")
    console.print("Update your existing Test PyPI and PyPI API tokens.\n")

    # Check existing tokens
    test_token_exists = keyring.get_password(service_name_test, username) is not None
    prod_token_exists = keyring.get_password(service_name_prod, username) is not None

    if not test_token_exists and not prod_token_exists:
        console.print("❌ [red]No existing tokens found![/red]")
        console.print(
            "💡 [yellow]Use 'khx-publish-pypi setup-tokens' to set up tokens first[/yellow]"
        )
        return

    console.print("ℹ️ [blue]Current token status:[/blue]")
    if test_token_exists:
        console.print("  ✅ Test PyPI token is configured")
    else:
        console.print("  ❌ Test PyPI token not configured")
    if prod_token_exists:
        console.print("  ✅ PyPI token is configured")
    else:
        console.print("  ❌ PyPI token not configured")
    console.print()

    updated = False

    # Update Test PyPI token
    if test_token_exists:
        update_test = Confirm.ask(
            "Do you want to update the Test PyPI token?", default=False
        )
        if update_test:
            test_token = console.input("Enter new Test PyPI API token: ").strip()
            if test_token:
                keyring.set_password(service_name_test, "__token__", test_token)
                console.print("✅ [green]Test PyPI token updated securely[/green]")
                updated = True
            else:
                console.print(
                    "⏭️ [yellow]Test PyPI token not updated (empty input)[/yellow]"
                )

    # Update PyPI token
    if prod_token_exists:
        update_prod = Confirm.ask(
            "Do you want to update the PyPI token?", default=False
        )
        if update_prod:
            prod_token = console.input("Enter new PyPI API token: ").strip()
            if prod_token:
                keyring.set_password(service_name_prod, "__token__", prod_token)
                console.print("✅ [green]PyPI token updated securely[/green]")
                updated = True
            else:
                console.print("⏭️ [yellow]PyPI token not updated (empty input)[/yellow]")

    if updated:
        console.print("\n🎉 [bold green]Token update complete![/bold green]")
    else:
        console.print("\nℹ️ [blue]No tokens were updated[/blue]")


@main.command()
def update_tokens() -> None:
    """🔄 Interactively update existing Test PyPI and PyPI API tokens."""
    print_banner()
    _update_tokens_interactive()


@main.command()
@click.option(
    "--path",
    "project_path",
    type=click.Path(path_type=Path),
    default=Path.cwd(),
    help="Project root containing pyproject.toml",
)
@click.option(
    "--skip-build", is_flag=True, help="Skip building if dist/ already exists"
)
def publish_test(project_path: Path, skip_build: bool) -> None:
    """🧪 Publish package to Test PyPI."""
    print_banner()
    success, package_name = publish_to_testpypi(project_path, skip_build)
    if success and package_name:
        display_package_urls(package_name, ["testpypi"])
    if not success:
        exit(1)


@main.command()
@click.option(
    "--path",
    "project_path",
    type=click.Path(path_type=Path),
    default=Path.cwd(),
    help="Project root containing pyproject.toml",
)
@click.option(
    "--skip-build", is_flag=True, help="Skip building if dist/ already exists"
)
def publish_prod(project_path: Path, skip_build: bool) -> None:
    """🚀 Publish package to production PyPI."""
    print_banner()
    success, package_name = publish_to_pypi(project_path, skip_build)
    if success and package_name:
        display_package_urls(package_name, ["pypi"])
    if not success:
        exit(1)


@main.command()
def check() -> None:
    """🔍 Run interactive pre-publish checks."""
    print_banner()

    # Interactive path prompt with validation
    while True:
        package_path_str = Prompt.ask(
            "\n📦 [bold cyan]Please enter the path to your Python package[/bold cyan]",
            default=".",
        )

        package_path = Path(package_path_str).resolve()

        if not package_path.exists():
            console.print(f"❌ [red]Path does not exist: {package_path}[/red]")
            continue

        if not package_path.is_dir():
            console.print(f"❌ [red]Path is not a directory: {package_path}[/red]")
            continue

        break

    console.print("\n🔍 [yellow]Running checks... please wait[/yellow]")

    # Create progress bar for checks
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:

        # Add tasks for each check step
        task1 = progress.add_task("📂 Checking package structure...", total=100)
        time.sleep(0.3)
        progress.update(task1, advance=25)

        task2 = progress.add_task("📄 Validating configuration files...", total=100)
        time.sleep(0.3)
        progress.update(task1, advance=25)
        progress.update(task2, advance=50)

        task3 = progress.add_task("📦 Analyzing package metadata...", total=100)
        time.sleep(0.3)
        progress.update(task1, advance=25)
        progress.update(task2, advance=50)
        progress.update(task3, advance=75)

        # Actually run the checks
        results = run_prechecks(package_path)

        # Complete all tasks
        progress.update(task1, completed=100)
        progress.update(task2, completed=100)
        progress.update(task3, completed=100)

        time.sleep(0.2)  # Brief pause to show completion

    console.print("━" * 50, style="cyan")
    print_report(results)


@main.command()
@click.argument("part", type=click.Choice(["patch", "minor", "major"]))
@click.option(
    "--path",
    "project_path",
    type=click.Path(path_type=Path),
    default=Path.cwd(),
    help="Project root containing pyproject.toml",
)
def bump(part: str, project_path: Path) -> None:
    """🔢 Bump the version in __version__.py (patch/minor/major)."""
    pyproject_path = project_path / "pyproject.toml"
    data = read_pyproject_toml(pyproject_path)
    if not data:
        console.print("❌ [red]pyproject.toml not found or invalid[/red]")
        return

    # Resolve version file from tool.setuptools.dynamic
    tool = data.get("tool", {}) or {}
    setuptools_cfg = tool.get("setuptools", {}) if isinstance(tool, dict) else {}
    dynamic_cfg = (
        setuptools_cfg.get("dynamic", {}) if isinstance(setuptools_cfg, dict) else {}
    )
    version_cfg = dynamic_cfg.get("version") if isinstance(dynamic_cfg, dict) else None

    version_file_rel = None
    version_attr = None
    if isinstance(version_cfg, dict):
        version_file_rel = version_cfg.get("file")
        version_attr = version_cfg.get("attr")

    if version_file_rel:
        version_file = pyproject_path.parent / version_file_rel
    elif isinstance(version_attr, str):
        # Map attr like khx_publish_pypi.__version:__version__ to src path
        attr_path = version_attr.replace(":", ".")
        module_path, _, _var = attr_path.rpartition(".")
        if not module_path:
            console.print("❌ [red]Invalid attr for dynamic version[/red]")
            return
        module_rel = Path("src") / Path(*module_path.split("."))
        version_file = pyproject_path.parent / module_rel.with_suffix(".py")
        version_file_rel = str(version_file.relative_to(pyproject_path.parent))
    else:
        console.print(
            "❌ [red]Dynamic version source not configured (file/attr) in pyproject.toml[/red]"
        )
        return
    current = read_version_from_python_file(version_file)
    if not current:
        console.print("❌ [red]Could not read current version from version file[/red]")
        return

    new_version = bump_version(current, part)
    if not new_version:
        console.print("❌ [red]Current version is invalid SemVer or unknown part[/red]")
        return

    ok = write_version_to_python_file(version_file, new_version)
    if not ok:
        console.print("❌ [red]Failed to write new version[/red]")
        return

    console.print(
        f"✅ Bumped {current} → [bold]{new_version}[/bold] in {version_file_rel}"
    )


@main.command()
@click.option(
    "--path",
    "project_path",
    type=click.Path(path_type=Path),
    default=Path.cwd(),
    help="Project root containing pyproject.toml",
)
@click.option("--clean/--no-clean", default=True, help="Clean dist/ before building")
def build(project_path: Path, clean: bool) -> None:
    """🏗️  Build the package using python -m build with niceties."""
    print_banner()

    pyproject_path = project_path / "pyproject.toml"
    if not pyproject_path.is_file():
        console.print("❌ [red]pyproject.toml not found[/red]")
        return

    # Ensure build is available
    if not shutil.which("python"):
        console.print("❌ [red]Python executable not found in PATH[/red]")
        return

    try:
        import build

        print(build.__version__)
    except Exception:
        console.print(
            "⚠️ [yellow]The 'build' package is not installed. Installing suggestion:[/yellow]"
        )
        console.print("   pip install build")

    # Run checks first
    console.print("\n🔍 [yellow]Running checks before build...[/yellow]")
    results = run_prechecks(project_path)
    print_report(results)
    if not results["summary"]["ready"]:
        console.print("❌ [red]Build aborted: required files missing[/red]")
        return

    # Optional clean
    dist_dir = project_path / "dist"
    if clean and dist_dir.exists():
        console.print("🧹 Cleaning dist/ ...")
        for child in dist_dir.iterdir():
            try:
                if child.is_file():
                    child.unlink()
                else:
                    shutil.rmtree(child)
            except Exception:
                pass

    console.print("🚀 Building with 'python -m build' ...")
    try:
        subprocess.run(["python", "-m", "build"], cwd=str(project_path), check=True)
    except subprocess.CalledProcessError:
        console.print("❌ [red]Build failed[/red]")
        return

    console.print("✅ [bold green]Build completed. Artifacts in dist/[/bold green]")


def _run_build_flow(project_path: Path, clean: bool = True) -> bool:
    """Run pre-checks and build; return True on success."""
    pyproject_path = project_path / "pyproject.toml"
    if not pyproject_path.is_file():
        console.print("❌ [red]pyproject.toml not found[/red]")
        return False

    # Ensure build is available hint
    try:
        import build

        print(build.__version__)
    except Exception:
        console.print(
            "⚠️ [yellow]The 'build' package is not installed. Installing suggestion:[/yellow]"
        )
        console.print("   pip install build")

    console.print("\n🔍 [yellow]Running checks before build...[/yellow]")
    results = run_prechecks(project_path)
    print_report(results)
    if not results["summary"]["ready"]:
        console.print("❌ [red]Build aborted: required files missing[/red]")
        return False

    dist_dir = project_path / "dist"
    if clean and dist_dir.exists():
        console.print("🧹 Cleaning dist/ ...")
        for child in dist_dir.iterdir():
            try:
                if child.is_file():
                    child.unlink()
                else:
                    shutil.rmtree(child)
            except Exception:
                pass

    console.print("🚀 Building with 'python -m build' ...")
    try:
        subprocess.run(["python", "-m", "build"], cwd=str(project_path), check=True)
    except subprocess.CalledProcessError:
        console.print("❌ [red]Build failed[/red]")
        return False

    console.print("✅ [bold green]Build completed. Artifacts in dist/[/bold green]")
    return True


@main.command()
@click.option(
    "--path",
    "project_path",
    type=click.Path(path_type=Path),
    default=Path.cwd(),
    help="Project root containing pyproject.toml",
)
def run(project_path: Path) -> None:
    """🚀 Run: complete guided publishing workflow - checks, tokens, bump, build, and publish."""
    print_banner()

    # Checks first
    results = run_prechecks(project_path)
    print_report(results)
    if not results["summary"]["ready"]:
        console.print("❌ [red]Run aborted: required files missing[/red]")
        return

    # Optional token setup
    console.print(f"\n🔑 [bold cyan]Token Setup[/bold cyan]")
    setup_choice = Prompt.ask(
        "Do you want to setup/configure PyPI tokens?",
        choices=["yes", "no", "check"],
        default="check",
        show_choices=True,
    )

    if setup_choice == "yes":
        config_setup_tokens()
    elif setup_choice == "check":
        # Check existing tokens
        from .config import get_token

        test_configured = False
        prod_configured = False
        try:
            get_token("testpypi")
            test_configured = True
        except ValueError:
            pass
        try:
            get_token("pypi")
            prod_configured = True
        except ValueError:
            pass

        if test_configured or prod_configured:
            console.print("ℹ️ [blue]Current token status:[/blue]")
            if test_configured:
                console.print("  ✅ Test PyPI token configured")
            else:
                console.print("  ❌ Test PyPI token not configured")
            if prod_configured:
                console.print("  ✅ PyPI token configured")
            else:
                console.print("  ❌ PyPI token not configured")

            setup_anyway = Confirm.ask("Setup/update tokens anyway?", default=False)
            if setup_anyway:
                config_setup_tokens()
        else:
            console.print("❌ [red]No tokens configured[/red]")
            setup_now = Confirm.ask("Setup tokens now?", default=True)
            if setup_now:
                config_setup_tokens()
    bump_choice = Prompt.ask(
        "Do you want to bump the version?",
        choices=["patch", "minor", "major", "skip"],
        default="skip",
        show_choices=True,
    )
    if bump_choice != "skip":
        # Reuse bump logic
        pyproject_path = project_path / "pyproject.toml"
        data = read_pyproject_toml(pyproject_path)
        if not data:
            console.print("❌ [red]pyproject.toml not found or invalid[/red]")
            return
        tool = data.get("tool", {}) or {}
        setuptools_cfg = tool.get("setuptools", {}) if isinstance(tool, dict) else {}
        dynamic_cfg = (
            setuptools_cfg.get("dynamic", {})
            if isinstance(setuptools_cfg, dict)
            else {}
        )
        version_cfg = (
            dynamic_cfg.get("version") if isinstance(dynamic_cfg, dict) else None
        )
        version_file_rel = (
            version_cfg.get("file") if isinstance(version_cfg, dict) else None
        )
        version_attr = (
            version_cfg.get("attr") if isinstance(version_cfg, dict) else None
        )
        if version_file_rel:
            version_file = pyproject_path.parent / version_file_rel
        elif isinstance(version_attr, str):
            attr_path = version_attr.replace(":", ".")
            module_path, _, _var = attr_path.rpartition(".")
            if not module_path:
                console.print("❌ [red]Invalid attr for dynamic version[/red]")
                return
            module_rel = Path("src") / Path(*module_path.split("."))
            version_file = pyproject_path.parent / module_rel.with_suffix(".py")
            version_file_rel = str(version_file.relative_to(pyproject_path.parent))
        else:
            console.print(
                "❌ [red]Dynamic version source not configured (file/attr) in pyproject.toml[/red]"
            )
            return
        current = read_version_from_python_file(version_file)
        new_version = bump_version(current or "0.0.0", bump_choice)
        if not new_version:
            console.print("❌ [red]Cannot compute new version[/red]")
            return
        if write_version_to_python_file(version_file, new_version):
            console.print(
                f"✅ Bumped {current or '0.0.0'} → [bold]{new_version}[/bold] in {version_file_rel}"
            )
        else:
            console.print("❌ [red]Failed to write new version[/red]")
            return

    # Confirm build
    if Confirm.ask("Proceed to build now?", default=True):
        build_success = _run_build_flow(project_path, clean=True)
        if not build_success:
            console.print("❌ [red]Build failed. Cannot proceed to publishing.[/red]")
            return
    else:
        console.print("⏭️ Skipping build.")
        return

    # Publishing options
    console.print(f"\n📤 [bold cyan]Publishing Options[/bold cyan]")
    publish_choice = Prompt.ask(
        "Do you want to publish the package?",
        choices=["test", "prod", "both", "skip"],
        default="skip",
        show_choices=True,
    )

    if publish_choice == "skip":
        console.print("⏭️ Skipping publishing.")
        return

    # Check if tokens are available
    from .config import get_token

    tokens_available = {"test": False, "prod": False}

    try:
        get_token("testpypi")
        tokens_available["test"] = True
    except ValueError:
        pass

    try:
        get_token("pypi")
        tokens_available["prod"] = True
    except ValueError:
        pass

    # Validate tokens based on choice
    if publish_choice in ["test", "both"] and not tokens_available["test"]:
        console.print(
            "❌ [red]Test PyPI token not configured. Run 'khx-publish-pypi setup-tokens' first.[/red]"
        )
        return

    if publish_choice in ["prod", "both"] and not tokens_available["prod"]:
        console.print(
            "❌ [red]PyPI token not configured. Run 'khx-publish-pypi setup-tokens' first.[/red]"
        )
        return

    # Execute publishing based on choice
    published_to = []
    package_name = None

    if publish_choice == "test":
        console.print("\n🧪 [yellow]Publishing to Test PyPI...[/yellow]")
        success, package_name = publish_to_testpypi(project_path, skip_build=True)
        if success:
            published_to.append("testpypi")
        else:
            console.print("❌ [red]Failed to publish to Test PyPI[/red]")

    elif publish_choice == "prod":
        console.print("\n🚀 [yellow]Publishing to PyPI...[/yellow]")
        success, package_name = publish_to_pypi(project_path, skip_build=True)
        if success:
            published_to.append("pypi")
        else:
            console.print("❌ [red]Failed to publish to PyPI[/red]")

    elif publish_choice == "both":
        console.print("\n🧪 [yellow]Publishing to Test PyPI first...[/yellow]")
        test_success, test_package_name = publish_to_testpypi(
            project_path, skip_build=True
        )

        if test_success:
            published_to.append("testpypi")
            package_name = test_package_name
            console.print("✅ [green]Test PyPI publish successful![/green]")
            console.print("\n🚀 [yellow]Now publishing to production PyPI...[/yellow]")

            proceed_to_prod = Confirm.ask("Proceed to production PyPI?", default=True)
            if proceed_to_prod:
                prod_success, prod_package_name = publish_to_pypi(
                    project_path, skip_build=True
                )
                if prod_success:
                    published_to.append("pypi")
                    if not package_name:
                        package_name = prod_package_name
                else:
                    console.print("❌ [red]Failed to publish to production PyPI[/red]")
            else:
                console.print("⏭️ Skipping production PyPI publish.")
        else:
            console.print(
                "❌ [red]Test PyPI publish failed. Aborting production publish.[/red]"
            )

    # Display package URLs if any publishing was successful
    if published_to and package_name:
        display_package_urls(package_name, published_to)


@main.command()
@click.option(
    "--path",
    "project_path",
    type=click.Path(path_type=Path),
    default=Path.cwd(),
    help="Project root containing pyproject.toml",
)
def auto_run(project_path: Path) -> None:
    """🚀 Auto-run: automated publishing workflow - skips tokens, auto-patch version, auto-build, auto-publish to prod."""
    print_banner()

    # Checks first
    results = run_prechecks(project_path)
    print_report(results)
    if not results["summary"]["ready"]:
        console.print("❌ [red]Auto-run aborted: required files missing[/red]")
        return

    # Skip token setup - assume tokens are already configured
    console.print("ℹ️ [blue]Skipping token setup (assuming tokens are configured)[/blue]")

    # Auto-bump version to patch
    console.print("📈 [yellow]Auto-bumping version (patch)...[/yellow]")
    pyproject_path = project_path / "pyproject.toml"
    data = read_pyproject_toml(pyproject_path)
    if not data:
        console.print("❌ [red]pyproject.toml not found or invalid[/red]")
        return
    
    tool = data.get("tool", {}) or {}
    setuptools_cfg = tool.get("setuptools", {}) if isinstance(tool, dict) else {}
    dynamic_cfg = (
        setuptools_cfg.get("dynamic", {})
        if isinstance(setuptools_cfg, dict)
        else {}
    )
    version_cfg = (
        dynamic_cfg.get("version") if isinstance(dynamic_cfg, dict) else None
    )
    version_file_rel = (
        version_cfg.get("file") if isinstance(version_cfg, dict) else None
    )
    version_attr = (
        version_cfg.get("attr") if isinstance(version_cfg, dict) else None
    )
    
    if version_file_rel:
        version_file = pyproject_path.parent / version_file_rel
    elif isinstance(version_attr, str):
        attr_path = version_attr.replace(":", ".")
        module_path, _, _var = attr_path.rpartition(".")
        if not module_path:
            console.print("❌ [red]Invalid attr for dynamic version[/red]")
            return
        module_rel = Path("src") / Path(*module_path.split("."))
        version_file = pyproject_path.parent / module_rel.with_suffix(".py")
        version_file_rel = str(version_file.relative_to(pyproject_path.parent))
    else:
        console.print(
            "❌ [red]Dynamic version source not configured (file/attr) in pyproject.toml[/red]"
        )
        return
    
    current = read_version_from_python_file(version_file)
    new_version = bump_version(current or "0.0.0", "patch")
    if not new_version:
        console.print("❌ [red]Cannot compute new version[/red]")
        return
    
    if write_version_to_python_file(version_file, new_version):
        console.print(
            f"✅ Bumped {current or '0.0.0'} → [bold]{new_version}[/bold] in {version_file_rel}"
        )
    else:
        console.print("❌ [red]Failed to write new version[/red]")
        return

    # Auto-build
    console.print("🔨 [yellow]Auto-building package...[/yellow]")
    build_success = _run_build_flow(project_path, clean=True)
    if not build_success:
        console.print("❌ [red]Build failed. Cannot proceed to publishing.[/red]")
        return

    # Check if prod token is available
    from .config import get_token
    
    try:
        get_token("pypi")
    except ValueError:
        console.print(
            "❌ [red]PyPI token not configured. Run 'khx-publish-pypi setup-tokens' first.[/red]"
        )
        return

    # Auto-publish to prod
    console.print("🚀 [yellow]Auto-publishing to PyPI...[/yellow]")
    success, package_name = publish_to_pypi(project_path, skip_build=True)
    if success:
        console.print("✅ [green]Successfully published to PyPI![/green]")
        if package_name:
            display_package_urls(package_name, ["pypi"])
    else:
        console.print("❌ [red]Failed to publish to PyPI[/red]")


if __name__ == "__main__":
    main()
