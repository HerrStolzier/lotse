"""Service-related CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from arkiv.commands.common import console, get_config

service_app = typer.Typer(name="service", help="Automatische Sortierung verwalten.")


@service_app.command("on")
def service_on(
    config: Path | None = typer.Option(None, "--config", "-c"),
) -> None:
    """Automatische Sortierung starten."""
    from arkiv import service

    success, msg = service.install()
    if success:
        console.print("[green]✓[/green] Automatische Sortierung ist eingeschaltet.")
        console.print(f"[dim]{msg}[/dim]")
        cfg = get_config(config)
        console.print(f"[dim]Kurier beobachtet jetzt diesen Eingang: {cfg.inbox_dir}[/dim]")
        console.print("[dim]Neue Dateien werden ab jetzt automatisch verarbeitet.[/dim]")
    else:
        console.print(f"[yellow]{msg}[/yellow]")


@service_app.command("off")
def service_off() -> None:
    """Automatische Sortierung stoppen."""
    from arkiv import service

    success, msg = service.uninstall()
    if success:
        console.print("[green]✓[/green] Automatische Sortierung ist ausgeschaltet.")
        console.print(f"[dim]{msg}[/dim]")
    else:
        console.print(f"[yellow]{msg}[/yellow]")


@service_app.command("status")
def service_status(
    config: Path | None = typer.Option(None, "--config", "-c"),
) -> None:
    """Zeigen, ob die automatische Sortierung läuft."""
    from arkiv import service

    info = service.status()

    table = Table(title="Kurier Auto-Sortierung", show_header=False, border_style="dim")
    table.add_column("Feld", style="dim", width=12)
    table.add_column("Wert")

    running = info.get("running", False)
    pid = info.get("pid")
    if running and pid:
        status_str = f"[green]✓ Läuft[/green] (Prozess {pid})"
    else:
        status_str = "[yellow]Ausgeschaltet[/yellow]"

    table.add_row("Zustand", status_str)

    cfg = get_config(config)
    table.add_row("Eingang", str(cfg.inbox_dir))

    log_path = info.get("log_path", "")
    table.add_row("Protokoll", str(log_path) if log_path else "[dim]nicht verfügbar[/dim]")

    console.print(table)

    if log_path:
        log_file = Path(str(log_path))
        if log_file.exists():
            lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
            last_lines = lines[-5:] if len(lines) >= 5 else lines
            if last_lines:
                console.print("\n[dim]Letzte technische Meldungen:[/dim]")
                for line in last_lines:
                    console.print(f"[dim]{line}[/dim]")


def register(app: typer.Typer) -> None:
    """Register the service sub-app."""
    app.add_typer(service_app)
