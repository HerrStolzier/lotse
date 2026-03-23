"""Cross-platform desktop notifications for Kurier."""

from __future__ import annotations

import logging
import platform
import subprocess

logger = logging.getLogger(__name__)


def notify(title: str, message: str) -> None:
    """Send a desktop notification. Non-blocking, best-effort."""
    system = platform.system()
    try:
        if system == "Darwin":
            _notify_macos(title, message)
        elif system == "Linux":
            _notify_linux(title, message)
        else:
            logger.debug("Benachrichtigung (kein nativer Support): %s - %s", title, message)
    except Exception as exc:
        logger.debug("Benachrichtigung fehlgeschlagen: %s", exc)


def _notify_macos(title: str, message: str) -> None:
    safe_title = title.replace('"', '\\"').replace("'", "\\'")
    safe_message = message.replace('"', '\\"').replace("'", "\\'")
    script = f'display notification "{safe_message}" with title "{safe_title}"'
    subprocess.run(
        ["osascript", "-e", script],
        timeout=5,
        capture_output=True,
        check=False,
    )


def _notify_linux(title: str, message: str) -> None:
    subprocess.run(
        ["notify-send", title, message],
        timeout=5,
        capture_output=True,
        check=False,
    )
