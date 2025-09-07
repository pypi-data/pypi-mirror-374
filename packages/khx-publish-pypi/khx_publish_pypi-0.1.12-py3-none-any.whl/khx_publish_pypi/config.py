"""Configuration module for secure token management and settings."""

import os
from typing import Optional
import keyring
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()


def get_token(env: str) -> str:
    """
    Retrieve API token for the specified environment.

    Args:
        env: Environment name ('testpypi' or 'pypi')

    Returns:
        API token as string

    Raises:
        ValueError: If token is not found
    """
    service_name = f"khx-publish-{env}"
    # For PyPI API tokens, username must always be __token__
    username = "__token__"

    # Try keyring first
    token = keyring.get_password(service_name, username)
    if token:
        return token

    # Fallback to environment variables
    env_var = f"{env.upper()}_TOKEN"
    token = os.getenv(env_var)
    if token:
        return token

    raise ValueError(
        f"Token for {env} not found. Run 'khx-publish-pypi setup-tokens' to configure."
    )


def setup_tokens() -> None:
    """
    Interactive setup for storing API tokens securely.
    """
    console.print("🔐 [bold cyan]Setting up API tokens[/bold cyan]")
    console.print("Tokens will be stored securely using your system's keyring.\n")

    service_name_test = "khx-publish-testpypi"
    service_name_prod = "khx-publish-pypi"
    # For PyPI API tokens, username must always be __token__
    username = "__token__"

    # Check existing tokens
    test_token_exists = keyring.get_password(service_name_test, username) is not None
    prod_token_exists = keyring.get_password(service_name_prod, username) is not None

    if test_token_exists or prod_token_exists:
        console.print("ℹ️ [blue]Existing tokens found:[/blue]")
        if test_token_exists:
            console.print("  ✅ Test PyPI token is already configured")
        if prod_token_exists:
            console.print("  ✅ PyPI token is already configured")
        console.print()

    # Ask which environment to configure
    console.print("Which PyPI environment would you like to configure?")
    choices = []
    if not test_token_exists:
        choices.append("test")
    if not prod_token_exists:
        choices.append("prod")
    if not test_token_exists and not prod_token_exists:
        choices.append("both")

    if not choices:
        console.print("✅ [green]All tokens are already configured![/green]")
        return

    if len(choices) == 1:
        env_choice = choices[0]
        console.print(f"Auto-selecting: {env_choice}")
    else:
        env_choice = Prompt.ask(
            "Choose environment",
            choices=choices,
            default="both" if "both" in choices else choices[0],
        )

    # Handle token input based on choice
    tokens_to_setup = []
    if env_choice in ["test", "both"]:
        tokens_to_setup.append(("Test PyPI", service_name_test, "testpypi"))
    if env_choice in ["prod", "both"]:
        tokens_to_setup.append(("PyPI", service_name_prod, "pypi"))

    for display_name, service_name, env in tokens_to_setup:
        console.print(f"\n🔑 [bold]{display_name} Token Setup[/bold]")

        # Check if token already exists
        existing_token = keyring.get_password(service_name, username)
        if existing_token:
            console.print(f"ℹ️ [blue]{display_name} token is already configured[/blue]")
            update = Confirm.ask(
                f"Do you want to update the {display_name} token?", default=False
            )
            if not update:
                console.print(f"⏭️ [yellow]Skipped {display_name} token update[/yellow]")
                continue

        # Get token input
        token = console.input(f"Enter your {display_name} API token: ").strip()
        if not token:
            console.print(f"❌ [red]{display_name} token cannot be empty[/red]")
            continue

        # Ask for confirmation to save
        save = Confirm.ask(f"Save {display_name} token securely?", default=True)
        if save:
            keyring.set_password(service_name, username, token)
            console.print(f"✅ [green]{display_name} token stored securely[/green]")
        else:
            console.print(f"⏭️ [yellow]{display_name} token not saved[/yellow]")

    console.print("\n🎉 [bold green]Token setup complete![/bold green]")


def update_token(env: str, token: str) -> None:
    """
    Update API token for the specified environment.

    Args:
        env: Environment name ('testpypi' or 'pypi')
        token: New API token to store
    """
    service_name = f"khx-publish-{env}"
    # For PyPI API tokens, username must always be __token__
    username = "__token__"

    keyring.set_password(service_name, username, token)
    console.print(f"✅ [green]{env.upper()} token updated securely[/green]")


if __name__ == "__main__":
    # Simple test
    try:
        # Test token retrieval (will fail if not set)
        try:
            token = get_token("testpypi")
            console.print(f"✅ [green]Test PyPI token found: {token[:10]}...[/green]")
        except ValueError:
            console.print("ℹ️ [blue]Test PyPI token not configured[/blue]")

        try:
            token = get_token("pypi")
            console.print(f"✅ [green]PyPI token found: {token[:10]}...[/green]")
        except ValueError:
            console.print("ℹ️ [blue]PyPI token not configured[/blue]")

        console.print("🔧 [yellow]Run setup_tokens() to configure tokens[/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")
