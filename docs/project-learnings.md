# Project Learnings

## Overview

Durable learnings from recent `kurier` work. Keep this file for practical caveats that should survive beyond a single session.

## Stable Learnings

- `src/arkiv/core/llm.py` is the canonical integration point for Ollama, OpenAI-compatible, and Anthropic chat calls. Keep provider logic there instead of adding wrapper dependencies back.
- Pluggy hook calls return lists. When a hook is unimplemented, preserve the original content instead of treating an empty result like a replacement value.
- Memory search quality improves when human-facing fields such as suggested filenames, destination names, and display titles are stored and indexed alongside the core content. A readable `match_reason` also makes retrieval behavior easier to trust and debug.
- A manual review correction is not complete until the item is marked as confirmed. If the category changes without confirming confidence, the entry can fall back into the review queue on the next refresh.
- User-facing validation and benchmark output must read like product language, not developer commands. Internals such as `uv run ruff check src/ tests/`, `mypy`, or raw pytest summaries are useful for contributors, but the finished Kurier UI/CLI should translate them into plain results such as "Code-Qualität geprüft", "Typprüfung bestanden", and "Alle automatischen Tests erfolgreich".
- Plan a dedicated UX polish pass after the core flows are technically stable. The goal is to make Kurier feel understandable for "Otto Normalverbraucher": fewer raw implementation terms, clearer status messages, calmer error explanations, and guided next steps instead of command-shaped output.

## Workflow Gotchas

- Mocked tests can miss real provider and plugin wiring bugs. After touching classification or routing flow, run at least one smoke test against a real provider.
- `mypy` is strict enough to catch integration details that unit tests may gloss over, especially around subprocess text handling and typed dict shapes.

## Infra / Deploy Notes

- GitHub Actions should use the same editable install path as local development so CI and README do not drift apart.
- The repo-level secret scan is worth treating as permanent CI baseline, not a one-off hardening task. The useful shape is: PR + `main` push + manual dispatch, least-privilege permissions, pinned action revisions, full-history checkout, and no noisy PR comments by default.
- For packaging or CLI changes, a green local dev environment is not enough on its own. Fresh editable-install and wheel-install smoke tests catch first-run problems that normal in-place checks can miss.
- Local network has two Raspberry Pi nodes relevant for Kurier/n8n testing:
  - `n8n-pi.local` / `192.168.178.75` is the current n8n node. SSH is open on `22`; n8n runs via Docker Compose in `/opt/n8n` and responds on `http://n8n-pi.local:5678/`.
  - n8n workflow `Kurier Intake` is published for the first smoke path. It accepts `POST http://n8n-pi.local:5678/webhook/kurier` and responds with JSON containing `ok: true`, `service: "kurier-intake"`, and `receivedAt`.
  - Local Kurier config at `~/.config/kurier/config.toml` includes `[routes.n8n]` as a webhook catch-all (`categories = []`, `confidence_threshold = 0.3`) pointing to `http://n8n-pi.local:5678/webhook/kurier`.
  - n8n API access is available with the local key stored outside the repo at `~/.config/kurier/n8n-api-key`. Do not commit or print this key; use it as `X-N8N-API-KEY` for `http://n8n-pi.local:5678/api/v1/...`.
  - `192.168.178.110` is the likely Bitcoin node and not the Kurier/n8n target. SSH is open on `22`; Bitcoin/Electrum-like ports observed include `8332`, `8333`, and `50001`.
