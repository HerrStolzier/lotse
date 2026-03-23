"""Tests for OCR text extraction."""

from __future__ import annotations

from pathlib import Path

from arkiv.core.ocr import (
    IMAGE_EXTENSIONS,
    PDF_EXTENSIONS,
    is_ocr_candidate,
    ocr_available,
)


def test_is_ocr_candidate_pdf(tmp_path: Path) -> None:
    pdf = tmp_path / "test.pdf"
    pdf.touch()
    assert is_ocr_candidate(pdf)


def test_is_ocr_candidate_images(tmp_path: Path) -> None:
    for ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]:
        img = tmp_path / f"test{ext}"
        img.touch()
        assert is_ocr_candidate(img), f"Should be OCR candidate: {ext}"


def test_is_not_ocr_candidate(tmp_path: Path) -> None:
    for ext in [".txt", ".md", ".json", ".csv"]:
        f = tmp_path / f"test{ext}"
        f.touch()
        assert not is_ocr_candidate(f), f"Should NOT be OCR candidate: {ext}"


def test_ocr_available_returns_dict() -> None:
    result = ocr_available()
    assert isinstance(result, dict)
    assert "pymupdf" in result
    assert "pytesseract" in result
    assert "tesseract_bin" in result


def test_extension_sets_are_disjoint() -> None:
    """PDF and image extensions should not overlap."""
    assert PDF_EXTENSIONS.isdisjoint(IMAGE_EXTENSIONS)
