"""Tests for webhook payload formatting."""

from __future__ import annotations

from lotse_webhook import _format_payload


def test_slack_format() -> None:
    url = "https://hooks.slack.com/services/T123/B456/xxx"
    item = {
        "category": "rechnung",
        "confidence": 0.95,
        "summary": "Telekom Rechnung März 2026",
        "tags": ["telekom", "rechnung"],
    }

    payload = _format_payload(url, item)
    assert "blocks" in payload
    text = payload["blocks"][0]["text"]["text"]
    assert "Telekom Rechnung" in text
    assert "`rechnung`" in text


def test_discord_format() -> None:
    url = "https://discord.com/api/webhooks/123/abc"
    item = {
        "category": "artikel",
        "confidence": 0.8,
        "summary": "Python async patterns",
        "tags": ["python"],
    }

    payload = _format_payload(url, item)
    assert "embeds" in payload
    assert payload["embeds"][0]["description"] == "Python async patterns"


def test_generic_format() -> None:
    url = "https://my-api.example.com/webhook"
    item = {"category": "notiz", "confidence": 0.7, "summary": "A note"}

    payload = _format_payload(url, item)
    assert payload["event"] == "item_routed"
    assert payload["item"]["category"] == "notiz"
    assert "timestamp" in payload
