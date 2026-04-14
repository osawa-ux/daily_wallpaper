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


# Known valid values for validation
VALID_CATEGORIES = {
    "action", "discipline", "focus", "leadership",
    "endurance", "reflection", "rest", "gratitude",
}
VALID_VERIFICATION = {"verified", "translated", "original", "secondary"}
VALID_LENGTHS = {"short", "medium", "long"}


def validate_quotes(base_dir: Path, config: dict[str, Any] | None = None) -> list[str]:
    """Validate quotes.json and return list of issues found.

    Checks: id uniqueness, required fields, valid categories,
    verification_status, length, text non-empty.
    """
    quotes_path = base_dir / "quotes.json"
    if not quotes_path.exists():
        return ["quotes.json not found"]

    try:
        data = json.loads(quotes_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return [f"Failed to parse quotes.json: {e}"]

    if not isinstance(data, list):
        return ["quotes.json must be a JSON array"]

    # Gather known categories from config if available
    routing = (config or {}).get("style_routing", {})
    known_cats = set(routing.get("reflective_categories", []))
    known_cats |= set(routing.get("action_categories", []))
    known_cats = known_cats or VALID_CATEGORIES

    issues: list[str] = []
    seen_ids: dict[str, int] = {}

    for i, q in enumerate(data):
        prefix = f"[{i}]"
        qid = q.get("id", "")

        # ID checks
        if not qid:
            issues.append(f"{prefix} missing 'id'")
        elif qid in seen_ids:
            issues.append(f"{prefix} duplicate id '{qid}' (first at [{seen_ids[qid]}])")
        else:
            seen_ids[qid] = i

        # Text
        if not q.get("text", "").strip():
            issues.append(f"{prefix} {qid}: empty 'text'")

        # Category
        cats = q.get("category", [])
        if not cats:
            issues.append(f"{prefix} {qid}: empty 'category' (required for style routing)")
        else:
            unknown = set(cats) - known_cats
            if unknown:
                issues.append(f"{prefix} {qid}: unknown categories {unknown}")

        # enabled
        if "enabled" not in q:
            issues.append(f"{prefix} {qid}: missing 'enabled' field")

        # verification_status
        vs = q.get("verification_status", "")
        if vs and vs not in VALID_VERIFICATION:
            issues.append(f"{prefix} {qid}: invalid verification_status '{vs}' (expected: {VALID_VERIFICATION})")

        # length
        ln = q.get("length", "")
        if ln and ln not in VALID_LENGTHS:
            issues.append(f"{prefix} {qid}: invalid length '{ln}' (expected: {VALID_LENGTHS})")

    # Summary stats
    total = len(data)
    enabled = sum(1 for q in data if q.get("enabled", True))
    cat_counts: dict[str, int] = {}
    for q in data:
        for c in q.get("category", []):
            cat_counts[c] = cat_counts.get(c, 0) + 1

    stats = [
        f"--- Stats ---",
        f"Total quotes: {total}",
        f"Enabled: {enabled}, Disabled: {total - enabled}",
        f"Category distribution: {dict(sorted(cat_counts.items(), key=lambda x: -x[1]))}",
    ]

    return issues + [""] + stats
