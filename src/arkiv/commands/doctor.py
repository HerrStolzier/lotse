"""Doctor/diagnostics CLI commands."""

from __future__ import annotations

import json
import tomllib
import urllib.request
from pathlib import Path

import typer
from rich.table import Table

from arkiv.commands.common import DEFAULT_CONFIG_FILE, ArkivConfig, console


def _count_visible_inbox_files(inbox_dir: Path) -> int:
    from arkiv.inlets.watch import list_inbox_files

    return len(list_inbox_files(inbox_dir))


def _doctor_directory_targets(cfg: ArkivConfig) -> list[tuple[str, Path]]:
    targets = [
        ("Datenbank-Ordner", cfg.database.path.parent),
        ("Inbox", cfg.inbox_dir),
        ("Prüfen", cfg.review_dir),
    ]
    for name, route in cfg.routes.items():
        if route.path:
            targets.append((f"Route '{name}'", Path(route.path).expanduser()))
    return targets


def doctor(
    config: Path | None = typer.Option(None, "--config", "-c"),
    fix: bool = typer.Option(
        False,
        "--fix",
        help="Lege fehlende Ordner aus der Config direkt an",
    ),
) -> None:
    """Systemzustand prüfen — Config, Routen, LLM, Datenbank."""
    config_path = config or DEFAULT_CONFIG_FILE

    check_table = Table(title="Kurier Doctor", show_header=True, border_style="dim")
    check_table.add_column("Status", width=4)
    check_table.add_column("Prüfung")
    check_table.add_column("Details", style="dim")

    def ok(label: str, detail: str = "") -> None:
        check_table.add_row("[green]✓[/green]", label, detail)

    def warn(label: str, detail: str = "") -> None:
        check_table.add_row("[yellow]![/yellow]", label, detail)

    def fail(label: str, detail: str = "") -> None:
        check_table.add_row("[red]✗[/red]", label, detail)

    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                tomllib.load(f)
            ok("Config-Datei", str(config_path))
            cfg_valid = True
        except Exception as e:
            fail("Config-Datei", f"Ungültiges TOML: {e}")
            cfg_valid = False
    else:
        fail("Config-Datei", f"Nicht gefunden: {config_path}")
        cfg_valid = False

    cfg = None
    if cfg_valid:
        try:
            cfg = ArkivConfig.load(config_path)
        except Exception as e:
            fail("Config laden", str(e))
            cfg_valid = False

    if cfg is not None:
        from arkiv import service

        try:
            info = service.status()
            backlog = _count_visible_inbox_files(cfg.inbox_dir)
            review_backlog = _count_visible_inbox_files(cfg.review_dir)

            if info.get("running"):
                detail = "Hintergrunddienst läuft"
                if backlog:
                    noun = "Datei" if backlog == 1 else "Dateien"
                    detail += f"; {backlog} {noun} warten gerade im Eingang"
                ok("Auto-Sortierung", detail)
            else:
                detail = "Hintergrunddienst ist aus. Starte mit: `kurier service on`"
                if backlog:
                    noun = "Datei" if backlog == 1 else "Dateien"
                    detail += f" ({backlog} {noun} warten im Eingang)"
                warn("Auto-Sortierung", detail)

            if backlog:
                noun = "Datei" if backlog == 1 else "Dateien"
                warn("Inbox", f"{backlog} {noun} liegen im Eingang")
            else:
                ok("Inbox", "Leer")

            if review_backlog:
                noun = "Datei" if review_backlog == 1 else "Dateien"
                warn("Prüfen", f"{review_backlog} {noun} warten auf Sichtung")
            else:
                ok("Prüfen", "Leer")
        except Exception as e:
            warn("Auto-Sortierung", f"Status konnte nicht geprüft werden: {e}")

    if cfg is not None:
        for label, directory in _doctor_directory_targets(cfg):
            if directory.exists():
                ok(label, str(directory))
                continue

            if fix:
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    ok(label, f"Angelegt: {directory}")
                except OSError as e:
                    fail(label, f"Konnte nicht angelegt werden: {e}")
            else:
                warn(
                    label,
                    "Fehlt noch: "
                    f"{directory}  (beim Erststart oft normal; `kurier doctor --fix` legt es an)",
                )

    if cfg is not None:
        if cfg.llm.provider == "ollama":
            ollama_url = (cfg.llm.base_url or "http://localhost:11434").rstrip("/")
            try:
                with urllib.request.urlopen(f"{ollama_url}/api/tags", timeout=3) as resp:
                    data = json.loads(resp.read())
                    models = [m["name"] for m in data.get("models", [])]
                model_names_base = [m.split(":")[0] for m in models]
                if cfg.llm.model in models or cfg.llm.model in model_names_base:
                    ok("LLM erreichbar", f"{cfg.llm.provider}/{cfg.llm.model}")
                else:
                    available = ", ".join(models[:3]) or "-"
                    warn(
                        "LLM-Modell fehlt",
                        f"'{cfg.llm.model}' nicht gefunden. Verfügbar: {available}",
                    )
            except Exception as e:
                fail("LLM erreichbar", f"Ollama nicht erreichbar: {e}")
        else:
            ok("LLM", f"{cfg.llm.provider} (API-Key via Env-Var)")

    if cfg is not None and cfg.categories:
        empty_cats = [name for name, desc in cfg.categories.items() if not desc or not desc.strip()]
        if empty_cats:
            warn("Kategorie-Beschreibungen", f"Leer bei: {', '.join(empty_cats)}")
        else:
            ok("Kategorie-Beschreibungen", "Alle vorhanden")

    if cfg is not None and cfg.database.path.exists():
        try:
            from arkiv.db.store import Store

            store = Store(cfg.database.path)
            all_items = store.get_all_items()
            pending = sum(1 for it in all_items if it.get("status") == "pending")
            failed = sum(1 for it in all_items if it.get("status") == "failed")
            if pending or failed:
                warn(
                    "DB-Status",
                    f"{pending} ausstehend, {failed} fehlgeschlagen (von {len(all_items)} gesamt)",
                )
            else:
                ok("DB-Status", f"{len(all_items)} Einträge, keine Fehler")
        except Exception as e:
            warn("Datenbank", str(e))
    elif cfg is not None:
        ok("Datenbank", "Noch leer (kein Element verarbeitet)")

    console.print(check_table)


def register(app: typer.Typer) -> None:
    """Register doctor commands."""
    app.command()(doctor)
