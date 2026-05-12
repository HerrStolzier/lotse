"""Ingestion-related CLI commands."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

import typer

from arkiv.application.ingest import ingest_file as ingest_file_workflow
from arkiv.application.ingest import ingest_text as ingest_text_workflow
from arkiv.commands.common import console, get_context


def add(
    path: Path = typer.Argument(..., help="Dateipfad oder '-' für Text aus stdin"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Pfad zur Einstellungsdatei"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Ein Dokument verarbeiten und einsortieren."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    ctx = get_context(config)

    if str(path) == "-":
        import sys

        text = sys.stdin.read()
        result = ingest_text_workflow(ctx, text)
    elif path.exists():
        result = ingest_file_workflow(ctx, path)
    else:
        console.print(f"[red]Nicht gefunden:[/red] {path}")
        raise typer.Exit(1)

    if result.success:
        console.print(f"[green]✓[/green] {result.message}")
    else:
        console.print(f"[red]✗[/red] {result.message}")
        raise typer.Exit(1)


def watch(
    config: Path | None = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Eingangs-Ordner beobachten und neue Dateien automatisch verarbeiten."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    from arkiv.inlets.watch import Watcher

    ctx = get_context(config)
    cfg = ctx.config
    engine = ctx.engine

    console.print(f"[blue]Kurier beobachtet:[/blue] {cfg.inbox_dir}")
    console.print("[dim]Zum Beenden Strg+C drücken[/dim]")

    def _ingest_and_discard(p: Path) -> None:
        result = engine.ingest_file(p)
        if cfg.notifications and result and result.success:
            from arkiv.notifications import notify

            notify("Kurier", f"{p.name} → {result.route_name}")

    watcher = Watcher(
        cfg.inbox_dir,
        cast_callback(_ingest_and_discard),
        llm_provider=cfg.llm.provider,
    )
    watcher.start()


def cast_callback(callback: Callable[[Path], None]) -> Callable[[Path], None]:
    """Keep watcher callback typing explicit and local."""
    return callback


def register(app: typer.Typer) -> None:
    """Register ingestion commands."""
    app.command()(add)
    app.command()(watch)
