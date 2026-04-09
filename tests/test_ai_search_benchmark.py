"""Tests for the AI memory-search benchmark fixture."""

from __future__ import annotations

import json
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "ai_search_benchmark.json"


def test_ai_search_benchmark_fixture_exists() -> None:
    assert FIXTURE_PATH.exists()


def test_ai_search_benchmark_fixture_has_expected_shape() -> None:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert isinstance(data, list)
    assert len(data) >= 10

    for case in data:
        assert isinstance(case["id"], str)
        assert isinstance(case["query"], str)
        assert isinstance(case["document_type"], str)

        expected = case["expected"]
        assert isinstance(expected["rewrites"], list)
        assert len(expected["rewrites"]) >= 2
        assert isinstance(expected["filters"], dict)
        assert isinstance(expected["notes"], str)

        for rewrite in expected["rewrites"]:
            assert isinstance(rewrite, str)
            assert rewrite.strip()
