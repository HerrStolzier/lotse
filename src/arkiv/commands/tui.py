"""TUI-related CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from arkiv.commands.common import launch_tui


def tui(
    config: Annotated[Path | None, typer.Option("--config", "-c")] = None,
) -> None:
    """Interaktive Terminal-Oberfläche starten."""
    launch_tui(config)


def register(app: typer.Typer) -> None:
    """Register TUI commands."""
    app.command()(tui)
