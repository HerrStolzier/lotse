"""Local beta feedback helpers."""

from __future__ import annotations

from typing import Any

from arkiv.application import AppContext


def record_beta_event(
    ctx: AppContext,
    event_type: str,
    message: str,
    *,
    severity: str = "info",
    context: dict[str, Any] | None = None,
    item_id: int | None = None,
) -> int:
    """Record a local beta signal without sending anything outside the device."""
    return ctx.engine.store.record_beta_event(
        event_type,
        message,
        severity=severity,
        context=context,
        item_id=item_id,
    )


def get_beta_events(ctx: AppContext, limit: int = 50) -> list[dict[str, Any]]:
    """Return recent local beta signals."""
    return ctx.engine.store.recent_beta_events(limit=limit)


def get_beta_report(ctx: AppContext, *, days: int = 7, limit: int = 50) -> dict[str, Any]:
    """Return a compact report with summary and recent signals."""
    return {
        "summary": ctx.engine.store.beta_event_summary(days=days),
        "events": ctx.engine.store.recent_beta_events(limit=limit),
    }
