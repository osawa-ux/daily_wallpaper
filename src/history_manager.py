"""Manage quote display history stored in output/history.json."""

import json
import logging
import os
import tempfile
from datetime import date, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_history(history_path: Path) -> list[dict[str, Any]]:
    """Load history from JSON file. Returns empty list on failure."""
    if not history_path.exists():
        return []
    try:
        data = json.loads(history_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        logger.warning("history.json is not a list, resetting.")
        return []
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Corrupt history file, resetting: %s", e)
        return []


def save_history(history_path: Path, history: list[dict[str, Any]]) -> None:
    """Save history to JSON file using atomic write (tmp → os.replace).

    Atomic write prevents partial writes from corrupting history.json on crash.
    """
    history_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(history, ensure_ascii=False, indent=2)
    try:
        fd, tmp_path = tempfile.mkstemp(
            dir=history_path.parent,
            prefix=".history_tmp_",
            suffix=".json",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, history_path)
        except Exception:
            # Clean up tmp file if replace fails
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    except Exception as e:
        logger.warning("Atomic write failed, falling back to direct write: %s", e)
        history_path.write_text(content, encoding="utf-8")
    logger.info("History saved (%d entries).", len(history))


def get_recent_ids(history: list[dict[str, Any]], cooldown_days: int) -> set[str]:
    """Return set of quote IDs shown within cooldown_days."""
    cutoff = (date.today() - timedelta(days=cooldown_days)).isoformat()
    return {
        entry["quote_id"]
        for entry in history
        if entry.get("date", "") >= cutoff and "quote_id" in entry
    }


def add_entry(
    history: list[dict[str, Any]],
    quote: dict[str, Any],
    mood: str | None,
    season: str,
    wallpaper_path: str,
) -> list[dict[str, Any]]:
    """Append a new entry to history and return updated list."""
    entry = {
        "date": date.today().isoformat(),
        "quote_id": quote["id"],
        "text": quote["text"],
        "author": quote.get("author", ""),
        "category": quote.get("category", []),
        "mood": mood,
        "season": season,
        "wallpaper_path": wallpaper_path,
    }
    history.append(entry)
    return history
