"""Tests for the query-assist layer used by memory search."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from arkiv.core.config import LLMConfig
from arkiv.core.search_assistant import QueryAssistant


def _mock_completion_response(data: dict) -> MagicMock:
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message.content = json.dumps(data)
    return mock


def test_query_assistant_parses_response() -> None:
    assistant = QueryAssistant(LLMConfig(provider="ollama", model="qwen2.5:7b"))
    expected = {
        "rewrites": ["Telekom Rechnung Frühling 2026", "Internetrechnung Telekom"],
        "filters": {"category": ["rechnung"], "organizations": ["Telekom"]},
        "notes": "Der Nutzer sucht wahrscheinlich eine Telekom-Rechnung.",
    }

    with patch("arkiv.core.search_assistant.completion") as mock_llm:
        mock_llm.return_value = _mock_completion_response(expected)
        result = assistant.assist("die Internetrechnung vom Frühling")

    assert result.rewrites == expected["rewrites"]
    assert result.filters["category"] == ["rechnung"]
    assert "Telekom" in result.filters["organizations"]


def test_query_assistant_returns_empty_on_invalid_json() -> None:
    assistant = QueryAssistant(LLMConfig(provider="ollama", model="qwen2.5:7b"))

    with patch("arkiv.core.search_assistant.completion") as mock_llm:
        mock = MagicMock()
        mock.choices = [MagicMock()]
        mock.choices[0].message.content = "not json"
        mock_llm.return_value = mock
        result = assistant.assist("Krankenkasse Beitrag")

    assert result.rewrites == []
    assert result.filters == {}
    assert result.notes == ""


def test_query_assistant_queries_dedupe_original_query() -> None:
    assistant = QueryAssistant(LLMConfig(provider="ollama", model="qwen2.5:7b"))
    raw = {
        "rewrites": ["Telekom Rechnung", "telekom   rechnung", "Internetrechnung"],
        "filters": {},
        "notes": "Kurz.",
    }

    with patch("arkiv.core.search_assistant.completion") as mock_llm:
        mock_llm.return_value = _mock_completion_response(raw)
        result = assistant.assist("Telekom Rechnung")

    assert result.queries("Telekom Rechnung") == ["Telekom Rechnung", "Internetrechnung"]
