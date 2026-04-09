"""Tests for the lightweight AI search benchmark harness."""

from __future__ import annotations

import json

from arkiv.evals.ai_search_benchmark import (
    evaluate_raw_output,
    load_benchmark_cases,
    parse_model_output,
)


def test_load_benchmark_cases_reads_fixture() -> None:
    cases = load_benchmark_cases()
    assert len(cases) >= 10
    assert len({case.id for case in cases}) == len(cases)


def test_parse_model_output_handles_markdown_wrapped_json() -> None:
    raw = """```json
    {
      "rewrites": ["Telekom Rechnung Fruehling 2026", "Internetrechnung Telekom 2026"],
      "filters": {"category": ["rechnung"], "organizations": ["Telekom"]},
      "notes": "Rechnung eines Telekommunikationsanbieters."
    }
    ```"""

    parsed = parse_model_output(raw)
    assert parsed.rewrites[0] == "Telekom Rechnung Fruehling 2026"
    assert parsed.filters["category"] == ["rechnung"]


def test_evaluate_raw_output_scores_perfectish_output() -> None:
    case = load_benchmark_cases()[0]
    raw = json.dumps(
        {
            "rewrites": case.expected.rewrites,
            "filters": case.expected.filters,
            "notes": case.expected.notes,
        }
    )

    result = evaluate_raw_output(case, raw, elapsed_ms=12.5)
    assert result.json_valid is True
    assert result.overall_score == 1.0
    assert result.elapsed_ms == 12.5


def test_evaluate_raw_output_returns_zero_score_for_invalid_json() -> None:
    case = load_benchmark_cases()[0]
    result = evaluate_raw_output(case, "not-json")

    assert result.json_valid is False
    assert result.overall_score == 0.0
    assert result.error is not None
