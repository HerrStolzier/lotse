"""API server CLI commands."""

from __future__ import annotations

import logging
from pathlib import Path

import typer

from arkiv.commands.common import __version__, console, get_config


def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h"),
    port: int = typer.Option(8790, "--port", "-p"),
    config: Path | None = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    force: bool = typer.Option(
        False,
        "--force",
        help="Allow binding to non-localhost without --api-key (insecure).",
    ),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="KURIER_API_KEY",
        help="API key required for non-localhost access (header: x-api-key).",
    ),
) -> None:
    """Start the REST API server."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    try:
        import uvicorn
    except ImportError:
        console.print("[red]Missing dependency.[/red] Reinstall Kurier to restore API packages:")
        console.print('  pip install "kurier @ git+https://github.com/HerrStolzier/kurier.git"')
        raise typer.Exit(1) from None

    if host != "127.0.0.1":
        if not force and not api_key:
            console.print(
                f"\n[red bold]Fehler:[/red bold] Binding to [bold]{host}[/bold] "
                "exposes the API to your network.\n"
                "Use [bold]--api-key <key>[/bold] to require authentication, "
                "or [bold]--force[/bold] to allow unauthenticated access (insecure).\n"
            )
            raise typer.Exit(1)

        if api_key:
            console.print(
                f"\n[yellow]Non-localhost binding:[/yellow] "
                f"[bold]{host}:{port}[/bold] — API key authentication active.\n"
            )
        else:
            console.print(
                f"\n[yellow bold]Security Warning:[/yellow bold] Binding to "
                f"[bold]{host}[/bold] exposes the API to your network.\n"
                "[yellow]All endpoints are unauthenticated. Anyone on your network "
                "can search, upload, and read your classified documents.[/yellow]\n"
            )

    from arkiv.inlets.api import create_app

    cfg = get_config(config)
    localhost_only = host != "127.0.0.1" and not force
    api = create_app(cfg, api_key=api_key, localhost_only=localhost_only)

    console.print(f"\n[bold]Kurier API[/bold] v{__version__}")
    console.print(f"[dim]Docs:[/dim]    http://{host}:{port}/docs")
    console.print(f"[dim]Health:[/dim]  http://{host}:{port}/health\n")

    uvicorn.run(api, host=host, port=port, log_level="info")


def register(app: typer.Typer) -> None:
    """Register API server commands."""
    app.command()(serve)
