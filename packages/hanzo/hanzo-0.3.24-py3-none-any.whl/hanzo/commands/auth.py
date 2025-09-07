"""Authentication commands."""

import os
from pathlib import Path

import click
from rich.prompt import Prompt

from ..utils.output import console


@click.group(name="auth")
def auth_group():
    """Manage Hanzo authentication."""
    pass


@auth_group.command()
@click.option("--email", "-e", help="Email address")
@click.option("--password", "-p", help="Password (not recommended, use prompt)")
@click.option("--api-key", "-k", help="API key for direct authentication")
@click.option("--sso", is_flag=True, help="Use SSO authentication")
@click.pass_context
async def login(ctx, email: str, password: str, api_key: str, sso: bool):
    """Login to Hanzo AI."""
    try:
        from hanzoai.auth import HanzoAuth
    except ImportError:
        console.print("[red]Error:[/red] hanzoai not installed")
        console.print("Install with: pip install hanzo")
        return

    auth = HanzoAuth()

    try:
        if api_key:
            # Direct API key authentication
            console.print("Authenticating with API key...")
            result = await auth.login_with_api_key(api_key)
        elif sso:
            # SSO authentication via browser
            console.print("Opening browser for SSO login...")
            console.print("If browser doesn't open, visit: https://iam.hanzo.ai/login")
            result = await auth.login_with_sso()
        else:
            # Email/password authentication
            if not email:
                email = Prompt.ask("Email")
            if not password:
                password = Prompt.ask("Password", password=True)

            console.print("Authenticating...")
            result = await auth.login(email, password)

        # Save credentials
        config_dir = Path.home() / ".hanzo"
        config_dir.mkdir(exist_ok=True)

        config_file = config_dir / "auth.json"
        await auth.save_credentials(config_file)

        # Also set environment variable if API key is available
        if api_key or result.get("api_key"):
            key = api_key or result.get("api_key")
            console.print(f"\n[dim]To use in environment:[/dim]")
            console.print(f"export HANZO_API_KEY={key}")

        console.print(f"[green]✓[/green] Logged in as {result.get('email', 'user')}")

        # Check organization
        if org := result.get("organization"):
            console.print(f"  Organization: {org}")

        # Check permissions
        if permissions := result.get("permissions"):
            console.print(f"  Permissions: {', '.join(permissions)}")

    except Exception as e:
        console.print(f"[red]Login failed: {e}[/red]")


@auth_group.command()
@click.pass_context
async def logout(ctx):
    """Logout from Hanzo AI."""
    try:
        from hanzoai.auth import HanzoAuth
    except ImportError:
        console.print("[red]Error:[/red] hanzoai not installed")
        return

    auth = HanzoAuth()

    try:
        await auth.logout()

        # Remove saved credentials
        config_file = Path.home() / ".hanzo" / "auth.json"
        if config_file.exists():
            config_file.unlink()

        console.print("[green]✓[/green] Logged out successfully")

    except Exception as e:
        console.print(f"[red]Logout failed: {e}[/red]")


@auth_group.command()
@click.pass_context
async def status(ctx):
    """Show authentication status."""
    # Check environment variable
    if api_key := os.environ.get("HANZO_API_KEY"):
        console.print("[green]✓[/green] HANZO_API_KEY environment variable set")
        console.print(f"  Key: {api_key[:8]}...{api_key[-4:]}")

    # Check saved credentials
    config_file = Path.home() / ".hanzo" / "auth.json"
    if config_file.exists():
        try:
            from hanzoai.auth import HanzoAuth

            auth = HanzoAuth()
            creds = await auth.load_credentials(config_file)

            console.print("[green]✓[/green] Saved credentials found")
            if email := creds.get("email"):
                console.print(f"  Email: {email}")
            if org := creds.get("organization"):
                console.print(f"  Organization: {org}")

            # Verify credentials are still valid
            with console.status("Verifying credentials..."):
                try:
                    user_info = await auth.get_user_info()
                    console.print("[green]✓[/green] Credentials are valid")

                    # Show usage stats if available
                    if usage := user_info.get("usage"):
                        console.print("\n[cyan]Usage:[/cyan]")
                        console.print(f"  API calls: {usage.get('api_calls', 0)}")
                        console.print(f"  Tokens: {usage.get('tokens', 0)}")
                        if quota := usage.get("quota"):
                            console.print(
                                f"  Quota: {usage.get('tokens', 0)} / {quota}"
                            )
                except Exception:
                    console.print("[yellow]![/yellow] Credentials may be expired")
                    console.print("Run 'hanzo auth login' to refresh")

        except Exception as e:
            console.print(f"[red]Error reading credentials: {e}[/red]")
    else:
        console.print("[yellow]![/yellow] Not logged in")
        console.print("Run 'hanzo auth login' to authenticate")


