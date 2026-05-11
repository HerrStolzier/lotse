"""Export-related CLI commands."""

from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from arkiv.commands.common import console, get_config


def export(
    format: Annotated[str, typer.Option("--format", "-f", help="Output format")] = "csv",
    category: Annotated[str | None, typer.Option("--category", "-c")] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    config: Annotated[Path | None, typer.Option("--config")] = None,
) -> None:
    """Verarbeitete Einträge als CSV oder JSON exportieren."""
    from arkiv.db.store import Store

    cfg = get_config(config)

    if not cfg.database.path.exists():
        console.print("[dim]Keine verarbeiteten Einträge gefunden.[/dim]")
        raise typer.Exit(1)

    store = Store(cfg.database.path)
    items = store.get_all_items(category=category)

    if not items:
        console.print("[dim]Keine Einträge gefunden.[/dim]")
        return

    fields = [
        "id",
        "category",
        "confidence",
        "original_path",
        "destination",
        "created_at",
        "status",
    ]

    if format.lower() == "json":
        rows = [{field: item.get(field) for field in fields} for item in items]
        data = json.dumps(rows, indent=2, ensure_ascii=False)
        if output:
            output.write_text(data, encoding="utf-8")
            console.print(f"[green]✓[/green] {len(rows)} Einträge exportiert nach {output}")
        else:
            console.print(data)
    elif format.lower() == "csv":
        if output:
            f_out = output.open("w", newline="", encoding="utf-8")
        else:
            f_out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="")  # type: ignore[assignment]

        try:
            writer = csv.DictWriter(f_out, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for item in items:
                writer.writerow({field: item.get(field) for field in fields})
        finally:
            if output:
                f_out.close()

        if output:
            console.print(f"[green]✓[/green] {len(items)} Einträge exportiert nach {output}")
    else:
        console.print(f"[red]Unbekanntes Format:[/red] {format} (verwende 'csv' oder 'json')")
        raise typer.Exit(1)


def register(app: typer.Typer) -> None:
    """Register export commands."""
    app.command()(export)
