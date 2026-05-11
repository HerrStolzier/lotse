"""Shared review-queue workflows."""

from __future__ import annotations

from typing import Any

from arkiv.application.context import AppContext


def get_review_items(
    ctx: AppContext,
    *,
    threshold: float = 0.6,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Return low-confidence items for review."""
    return ctx.engine.store.low_confidence(threshold=threshold, limit=limit)


def correct_review_item(ctx: AppContext, item_id: int, category: str) -> None:
    """Correct an item's category and mark it confirmed."""
    ctx.engine.store.update_category(item_id, category.strip())


def confirm_review_item(ctx: AppContext, item_id: int) -> None:
    """Confirm an item's current classification."""
    ctx.engine.store.confirm_classification(item_id)