@auth_group.command()
@click.option("--name", "-n", required=True, help="API key name")
@click.option(
    "--permissions", "-p", multiple=True, help="Permissions (e.g., read, write, admin)"
)
@click.option("--expires", "-e", help="Expiration (e.g., 30d, 1y, never)")
@click.pass_context
async def create_key(ctx, name: str, permissions: tuple, expires: str):
    """Create a new API key."""
    try:
        from hanzoai.auth import HanzoAuth
    except ImportError:
        console.print("[red]Error:[/red] hanzoai not installed")
        return

    auth = HanzoAuth()

    # Ensure authenticated
    if not await auth.is_authenticated():
        console.print("[red]Error:[/red] Not authenticated")
        console.print("Run 'hanzo auth login' first")
        return

    with console.status(f"Creating API key '{name}'..."):
        try:
            result = await auth.create_api_key(
                name=name,
                permissions=list(permissions) if permissions else None,
                expires=expires,
            )

            key = result.get("key")
            console.print(f"[green]✓[/green] Created API key: {name}")
            console.print(
                f"\n[yellow]Save this key - it won't be shown again:[/yellow]"
            )
            console.print(f"{key}")
            console.print(f"\nTo use:")
            console.print(f"export HANZO_API_KEY={key}")

        except Exception as e:
            console.print(f"[red]Failed to create key: {e}[/red]")


@auth_group.command()
@click.pass_context
async def list_keys(ctx):
    """List your API keys."""
    try:
        from hanzoai.auth import HanzoAuth
    except ImportError:
        console.print("[red]Error:[/red] hanzoai not installed")
        return

    auth = HanzoAuth()

    # Ensure authenticated
    if not await auth.is_authenticated():
        console.print("[red]Error:[/red] Not authenticated")
        console.print("Run 'hanzo auth login' first")
        return

    with console.status("Loading API keys..."):
        try:
            keys = await auth.list_api_keys()

            if keys:
                from rich.table import Table

                table = Table(title="API Keys")
                table.add_column("Name", style="cyan")
                table.add_column("Created", style="green")
                table.add_column("Last Used", style="yellow")
                table.add_column("Permissions", style="blue")
                table.add_column("Status", style="magenta")

                for key in keys:
                    table.add_row(
                        key.get("name", "unknown"),
                        key.get("created_at", "unknown"),
                        key.get("last_used", "never"),
                        ", ".join(key.get("permissions", [])),
                        key.get("status", "active"),
                    )

                console.print(table)
            else:
                console.print("[yellow]No API keys found[/yellow]")
                console.print("Create one with: hanzo auth create-key")

        except Exception as e:
            console.print(f"[red]Failed to list keys: {e}[/red]")


@auth_group.command()
@click.argument("name")
@click.pass_context
async def revoke_key(ctx, name: str):
    """Revoke an API key."""
    try:
        from hanzoai.auth import HanzoAuth
    except ImportError:
        console.print("[red]Error:[/red] hanzoai not installed")
        return

    auth = HanzoAuth()

    # Ensure authenticated
    if not await auth.is_authenticated():
        console.print("[red]Error:[/red] Not authenticated")
        console.print("Run 'hanzo auth login' first")
        return

    if click.confirm(f"Revoke API key '{name}'?"):
        with console.status(f"Revoking key '{name}'..."):
            try:
                await auth.revoke_api_key(name)
                console.print(f"[green]✓[/green] Revoked API key: {name}")
            except Exception as e:
                console.print(f"[red]Failed to revoke key: {e}[/red]")


@auth_group.command()
@click.pass_context
async def whoami(ctx):
    """Show current user information."""
    try:
        from hanzoai.auth import HanzoAuth
    except ImportError:
        console.print("[red]Error:[/red] hanzoai not installed")
        return

    auth = HanzoAuth()

    # Check if authenticated
    if not await auth.is_authenticated():
        console.print("[yellow]Not authenticated[/yellow]")

        # Check if API key is set
        if os.environ.get("HANZO_API_KEY"):
            console.print("HANZO_API_KEY is set but may be invalid")
        else:
            console.print("Run 'hanzo auth login' to authenticate")
        return

    with console.status("Loading user information..."):
        try:
            user = await auth.get_user_info()

            console.print(f"[cyan]User Information:[/cyan]")
            console.print(f"  ID: {user.get('id', 'unknown')}")
            console.print(f"  Email: {user.get('email', 'unknown')}")
            console.print(f"  Name: {user.get('name', 'unknown')}")

            if org := user.get("organization"):
                console.print(f"\n[cyan]Organization:[/cyan]")
                console.print(f"  Name: {org.get('name', 'unknown')}")
                console.print(f"  Role: {org.get('role', 'member')}")

            if teams := user.get("teams"):
                console.print(f"\n[cyan]Teams:[/cyan]")
                for team in teams:
                    console.print(f"  • {team}")

            if perms := user.get("permissions"):
                console.print(f"\n[cyan]Permissions:[/cyan]")
                for perm in sorted(perms):
                    console.print(f"  • {perm}")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
