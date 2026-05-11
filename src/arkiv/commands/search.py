"""Search-related CLI commands."""

from __future__ import annotations

import logging
from pathlib import Path

import typer
from rich.table import Table

from arkiv.application.search import search_items as search_items_workflow
from arkiv.commands.common import console, get_context


def search(
    query: str = typer.Argument(..., help="Search query (natural language)"),
    limit: int = typer.Option(20, "--limit", "-n"),
    mode: str = typer.Option(
        "auto",
        "--mode",
        "-m",
        help="Search mode: 'auto' (hybrid), 'fts' (keyword), 'vec' (semantic)",
    ),
    memory: bool = typer.Option(
        False,
        "--memory",
        help="Use the local LLM to rewrite vague queries before retrieval",
    ),
    config: Path | None = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Search processed items. Uses hybrid keyword + semantic search by default."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    ctx = get_context(config)
    results, assist = search_items_workflow(ctx, query, limit=limit, mode=mode, memory=memory)

    if not results:
        console.print("[dim]No results found.[/dim]")
        return

    if ctx.engine.store.vec_enabled and mode in ("auto", "vec"):
        console.print("[dim]Search mode: hybrid (keyword + semantic)[/dim]\n")
    else:
        console.print("[dim]Search mode: keyword (FTS5)[/dim]\n")

    if memory and assist and assist.rewrites:
        console.print(f"[dim]Query assist: {', '.join(assist.rewrites)}[/dim]\n")

    table = Table(title=f"Results for '{query}'")
    table.add_column("ID", style="dim")
    table.add_column("Titel", style="bold")
    table.add_column("Category", style="cyan")
    table.add_column("Summary")
    table.add_column("Warum")
    table.add_column("Route", style="green")
    table.add_column("Date", style="dim")

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
