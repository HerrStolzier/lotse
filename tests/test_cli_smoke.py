"""Characterization tests for the Kurier CLI surface."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from arkiv.cli import app

runner = CliRunner()


def _write_config(config_path: Path, db_path: Path, inbox_dir: Path, review_dir: Path) -> None:
    config_path.write_text(
        "\n".join(
            [
                "[llm]",
                'provider = "ollama"',
                'model = "qwen2.5:7b"',
                'base_url = "http://localhost:11434"',
                "",
                "[database]",
                f'path = "{db_path}"',
                "",
                f'inbox_dir = "{inbox_dir}"',
                f'review_dir = "{review_dir}"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_help_lists_expected_primary_commands() -> None:
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
        "eval",
        "serve",
        "plugins",
        "undo",
        "export",
        "tui",
        "service",
    ):
        assert command_name in result.stdout


def test_version_flag_prints_version_and_exits_cleanly() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "kurier" in result.stdout.lower()


def test_status_reports_empty_database_without_crashing(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    db_path = tmp_path / "state" / "kurier.db"
    inbox_dir = tmp_path / "inbox"
    review_dir = tmp_path / "review"
    _write_config(config_path, db_path, inbox_dir, review_dir)

    result = runner.invoke(app, ["status", "--config", str(config_path)])

    assert result.exit_code == 0
    assert "Kurier" in result.stdout
    assert "Noch keine Dokumente verarbeitet." in result.stdout
    assert "Ablage-Daten:" in result.stdout
    assert db_path.name in result.stdout


def test_doctor_reports_missing_config_file(tmp_path: Path) -> None:
    missing_config = tmp_path / "missing.toml"

    result = runner.invoke(app, ["doctor", "--config", str(missing_config)])

    assert result.exit_code == 0
    assert "Kurier Gesundheitscheck" in result.stdout
    assert "Einstellungen" in result.stdout
    assert "Nicht gefunden" in result.stdout


def test_plugins_reports_empty_state_without_error(monkeypatch) -> None:
    class DummyPluginManager:
        def list_plugins(self) -> list[str]:
            return []

    monkeypatch.setattr("arkiv.plugins.manager.PluginManager", DummyPluginManager)

    result = runner.invoke(app, ["plugins"])

    assert result.exit_code == 0
    assert "Keine Erweiterungen installiert." in result.stdout


def test_search_help_uses_user_facing_language() -> None:
    result = runner.invoke(app, ["search", "--help"])

    assert result.exit_code == 0
    assert "Suchfrage in normaler Sprache" in result.stdout
    assert "Lasse Kurier unklare Suchfragen lokal verbessern" in result.stdout
