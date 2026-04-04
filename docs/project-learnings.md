# Project Learnings

## Overview

Durable learnings from recent `kurier` work. Keep this file for practical caveats that should survive beyond a single session.

## Stable Learnings

- `src/arkiv/core/llm.py` is the canonical integration point for Ollama, OpenAI-compatible, and Anthropic chat calls. Keep provider logic there instead of adding wrapper dependencies back.
- Pluggy hook calls return lists. When a hook is unimplemented, preserve the original content instead of treating an empty result like a replacement value.

## Workflow Gotchas

- Mocked tests can miss real provider and plugin wiring bugs. After touching classification or routing flow, run at least one smoke test against a real provider.
- `mypy` is strict enough to catch integration details that unit tests may gloss over, especially around subprocess text handling and typed dict shapes.

## Infra / Deploy Notes

- GitHub Actions should use the same editable install path as local development so CI and README do not drift apart.
