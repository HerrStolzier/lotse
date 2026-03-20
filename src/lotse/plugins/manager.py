"""Plugin discovery and management."""

from __future__ import annotations

import logging
from importlib.metadata import entry_points

import pluggy

from lotse.plugins.spec import LotsePluginSpec

logger = logging.getLogger(__name__)


class PluginManager:
    """Discovers and manages Lotse plugins."""

    def __init__(self) -> None:
        self._pm = pluggy.PluginManager("lotse")
        self._pm.add_hookspecs(LotsePluginSpec)
        self._load_plugins()

    @property
    def hook(self) -> pluggy.HookRelay:
        return self._pm.hook

    def _load_plugins(self) -> None:
        """Auto-discover plugins from entry_points."""
        eps = entry_points()
        lotse_plugins = eps.select(group="lotse.plugins")

        for ep in lotse_plugins:
            try:
                plugin_module = ep.load()
                self._pm.register(plugin_module, name=ep.name)
                logger.info("Loaded plugin: %s", ep.name)
            except Exception as e:
                logger.warning("Failed to load plugin %s: %s", ep.name, e)

    def register(self, plugin: object, name: str | None = None) -> None:
        """Manually register a plugin (useful for testing)."""
        self._pm.register(plugin, name=name)

    def list_plugins(self) -> list[str]:
        """List all registered plugin names (clean, human-readable)."""
        names = []
        for item1, item2 in self._pm.list_name_plugin():
            # pluggy returns (plugin, name) or (name, plugin) depending on version
            # Detect which is the string name
            if isinstance(item2, str):
                names.append(item2)
            elif isinstance(item1, str):
                names.append(item1)
            elif hasattr(item1, "__name__"):
                names.append(item1.__name__.replace("lotse_", ""))
        return names
