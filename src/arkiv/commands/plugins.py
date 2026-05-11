"""Plugin-related CLI commands."""

from __future__ import annotations

import typer

from arkiv.commands.common import console


def plugins() -> None:
    """List installed plugins."""
    from arkiv.plugins.manager import PluginManager

    pm = PluginManager()
    plugin_list = pm.list_plugins()

    if not plugin_list:
        console.print("[dim]No plugins installed.[/dim]")
        console.print("[dim]Install plugins with: pip install arkiv-<plugin-name>[/dim]")
        return

    for name in plugin_list:
        console.print(f"  [green]●[/green] {name}")


def register(app: typer.Typer) -> None:
    """Register plugin commands."""
    app.command()(plugins)
