"""Search-related CLI commands."""

from __future__ import annotations

import logging
from pathlib import Path

import typer
from rich.table import Table

from arkiv.application.search import search_items as search_items_workflow
from arkiv.commands.common import console, get_context


def search(
    query: str = typer.Argument(..., help="Suchfrage in normaler Sprache"),
    limit: int = typer.Option(20, "--limit", "-n"),
    mode: str = typer.Option(
        "auto",
        "--mode",
        "-m",
        help="Suchart: auto, fts (Wortsuche), vec (Bedeutungssuche)",
    ),
    memory: bool = typer.Option(
        False,
        "--memory",
        help="Lasse Kurier unklare Suchfragen lokal verbessern",
    ),
    config: Path | None = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Verarbeitete Dokumente suchen."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    ctx = get_context(config)
    results, assist = search_items_workflow(ctx, query, limit=limit, mode=mode, memory=memory)

    if not results:
        console.print(f"[yellow]Keine passenden Dokumente für “{query}” gefunden.[/yellow]")
        console.print(
            "[dim]Versuche einen anderen Begriff, eine Dokumentart wie “Rechnung” "
            "oder nutze --memory für ungenaue Alltagssprache.[/dim]"
        )
        console.print("[dim]Dieser Suchfehler kann im Beta-Bericht sichtbar werden.[/dim]")
        return

    if ctx.engine.store.vec_enabled and mode in ("auto", "vec"):
        console.print("[dim]Suche: Wörter + Bedeutung kombiniert[/dim]\n")
    else:
        console.print("[dim]Suche: Wortsuche[/dim]\n")

    if memory and assist and assist.rewrites:
        rewrites = ", ".join(assist.rewrites)
        console.print(f"[dim]Kurier hat zusätzlich gesucht nach: {rewrites}[/dim]\n")
    elif not memory:
        console.print(
            "[dim]Tipp: Mit --memory versteht Kurier ungenauere Suchfragen besser.[/dim]\n"
        )

    table = Table(title=f"Gefundene Dokumente für: {query}")
    table.add_column("ID", style="dim")
    table.add_column("Titel", style="bold")
    table.add_column("Art", style="cyan")
    table.add_column("Kurzinfo")
    table.add_column("Warum")
    table.add_column("Ablage", style="green")
    table.add_column("Datum", style="dim")

    for item in results:
        table.add_row(
            str(item["id"]),
            (item.get("display_title") or item.get("destination_name") or "")[:40],
            item["category"],
            (item["summary"] or "")[:60],
            (item.get("match_reason") or "")[:50],
            item["route_name"],
            item["created_at"][:10],
        )

    console.print(table)


def register(app: typer.Typer) -> None:
    """Register search commands."""
    app.command()(search)
