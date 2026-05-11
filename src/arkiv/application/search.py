"""Shared search workflows."""

from __future__ import annotations

from typing import Any

from arkiv.application.context import AppContext
from arkiv.core.search_assistant import QueryAssist


def search_items(
    ctx: AppContext,
    query: str,
    *,
    limit: int = 20,
    mode: str = "auto",
    memory: bool = False,
) -> tuple[list[dict[str, Any]], QueryAssist | None]:
    """Search items through the shared application context."""
    return ctx.engine.search_with_assist(query, limit=limit, mode=mode, memory=memory)
