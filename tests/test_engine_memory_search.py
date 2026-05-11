"""Tests for memory-search fusion and filter-aware reranking."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from arkiv.core.config import ArkivConfig
from arkiv.core.engine import Engine
from arkiv.core.search_assistant import QueryAssist


def test_memory_search_boosts_filter_matches(tmp_path: Path) -> None:
    config = ArkivConfig(
        database={"path": tmp_path / "test.db"},
        inbox_dir=tmp_path / "inbox",
        review_dir=tmp_path / "review",
    )
    engine = Engine(config)

    base_results = [
        {
            "id": 1,
            "display_title": "Dokument Eins",
            "destination_name": "scan-001.pdf",
            "summary": "Allgemeines Schreiben",
            "tags": '["brief"]',
            "category": "brief",
            "original_path": "/tmp/scan-001.pdf",
            "route_name": "archiv",
            "created_at": "2026-04-09T10:00:00+00:00",
        },
        {
            "id": 2,
            "display_title": "Rechnung Telekom März 2026",
            "destination_name": "telekom-rechnung.pdf",
            "summary": "Mobilfunkrechnung der Telekom",
            "tags": '["telekom","rechnung"]',
            "category": "rechnung",
            "original_path": "/tmp/scan-002.pdf",
            "route_name": "archiv",
            "created_at": "2026-04-09T10:00:00+00:00",
        },
    ]
    assist = QueryAssist(
        rewrites=["Telekom Rechnung März 2026"],
        filters={"category": ["rechnung"], "organizations": ["Telekom"]},
        notes="",
        raw="",
    )

    with patch.object(engine, "_search_single_query", return_value=base_results):
        results = engine._search_multi_query(
            ["Internetanbieter Frühling", "Telekom Rechnung März 2026"],
            limit=5,
            mode="fts",
            assist=assist,
        )

    assert results[0]["id"] == 2
    assert "kategorie: rechnung" in [hit.casefold() for hit in results[0]["matched_filters"]]


def test_memory_search_matches_location_filter_alias(tmp_path: Path) -> None:
    config = ArkivConfig(
        database={"path": tmp_path / "test.db"},
        inbox_dir=tmp_path / "inbox",
        review_dir=tmp_path / "review",
    )
    engine = Engine(config)
    item = {
        "id": 1,
        "display_title": "Mietvertrag Wohnung Wuerzburg",
        "destination_name": "mietvertrag.pdf",
        "summary": "Mietvertrag fuer eine Wohnung in Wuerzburg",
        "tags": '["mietvertrag","wuerzburg"]',
        "category": "vertrag",
        "original_path": "/tmp/mietvertrag.pdf",
    }
    assist = QueryAssist(
        rewrites=["Mietvertrag Würzburg"],
        filters={"locations": ["Wuerzburg"]},
        notes="",
        raw="",
    )

    hits = engine._match_assist_filters(item, assist)

    assert "Ort: Wuerzburg" in hits


def test_search_results_receive_match_reason(tmp_path: Path) -> None:
    config = ArkivConfig(
        database={"path": tmp_path / "test.db"},
        inbox_dir=tmp_path / "inbox",
        review_dir=tmp_path / "review",
    )
    engine = Engine(config)
    assist = QueryAssist(
        rewrites=["Telekom Rechnung März 2026"],
        filters={"category": ["rechnung"], "organizations": ["Telekom"]},
        notes="",
        raw="",
    )

    with (
        patch.object(engine.query_assistant, "assist", return_value=assist),
        patch.object(
            engine,
            "_search_single_query",
            return_value=[
                {
                    "id": 2,
                    "display_title": "Rechnung Telekom März 2026",
                    "destination_name": "telekom-rechnung.pdf",
                    "summary": "Mobilfunkrechnung der Telekom",
                    "tags": '["telekom","rechnung"]',
                    "category": "rechnung",
                    "original_path": "/tmp/scan-002.pdf",
                    "route_name": "archiv",
                    "created_at": "2026-04-09T10:00:00+00:00",
                }
            ],
        ),
    ):
        results, _ = engine.search_with_assist(
            "Internetanbieter Frühling",
            limit=5,
            mode="fts",
            memory=True,
        )

    assert len(results) == 1
    assert results[0]["match_reason"].startswith("Passt wegen")
