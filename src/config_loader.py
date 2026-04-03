"""Load and validate config.json and quotes.json."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Defaults used when config keys are missing
DEFAULTS: dict[str, Any] = {
    "wallpaper_width": 1920,
    "wallpaper_height": 1080,
    "cooldown_days": 45,
    "show_author": True,
    "show_translated_label": False,
    "overlay_opacity": 0.55,
    "use_background_images": False,
    "background_image_dir": "assets/backgrounds",
    "output_path": "output/wallpaper_today.jpg",
    "history_path": "output/history.json",
    "log_path": "logs/app.log",
    "default_mood": None,
    "font_quote": None,
    "font_author": None,
    "weekday_category_weights": {},
    "seasonal_adjustments": {},
    "mood_adjustments": {},
}


def load_config(base_dir: Path) -> dict[str, Any]:
    """Load config.json, filling missing keys with defaults."""
    config_path = base_dir / "config.json"
    config: dict[str, Any] = {}
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to parse config.json, using defaults: %s", e)
    else:
        logger.info("config.json not found, using defaults.")

    for key, default in DEFAULTS.items():
        config.setdefault(key, default)
    return config


def load_quotes(base_dir: Path) -> list[dict[str, Any]]:
    """Load quotes.json and return enabled quotes only."""
    quotes_path = base_dir / "quotes.json"
    if not quotes_path.exists():
        logger.warning("quotes.json not found.")
        return []
    try:
        data = json.loads(quotes_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Failed to parse quotes.json: %s", e)
        return []

    if not isinstance(data, list):
        logger.error("quotes.json must be a JSON array.")
        return []

    enabled = [q for q in data if q.get("enabled", True)]
    logger.info("Loaded %d enabled quotes (total %d).", len(enabled), len(data))
    return enabled
