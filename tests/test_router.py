"""Tests for the routing engine."""

from pathlib import Path
from unittest.mock import patch

import pytest

from lotse.core.classifier import Classification
from lotse.core.config import RouteConfig
from lotse.core.router import Router, _build_filename


@pytest.fixture
def router(tmp_path: Path) -> Router:
    routes = {
        "archiv": RouteConfig(
            type="folder",
            path=str(tmp_path / "archiv"),
            categories=["rechnung", "vertrag"],
            confidence_threshold=0.7,
        ),
        "artikel": RouteConfig(
            type="folder",
            path=str(tmp_path / "artikel"),
            categories=["artikel", "tutorial"],
            confidence_threshold=0.5,
        ),
    }
    review_dir = tmp_path / "review"
    return Router(routes, review_dir)


@pytest.fixture
def router_no_rename(tmp_path: Path) -> Router:
    routes = {
        "archiv": RouteConfig(
            type="folder",
            path=str(tmp_path / "archiv"),
            categories=["rechnung"],
            confidence_threshold=0.7,
            rename=False,
        ),
    }
    return Router(routes, tmp_path / "review")


def test_route_to_matching_folder(router: Router, tmp_path: Path) -> None:
    source = tmp_path / "invoice.pdf"
    source.write_text("test content")

    classification = Classification(
        category="rechnung",
        confidence=0.9,
        summary="Test invoice",
        tags=["test"],
        language="de",
        suggested_filename="Rechnung Telekom März",
    )

    result = router.execute(source, classification)
    assert result.success
    assert result.route_name == "archiv"
    assert not source.exists()  # File was moved


def test_route_to_review_on_low_confidence(router: Router, tmp_path: Path) -> None:
    source = tmp_path / "unclear.pdf"
    source.write_text("test content")

    classification = Classification(
        category="rechnung",
        confidence=0.3,  # Below threshold
        summary="Unclear document",
        tags=[],
        language="de",
    )

    result = router.execute(source, classification)
    assert result.success
    assert result.route_name == "__review__"


def test_route_to_review_on_unknown_category(router: Router, tmp_path: Path) -> None:
    source = tmp_path / "mystery.pdf"
    source.write_text("test content")

    classification = Classification(
        category="unknown_type",
        confidence=0.95,
        summary="Unknown type",
        tags=[],
        language="en",
    )

    result = router.execute(source, classification)
    assert result.success
    assert result.route_name == "__review__"


def test_handles_name_collision(router: Router, tmp_path: Path) -> None:
    archiv_dir = tmp_path / "archiv"
    archiv_dir.mkdir(parents=True)
    (archiv_dir / "invoice.pdf").write_text("existing")

    source = tmp_path / "invoice.pdf"
    source.write_text("new content")

    classification = Classification(
        category="rechnung",
        confidence=0.9,
        summary="Another invoice",
        tags=[],
        language="de",
    )

    result = router.execute(source, classification)
    assert result.success
    assert "_1.pdf" in result.destination


# --- Smart Rename Tests ---


@patch("lotse.core.router.date")
def test_rename_builds_correct_filename(mock_date: object, router: Router, tmp_path: Path) -> None:
    from datetime import date as real_date

    mock_date.today.return_value = real_date(2026, 3, 23)  # type: ignore[attr-defined]
    mock_date.side_effect = lambda *args, **kw: real_date(*args, **kw)  # type: ignore[attr-defined]

    source = tmp_path / "Screenshot 2026-03-23 um 14.23.45.png"
    source.write_text("test content")

    classification = Classification(
        category="rechnung",
        confidence=0.9,
        summary="Telekom Monatsabrechnung",
        tags=["telekom"],
        language="de",
        suggested_filename="Rechnung Telekom März",
    )

    result = router.execute(source, classification)
    assert result.success
    assert "23.03.2026 Rechnung Telekom März.png" in result.destination


def test_rename_disabled_keeps_original_name(router_no_rename: Router, tmp_path: Path) -> None:
    source = tmp_path / "invoice.pdf"
    source.write_text("test content")

    classification = Classification(
        category="rechnung",
        confidence=0.9,
        summary="Test",
        tags=[],
        language="de",
        suggested_filename="Rechnung Telekom",
    )

    result = router_no_rename.execute(source, classification)
    assert result.success
    assert "invoice.pdf" in result.destination


