"""Kurier CLI - your AI-powered data pilot."""

from __future__ import annotations

import typer

from arkiv import __version__
from arkiv.commands import register_commands
from arkiv.commands.common import console, launch_tui

app = typer.Typer(
    name="arkiv",
    help="Universal capture -> classify -> route. Your AI-powered data pilot.",
    no_args_is_help=False,
)

register_commands(app)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Show version"),
) -> None:
    """Kurier - your AI-powered data pilot."""
    if version:
        console.print(f"kurier {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        launch_tui(None)
