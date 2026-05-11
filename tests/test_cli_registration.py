"""Tests for modular CLI command registration."""

from __future__ import annotations

import typer
from typer.testing import CliRunner

runner = CliRunner()


def test_register_commands_populates_root_and_service_commands() -> None:
    from arkiv.commands import register_commands

    app = typer.Typer()
    register_commands(app)

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    for command_name in (
        "add",
        "watch",
        "import-email",
        "fetch-email",
        "search",
        "status",
        "init",
        "doctor",
        "audit",
        "serve",
        "plugins",
        "undo",
        "export",
        "tui",
        "service",
    ):
        assert command_name in result.stdout
