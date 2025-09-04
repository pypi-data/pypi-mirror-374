"""Main CLI application for Bitbucket Code Reviewer."""

from typing import Optional

import typer
from rich.console import Console

from . import __version__

app = typer.Typer(
    name="bb-review",
    help="Bitbucket Code Reviewer CLI Tool",
    add_completion=False,
)
console = Console()


@app.callback()
def callback():
    """Bitbucket Code Reviewer CLI Tool."""


@app.command()
def version():
    """Show the version."""
    console.print(f"bb-review version {__version__}")


@app.command()
def review(
    repository: str = typer.Argument(..., help="Repository in format 'workspace/repo'"),
    pull_request_id: Optional[int] = typer.Option(
        None, "--pr", "-p", help="Pull request ID"
    ),
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Branch name"),
    token: Optional[str] = typer.Option(
        None, "--token", "-t", help="Bitbucket access token"
    ),
):
    """Review code in a Bitbucket repository."""
    console.print(f"[bold blue]Reviewing repository:[/bold blue] {repository}")

    if pull_request_id:
        console.print(f"[bold green]Pull Request ID:[/bold green] {pull_request_id}")
    elif branch:
        console.print(f"[bold green]Branch:[/bold green] {branch}")
    else:
        console.print("[yellow]Warning: No pull request or branch specified[/yellow]")

    if token:
        console.print("[green]✓ Access token provided[/green]")
    else:
        console.print("[yellow]⚠ No access token provided[/yellow]")

    # TODO: Implement actual review logic
    console.print("[bold]Code review functionality coming soon![/bold]")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    token: Optional[str] = typer.Option(
        None, "--token", help="Set Bitbucket access token"
    ),
    workspace: Optional[str] = typer.Option(
        None, "--workspace", help="Set default workspace"
    ),
):
    """Manage configuration settings."""
    if show:
        console.print("[bold]Current Configuration:[/bold]")
        console.print("• Access Token: [red]Not configured[/red]")
        console.print("• Default Workspace: [red]Not configured[/red]")
    elif token:
        console.print("[green]✓ Access token configured[/green]")
    elif workspace:
        console.print(f"[green]✓ Default workspace set to: {workspace}[/green]")
    else:
        console.print(
            "[yellow]Use --show to view config or provide options to update[/yellow]"
        )
