from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align


console = Console()


def print_banner() -> None:
    """🌟 Print the beautiful welcome banner with proper styling"""
    console.print()

    # Create the main title
    title = Text("💫 Welcome to KHX-PUBLISH-PYPI 💫", style="bold magenta")
    console.print(Align.center(title))

    # Create the decorative line
    console.print("━" * 80, style="magenta", justify="center")

    # Subtitle with emoji
    subtitle = Text(
        "🚀 Let's prepare your Python package for publishing!", style="cyan"
    )
    console.print(Align.center(subtitle))

    # Bottom decorative line
    console.print("━" * 80, style="magenta", justify="center")


def _status_emoji(ok: bool) -> str:
    return "✅" if ok else "❌"


def print_report(results: Dict[str, Any]) -> None:
    """🎨 Print the beautiful results report with emoji styling"""
    checks = results["checks"]
    summary = results["summary"]

    console.print()

    # Header section
    console.print("≋" * 60, style="cyan", justify="center")
    header_title = Text("🌟 KHX-PUBLISH-PYPI READY CHECK 🌟", style="bold cyan")
    console.print(Align.center(header_title))
    console.print("≋" * 60, style="cyan", justify="center")

    # Individual checks with dots and proper spacing
    check_labels = {
        "Package path": "📂 Checking package path",
        "pyproject.toml": "📄 pyproject.toml",
        "README.md": "📄 README.md",
        "LICENSE (recommended)": "📄 LICENSE",
        "Package folder": "📦 Package folder",
        "Project name": "🏷️  Project name",
        "Version": "🔢 Version",
    }

    status_map = {c["label"]: c for c in checks}

    for original_label, display_label in check_labels.items():
        check = status_map.get(original_label, {"ok": False, "detail": None})
        status_emoji = _status_emoji(check["ok"])

        # Create the dotted line effect
        dots = "." * (35 - len(display_label))
        line = f"{display_label} {dots} {status_emoji}"

        # Add detail if available (like package name or version)
        if check.get("detail") and check["ok"]:
            if "folder" in original_label.lower():
                line += f" ({check['detail']})"
            elif (
                "version" in original_label.lower() or "name" in original_label.lower()
            ):
                line += f" ({check['detail']})"
        elif not check["ok"] and "LICENSE" in original_label:
            line += " Missing (recommended)"

        console.print(line)

    console.print("━" * 80, style="cyan", justify="center")

    # Status message
    if summary["ready"]:
        console.print(
            "✨ [bold green]All required files found, ready to build![/bold green] ✨",
            justify="center",
        )
    else:
        console.print(
            "⚠️  [bold red]Some required files are missing![/bold red] ⚠️",
            justify="center",
        )

    console.print("━" * 80, style="cyan", justify="center")

    # Summary table with better styling
    table = Table(
        title="📊 Summary",
        expand=False,
        show_header=True,
        header_style="bold blue",
        border_style="blue",
    )
    table.add_column("Check", justify="left", style="bold")
    table.add_column("Status", justify="left")

    # Add rows to table
    for original_label, display_label in check_labels.items():
        check = status_map.get(original_label, {"ok": False, "detail": None})

        # Clean up label for table
        clean_label = (
            display_label.replace("📂 Checking ", "")
            .replace("📄 ", "")
            .replace("📦 ", "")
            .replace("🏷️  ", "")
            .replace("🔢 ", "")
        )
        if clean_label == "package path":
            clean_label = "Package Path"

        status_text = f"{_status_emoji(check['ok'])}"
        if check.get("detail") and check["ok"]:
            if "version" in original_label.lower():
                status_text += f" {check['detail']}"
            elif "folder" in original_label.lower():
                status_text += " OK"
            else:
                status_text += " OK"
        elif not check["ok"]:
            status_text += " Missing" if "LICENSE" not in original_label else " Missing"
        else:
            status_text += " OK"

        table.add_row(clean_label, status_text)

    console.print(table)

    # Final status panel with next steps
    if summary["ready"]:
        package_info = (
            f"Package: {summary['package_name']} | Version: {summary['version']}"
        )
        status_msg = f"🎉 [bold green]Status: READY TO BUILD[/bold green] 🎉\n{package_info}\n[dim](Next step: Run build check before upload)[/dim]"
        console.print(Panel(status_msg, border_style="green", padding=(1, 2)))
    else:
        status_msg = "⚠️ [bold red]Status: NOT READY[/bold red] ⚠️\n[dim]Fix the ❌ items above and re-run the checks.[/dim]"
        console.print(Panel(status_msg, border_style="red", padding=(1, 2)))

    # Warnings
    if summary.get("name_folder_warning"):
        console.print(
            Panel(
                f"⚠️ Name vs folder mismatch: {summary['name_folder_warning']}",
                border_style="yellow",
                padding=(1, 2),
            )
        )

    console.print("━" * 80, style="cyan")
