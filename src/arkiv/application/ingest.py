"""Shared ingest workflows."""

from __future__ import annotations

from pathlib import Path

from arkiv.application.context import AppContext
from arkiv.core.router import RouteResult


def ingest_file(ctx: AppContext, file_path: Path) -> RouteResult:
    """Ingest a file through the shared application context."""
    return ctx.engine.ingest_file(file_path)


def ingest_text(ctx: AppContext, text: str, name: str = "text_input") -> RouteResult:
    """Ingest text through the shared application context."""
    return ctx.engine.ingest_text(text, name=name)
