"""Shared CLI helpers for Kurier commands."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from arkiv import __version__
from arkiv.application import AppContext
from arkiv.core.config import DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILE, ArkivConfig

console = Console()


def get_config(config: Path | None = None) -> ArkivConfig:
    """Load configuration and ensure required directories exist."""
    cfg = ArkivConfig.load(config)
    cfg.ensure_dirs()
    return cfg


def get_context(config: Path | None = None) -> AppContext:
    """Create a shared application runtime for CLI commands."""
    return AppContext(get_config(config))


def launch_tui(config: Path | None = None) -> None:
    """Start the Textual TUI from a CLI command or callback."""
    try:
        from arkiv.tui.app import ArkivApp
    except ImportError:
        console.print("[red]Textual nicht installiert.[/red]")
        console.print("Installiere mit: pip install 'arkiv[tui]'")
        raise SystemExit(1) from None

    cfg = get_config(config)
    ArkivApp(cfg).run()


__all__ = [
    "DEFAULT_CONFIG_DIR",
    "DEFAULT_CONFIG_FILE",
    "AppContext",
    "ArkivConfig",
    "__version__",
    "console",
    "get_config",
    "get_context",
    "launch_tui",
]
