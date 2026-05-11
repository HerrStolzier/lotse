"""Tests for direct LLM provider routing."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from arkiv.core.llm import _detect_provider, completion


def test_detect_provider_recognizes_huggingface_prefix() -> None:
    assert _detect_provider("huggingface:openai/gpt-oss-20b", None) == "huggingface"
    assert _detect_provider("huggingface/openai/gpt-oss-20b:fastest", None) == "huggingface"


def test_huggingface_uses_router_default_and_hf_token(monkeypatch) -> None:
    monkeypatch.setenv("HF_TOKEN", "hf-test-token")
    response = MagicMock()
    response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
    response.raise_for_status.return_value = None

    with patch("arkiv.core.llm.httpx.post", return_value=response) as post:
        result = completion(
            model="huggingface/openai/gpt-oss-20b:fastest",
            messages=[{"role": "user", "content": "Hello"}],
        )

    assert result.choices[0].message.content == "ok"
    url = post.call_args.args[0]
    headers = post.call_args.kwargs["headers"]
    body = post.call_args.kwargs["json"]
    assert url == "https://router.huggingface.co/v1/chat/completions"
    assert headers["Authorization"] == "Bearer hf-test-token"
    assert body["model"] == "openai/gpt-oss-20b:fastest"
