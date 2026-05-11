"""Tests for hardware-aware local model helpers."""

from __future__ import annotations

from arkiv.core.hardware import (
    default_eval_ollama_model,
    model_fits_ram,
    model_min_ram_gb,
    recommended_models_for_ram,
)


def test_recommended_models_follow_detected_ram() -> None:
    assert recommended_models_for_ram(8)[0].model_id == "qwen2.5:7b"
    assert recommended_models_for_ram(4)[0].model_id == "qwen2.5:3b"


def test_default_eval_model_is_conservative() -> None:
    assert default_eval_ollama_model(4) == "qwen2.5:3b"
    assert default_eval_ollama_model(16) == "qwen2.5:7b"


def test_model_min_ram_estimates_known_and_generic_models() -> None:
    assert model_min_ram_gb("qwen2.5:14b") == 16
    assert model_min_ram_gb("ollama:qwen2.5:7b") == 8
    assert model_min_ram_gb("custom:9b") == 12


def test_model_fits_ram_reports_warning_for_oversized_model() -> None:
    fits, detail = model_fits_ram("qwen2.5:14b", 8)

    assert fits is False
    assert "16 GB" in detail
    assert "8 GB" in detail
