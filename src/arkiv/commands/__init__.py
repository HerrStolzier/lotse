"""Modular CLI command registration for Kurier."""

from __future__ import annotations

import typer

from arkiv.commands import (
    audit,
    beta,
    doctor,
    email,
    eval,
    export,
    ingest,
    plugins,
    search,
    server,
    service,
    setup,
    status,
    tui,
    undo,
    webhooks,
)


def register_commands(app: typer.Typer) -> None:
    """Register all root commands and sub-apps on the given Typer app."""
    service.register(app)
    ingest.register(app)
    email.register(app)
    search.register(app)
    status.register(app)
    setup.register(app)
    doctor.register(app)
    audit.register(app)
    beta.register(app)
    eval.register(app)
    server.register(app)
    plugins.register(app)
    undo.register(app)
    export.register(app)
    webhooks.register(app)
    tui.register(app)
