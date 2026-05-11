"""Tests for the shared application-layer workflows."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from arkiv.core.config import ArkivConfig


@pytest.fixture
def config(tmp_path: Path) -> ArkivConfig:
    return ArkivConfig(
        database={"path": tmp_path / "test.db"},
        inbox_dir=tmp_path / "inbox",
        review_dir=tmp_path / "review",
    )


def _classifier_response(
    *,
    category: str,
    confidence: float,
    summary: str,
    filename: str,
) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = json.dumps(
        {
            "category": category,
            "confidence": confidence,
            "summary": summary,
            "tags": [category],
            "language": "de",
            "suggested_filename": filename,
        }
    )
    return response


def test_application_context_lazily_creates_engine(config: ArkivConfig) -> None:
    from arkiv.application import AppContext

    ctx = AppContext(config)

    assert ctx.config is config
    assert ctx._engine is None

    engine = ctx.engine

    assert engine is ctx.engine
    assert ctx._engine is engine


def test_application_ingest_and_search_share_one_context(config: ArkivConfig) -> None:
    from arkiv.application import AppContext
    from arkiv.application.ingest import ingest_text
    from arkiv.application.search import search_items

    ctx = AppContext(config)

    with patch(
        "arkiv.core.classifier.completion",
        return_value=_classifier_response(
            category="rechnung",
            confidence=0.96,
            summary="Telekom Rechnung April",
            filename="Rechnung Telekom April 2026",
        ),
    ):
        result = ingest_text(ctx, "Telekom Rechnung April 2026", name="invoice")

    assert result.success is True
    assert result.route_name == "__text__"

    matches, assist = search_items(ctx, "Telekom", limit=10, mode="fts", memory=False)

    assert assist is None
    assert len(matches) >= 1
    assert matches[0]["category"] == "rechnung"
    assert matches[0]["display_title"] == "Rechnung Telekom April 2026"


def test_application_status_recent_and_review_workflows(config: ArkivConfig) -> None:
    from arkiv.application import AppContext
    from arkiv.application.ingest import ingest_text
    from arkiv.application.review import confirm_review_item, correct_review_item, get_review_items
    from arkiv.application.status import get_recent_items, get_status

    ctx = AppContext(config)

    with patch(
        "arkiv.core.classifier.completion",
        return_value=_classifier_response(
            category="brief",
            confidence=0.42,
            summary="Unsicherer Brief",
            filename="Brief Krankenkasse",
        ),
    ):
        ingest_text(ctx, "Brief von der Krankenkasse", name="letter")

    status = get_status(ctx)
    recent = get_recent_items(ctx, limit=5)
    review_items = get_review_items(ctx, threshold=0.6, limit=10)

    assert status["total_items"] == 1
    assert recent[0]["display_title"] == "Brief Krankenkasse"
    assert review_items[0]["summary"] == "Unsicherer Brief"

    item_id = review_items[0]["id"]
    correct_review_item(ctx, item_id, "versicherung")
    assert get_review_items(ctx, threshold=0.6, limit=10) == []

    with patch(
        "arkiv.core.classifier.completion",
        return_value=_classifier_response(
            category="notiz",
            confidence=0.33,
            summary="Kurze Notiz",
            filename="Kurze Notiz",
        ),
    ):
        ingest_text(ctx, "Eine kurze Notiz", name="note")

    low_confidence = get_review_items(ctx, threshold=0.6, limit=10)
    assert len(low_confidence) == 1

    confirm_review_item(ctx, low_confidence[0]["id"])
    assert get_review_items(ctx, threshold=0.6, limit=10) == []