def test_rename_without_suggested_filename_keeps_original(router: Router, tmp_path: Path) -> None:
    source = tmp_path / "invoice.pdf"
    source.write_text("test content")

    classification = Classification(
        category="rechnung",
        confidence=0.9,
        summary="Test",
        tags=[],
        language="de",
        suggested_filename="",
    )

    result = router.execute(source, classification)
    assert result.success
    assert "invoice.pdf" in result.destination


@patch("lotse.core.router.date")
def test_build_filename_strips_unsafe_chars(mock_date: object) -> None:
    from datetime import date as real_date

    mock_date.today.return_value = real_date(2026, 3, 23)  # type: ignore[attr-defined]

    c = Classification(
        category="rechnung",
        confidence=0.9,
        summary="",
        tags=[],
        language="de",
        suggested_filename='Rechnung: Telekom / März "2026"',
    )
    result = _build_filename(c, ".pdf")
    assert "23.03.2026" in result
    assert "Rechnung" in result
    assert "Telekom" in result
    assert ":" not in result
    assert '"' not in result
    assert "/" not in result


@patch("lotse.core.router.date")
def test_build_filename_preserves_umlauts(mock_date: object) -> None:
    from datetime import date as real_date

    mock_date.today.return_value = real_date(2026, 3, 23)  # type: ignore[attr-defined]

    c = Classification(
        category="vertrag",
        confidence=0.9,
        summary="",
        tags=[],
        language="de",
        suggested_filename="Mietvertrag Hauptstraße Würzburg",
    )
    result = _build_filename(c, ".pdf")
    assert "ä" in result or "ü" in result or "ß" in result
    assert "23.03.2026" in result


@patch("lotse.core.router.date")
def test_build_filename_removes_extension_from_llm(mock_date: object) -> None:
    from datetime import date as real_date

    mock_date.today.return_value = real_date(2026, 3, 23)  # type: ignore[attr-defined]

    c = Classification(
        category="rechnung",
        confidence=0.9,
        summary="",
        tags=[],
        language="de",
        suggested_filename="Rechnung Telekom.pdf",
    )
    result = _build_filename(c, ".pdf")
    assert result == "23.03.2026 Rechnung Telekom.pdf"
    assert ".pdf.pdf" not in result


@patch("lotse.core.router.date")
def test_build_filename_fallback_to_category(mock_date: object) -> None:
    from datetime import date as real_date

    mock_date.today.return_value = real_date(2026, 3, 23)  # type: ignore[attr-defined]

    c = Classification(
        category="rechnung",
        confidence=0.9,
        summary="",
        tags=[],
        language="de",
        suggested_filename="   ",  # Only whitespace
    )
    result = _build_filename(c, ".pdf")
    assert result == "23.03.2026 Rechnung.pdf"


@patch("lotse.core.router.date")
def test_build_filename_keeps_dates_intact(mock_date: object) -> None:
    """Dots in dates like 20.03.2026 must NOT be treated as file extensions."""
    from datetime import date as real_date

    mock_date.today.return_value = real_date(2026, 3, 23)  # type: ignore[attr-defined]

    c = Classification(
        category="notiz",
        confidence=0.9,
        summary="",
        tags=[],
        language="de",
        suggested_filename="Teammeeting 20.03.2026",
    )
    result = _build_filename(c, ".txt")
    assert result == "23.03.2026 Teammeeting 20.03.2026.txt"
    assert "20.03.2026" in result


@patch("lotse.core.router.date")
def test_build_filename_replaces_underscores(mock_date: object) -> None:
    """LLM sometimes uses underscores despite instructions — fix them."""
    from datetime import date as real_date

    mock_date.today.return_value = real_date(2026, 3, 23)  # type: ignore[attr-defined]

    c = Classification(
        category="rechnung",
        confidence=0.9,
        summary="",
        tags=[],
        language="de",
        suggested_filename="telekom_rechnung_märz",
    )
    result = _build_filename(c, ".txt")
    assert "_" not in result
    assert "telekom rechnung märz" in result
