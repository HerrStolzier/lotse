"""Helpers for the AI memory-search benchmark fixture.

This module is intentionally lightweight:
- no real model execution
- no Ollama dependency
- no benchmark orchestration yet

It provides the building blocks we need for Sprint 1:
- load benchmark cases from JSON
- parse model-style JSON output robustly
- score outputs against the fixture in a reproducible way
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _default_fixture_path() -> Path:
    """Return the repo-local benchmark fixture path."""
    return Path.cwd() / "tests" / "fixtures" / "ai_search_benchmark.json"


def _normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _normalize_list(values: list[str]) -> list[str]:
    return [_normalize_text(v) for v in values if v.strip()]


@dataclass(frozen=True)
class ExpectedOutput:
    rewrites: list[str]
    filters: dict[str, list[str]]
    notes: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExpectedOutput:
        raw_filters = data.get("filters", {})
        filters: dict[str, list[str]] = {}
        if isinstance(raw_filters, dict):
            for key, value in raw_filters.items():
                if isinstance(value, list):
                    filters[str(key)] = [str(v) for v in value]

        return cls(
            rewrites=[str(v) for v in data.get("rewrites", []) if isinstance(v, str)],
            filters=filters,
            notes=str(data.get("notes", "")),
        )


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    query: str
    document_type: str
    expected: ExpectedOutput

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkCase:
        return cls(
            id=str(data["id"]),
            query=str(data["query"]),
            document_type=str(data["document_type"]),
            expected=ExpectedOutput.from_dict(data["expected"]),
        )


@dataclass(frozen=True)
class ModelOutput:
    rewrites: list[str]
    filters: dict[str, list[str]]
    notes: str
    raw: str


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    json_valid: bool
    rewrites_present: bool
    filters_present: bool
    notes_present: bool
    rewrite_coverage: float
    filter_coverage: float
    format_score: float
    overall_score: float
    elapsed_ms: float | None = None
    error: str | None = None


def load_benchmark_cases(path: Path | None = None) -> list[BenchmarkCase]:
    """Load AI search benchmark cases from JSON."""
    fixture_path = path or _default_fixture_path()
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Benchmark fixture must contain a list of cases")
    return [BenchmarkCase.from_dict(item) for item in data]


def parse_model_output(raw: str) -> ModelOutput:
    """Parse a model response expected to contain JSON.

    Accepts plain JSON or JSON wrapped in markdown code fences.
    """
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("Model output must be a JSON object")

    rewrites = parsed.get("rewrites", [])
    raw_filters = parsed.get("filters", {})
    notes = parsed.get("notes", "")

    if not isinstance(rewrites, list):
        raise ValueError("'rewrites' must be a list")
    if not isinstance(raw_filters, dict):
        raise ValueError("'filters' must be an object")
    if not isinstance(notes, str):
        raise ValueError("'notes' must be a string")

    filters: dict[str, list[str]] = {}
    for key, value in raw_filters.items():
        if isinstance(value, list):
            filters[str(key)] = [str(v) for v in value if str(v).strip()]

    return ModelOutput(
        rewrites=[str(v) for v in rewrites if isinstance(v, str) and v.strip()],
        filters=filters,
        notes=notes,
        raw=raw,
    )


def evaluate_output(
    case: BenchmarkCase,
    output: ModelOutput,
    *,
    elapsed_ms: float | None = None,
) -> EvaluationResult:
    """Score a parsed model output against a benchmark case.

    Current scoring is intentionally simple and transparent:
    - format_score rewards presence of the expected top-level fields
    - rewrite_coverage checks how many expected rewrites are matched exactly
      after light normalization
    - filter_coverage checks how many expected filter values are reproduced

    This is good enough for Sprint 1 and can later be extended with softer
    semantic matching.
    """
    expected_rewrites = set(_normalize_list(case.expected.rewrites))
    actual_rewrites = set(_normalize_list(output.rewrites))

    expected_filter_values: list[str] = []
    actual_filter_values: list[str] = []
    for values in case.expected.filters.values():
        expected_filter_values.extend(_normalize_list(values))
    for values in output.filters.values():
        actual_filter_values.extend(_normalize_list(values))

    rewrite_hits = len(expected_rewrites & actual_rewrites)
    filter_hits = len(set(expected_filter_values) & set(actual_filter_values))

    rewrite_coverage = rewrite_hits / len(expected_rewrites) if expected_rewrites else 1.0
    filter_coverage = (
        filter_hits / len(set(expected_filter_values)) if expected_filter_values else 1.0
    )

    format_parts = [
        bool(output.rewrites),
        bool(output.filters),
        bool(output.notes.strip()),
    ]
    format_score = sum(1.0 for part in format_parts if part) / len(format_parts)

    overall_score = format_score * 0.4 + rewrite_coverage * 0.35 + filter_coverage * 0.25

    return EvaluationResult(
        case_id=case.id,
        json_valid=True,
        rewrites_present=bool(output.rewrites),
        filters_present=bool(output.filters),
        notes_present=bool(output.notes.strip()),
        rewrite_coverage=rewrite_coverage,
        filter_coverage=filter_coverage,
        format_score=format_score,
        overall_score=overall_score,
        elapsed_ms=elapsed_ms,
    )


def evaluate_raw_output(
    case: BenchmarkCase,
    raw: str,
    *,
    elapsed_ms: float | None = None,
) -> EvaluationResult:
    """Parse and score a raw model response."""
    try:
        parsed = parse_model_output(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        return EvaluationResult(
            case_id=case.id,
            json_valid=False,
            rewrites_present=False,
            filters_present=False,
            notes_present=False,
            rewrite_coverage=0.0,
            filter_coverage=0.0,
            format_score=0.0,
            overall_score=0.0,
            elapsed_ms=elapsed_ms,
            error=str(exc),
        )

    return evaluate_output(case, parsed, elapsed_ms=elapsed_ms)
