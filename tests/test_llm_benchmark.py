"""Tests for Kurier's LLM benchmark machinery."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from arkiv.cli import app
from arkiv.evals.llm_benchmark import (
    _score_ranking,
    credentials_available,
    default_models,
    load_json_fixture,
    parse_model_spec,
    run_retrieval_eval,
)

runner = CliRunner()


def test_parse_model_spec_keeps_huggingface_model_suffix() -> None:
    spec = parse_model_spec("huggingface:openai/gpt-oss-20b:fastest")

    assert spec.provider == "huggingface"
    assert spec.model == "openai/gpt-oss-20b:fastest"
    assert spec.label == "huggingface:openai/gpt-oss-20b:fastest"


def test_huggingface_credentials_require_hf_token(monkeypatch) -> None:
    monkeypatch.delenv("HF_TOKEN", raising=False)
    assert credentials_available(parse_model_spec("huggingface:openai/gpt-oss-20b")) is False

    monkeypatch.setenv("HF_TOKEN", "hf-test-token")
    assert credentials_available(parse_model_spec("huggingface:openai/gpt-oss-20b")) is True


def test_default_models_keep_paid_cloud_providers_opt_in(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "present-but-no-credit")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "present-but-no-credit")

    models = default_models()

    assert "baseline" in models
    assert any(model.startswith("ollama:") for model in models)
    assert not any(model.startswith(("openai:", "anthropic:")) for model in models)


def test_classifier_benchmark_fixture_shape() -> None:
    cases = load_json_fixture(Path("tests/fixtures/classifier_benchmark.json"))

    assert len(cases) >= 3
    for case in cases:
        assert case["content"]
        assert case["expected"]["category"]
        assert isinstance(case["expected"]["filename_must_include"], list)


def test_score_ranking_calculates_topk_and_mrr() -> None:
    results = [
        {"original_path": "fixture://doc_a"},
        {"original_path": "fixture://doc_b"},
        {"original_path": "fixture://doc_c"},
    ]

    assert _score_ranking(results, "doc_b") == (0.0, 1.0, 0.5)
    assert _score_ranking(results, "doc_missing") == (0.0, 0.0, 0.0)


def test_retrieval_baseline_runs_against_fixture() -> None:
    summary, details = run_retrieval_eval(parse_model_spec("baseline"))

    assert summary.task == "retrieval"
    assert summary.status == "ok"
    assert summary.cases >= 3
    assert summary.top3 is not None
    assert details
    assert details[0].task == "retrieval"


def test_eval_llm_dry_run_lists_tasks_and_models() -> None:
    result = runner.invoke(
        app,
        [
            "eval",
            "llm",
            "--all",
            "--models",
            "baseline",
            "--models",
            "huggingface:openai/gpt-oss-20b:fastest",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Kurier Modell-Test: Probelauf" in result.stdout
    assert "Dokumente erkennen" in result.stdout
    assert "Suchanfragen verstehen" in result.stdout
    assert "Richtige Treffer" in result.stdout
    assert "huggingface:openai/gpt-oss-20b:fastest" in result.stdout


def test_eval_llm_command_writes_report_with_mocked_runner(tmp_path: Path) -> None:
    report = MagicMock()
    report.results = []

    with (
        patch("arkiv.commands.eval.run_benchmark", return_value=report),
        patch("arkiv.commands.eval.write_report", return_value=tmp_path / "report.json") as write,
    ):
        result = runner.invoke(app, ["eval", "llm", "--models", "baseline"])

    assert result.exit_code == 0
    assert "Ausführlicher Bericht gespeichert" in result.stdout
    write.assert_called_once()
