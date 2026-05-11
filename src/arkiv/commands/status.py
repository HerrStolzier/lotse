"""Status-related CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from arkiv.commands.common import DEFAULT_CONFIG_FILE, __version__, console, get_config


def status(
    config: Path | None = typer.Option(None, "--config", "-c"),
) -> None:
    """Show processing statistics and system status."""
    from arkiv.core.ocr import ocr_available
    from arkiv.db.store import Store

    cfg = get_config(config)

    console.print(f"\n[bold]Kurier[/bold] v{__version__}\n")

    config_display = config or DEFAULT_CONFIG_FILE
    console.print(f"[dim]Config:[/dim]  {config_display}")
    console.print(f"[dim]Database:[/dim] {cfg.database.path}")
    console.print(f"[dim]Inbox:[/dim]   {cfg.inbox_dir}")
    console.print(f"[dim]LLM:[/dim]     {cfg.llm.provider}/{cfg.llm.model}")
    console.print(f"[dim]Routes:[/dim]  {len(cfg.routes)} configured")
    console.print(f"[dim]Embed:[/dim]   {cfg.embeddings.model}")

    ocr = ocr_available()
    if ocr["tesseract_bin"]:
        console.print("[dim]OCR:[/dim]     [green]available[/green] (Tesseract + PyMuPDF)")
    elif ocr["pymupdf"]:
        console.print("[dim]OCR:[/dim]     [yellow]partial[/yellow] (PyMuPDF only, no Tesseract)")
    else:
        console.print(
            "[dim]OCR:[/dim]     [dim]not installed[/dim] "
            "(reinstall kurier and ensure PyMuPDF/Tesseract are available)"
        )
    console.print()

    if not cfg.database.path.exists():
        console.print("[dim]No items processed yet.[/dim]")
        return

    store = Store(cfg.database.path)
    s = store.stats()

    console.print(f"[bold]Total items:[/bold] {s['total_items']}\n")

    if s.get("vec_enabled"):
        console.print(
            f"[dim]Semantic search:[/dim] [green]enabled[/green]"
            f" ({s.get('embeddings', 0)} embeddings)\n"
        )
    else:
        console.print(
            "[dim]Semantic search:[/dim] [yellow]disabled[/yellow] (pip install sqlite-vec)\n"
        )

    if s["categories"]:
        cat_table = Table(title="Categories")
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Count", justify="right")
        for cat, count in s["categories"].items():
            cat_table.add_row(cat, str(count))
        console.print(cat_table)


def register(app: typer.Typer) -> None:
    """Register status commands."""
    app.command()(status)
