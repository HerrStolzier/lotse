"""Local beta feedback helpers."""

from __future__ import annotations

from typing import Any

from arkiv.application import AppContext

PRIORITY_RULES = {
    "upload_failed": (
        1,
        "Import-Vertrauen prüfen",
        "Uploads schlagen fehl. Prüfe Dateitypen, Fehlermeldungen und nächste Schritte.",
    ),
    "category_corrected": (
        2,
        "Einordnung verbessern",
        "Kategorien werden korrigiert. Prüfe Prompts, Kategorienamen und Review-Tempo.",
    ),
    "low_confidence_review": (
        3,
        "Review-Reibung senken",
        "Viele Dokumente landen unsicher. Prüfe Rückmeldung und Kategorienschärfe.",
    ),
    "search_no_results": (
        4,
        "Suche verständlicher machen",
        "Suchen bleiben ohne Treffer. Prüfe Suchsignale, Treffergründe und Hinweise.",
    ),
    "manual_feedback": (
        5,
        "Manuelles Feedback auswerten",
        "Es gibt Nutzerfrust. Lies die letzten Hinweise und leite konkrete UX-Aufgaben ab.",
    ),
    "classification_confirmed": (
        6,
        "Positive Review-Signale nutzen",
        "Einordnungen werden bestätigt. Nutze diese Fälle als gute Kategoriebeispiele.",
    ),
}


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
    summary = ctx.engine.store.beta_event_summary(days=days)
    events = ctx.engine.store.recent_beta_events(limit=limit)
    return {
        "summary": summary,
        "events": events,
        "recommendations": recommend_beta_actions(summary["by_type"]),
    }


def recommend_beta_actions(summary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Turn beta event counts into concrete product-hardening actions."""
    recommendations = []
    for row in summary_rows:
        event_type = str(row["event_type"])
        count = int(row["count"])
        rank, title, action = PRIORITY_RULES.get(
            event_type,
            (
                99,
                "Unbekanntes Signal prüfen",
                "Dieses Signal ist noch nicht klassifiziert. Prüfe die neue Produktfrage.",
            ),
        )
        recommendations.append(
            {
                "rank": rank,
                "event_type": event_type,
                "title": title,
                "action": action,
                "count": count,
            }
        )

    return sorted(recommendations, key=lambda item: (item["rank"], -item["count"], item["title"]))
