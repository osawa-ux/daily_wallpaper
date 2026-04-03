"""Select a quote based on weighted category logic."""

import logging
import random
from typing import Any

from .utils import get_current_season, get_weekday_name
from .history_manager import get_recent_ids

logger = logging.getLogger(__name__)


def compute_category_weights(
    config: dict[str, Any],
    mood: str | None = None,
) -> dict[str, float]:
    """Compute final category weights from weekday + season + mood."""
    weekday = get_weekday_name()
    season = get_current_season()

    # Base weekday weights
    weekday_weights = config.get("weekday_category_weights", {})
    weights: dict[str, float] = dict(weekday_weights.get(weekday, {}))

    if not weights:
        logger.warning("No weekday weights for %s, using uniform.", weekday)
        for cat in ["action", "discipline", "focus", "leadership",
                     "endurance", "reflection", "rest", "gratitude"]:
            weights[cat] = 10.0

    # Seasonal adjustments
    seasonal = config.get("seasonal_adjustments", {}).get(season, {})
    for cat, adj in seasonal.items():
        weights[cat] = weights.get(cat, 0) + adj

    # Mood adjustments
    if mood:
        mood_adj = config.get("mood_adjustments", {}).get(mood, {})
        for cat, adj in mood_adj.items():
            weights[cat] = weights.get(cat, 0) + adj

    # Remove categories with weight <= 0
    weights = {cat: w for cat, w in weights.items() if w > 0}

    logger.info("Final weights (weekday=%s, season=%s, mood=%s): %s",
                weekday, season, mood, weights)
    return weights


def _pick_category(weights: dict[str, float]) -> str:
    """Weighted random selection of a category."""
    categories = list(weights.keys())
    w = [weights[c] for c in categories]
    return random.choices(categories, weights=w, k=1)[0]


def _filter_candidates(
    quotes: list[dict[str, Any]],
    category: str,
    recent_ids: set[str],
) -> list[dict[str, Any]]:
    """Filter quotes by category, excluding recently shown."""
    return [
        q for q in quotes
        if category in q.get("category", []) and q["id"] not in recent_ids
    ]


def select_quote(
    quotes: list[dict[str, Any]],
    config: dict[str, Any],
    history: list[dict[str, Any]],
    mood: str | None = None,
    force_id: str | None = None,
) -> dict[str, Any] | None:
    """Select a single quote. Returns None only if quotes list is empty."""
    if not quotes:
        logger.error("No quotes available.")
        return None

    # Force specific quote
    if force_id:
        for q in quotes:
            if q["id"] == force_id:
                logger.info("Forced quote: %s", force_id)
                return q
        logger.warning("Quote ID %s not found, falling back to random.", force_id)

    cooldown_days = config.get("cooldown_days", 45)
    recent_ids = get_recent_ids(history, cooldown_days)
    weights = compute_category_weights(config, mood)

    if not weights:
        logger.warning("All category weights are zero, picking random quote.")
        return random.choice(quotes)

    # Try up to 5 category picks
    for attempt in range(5):
        category = _pick_category(weights)
        candidates = _filter_candidates(quotes, category, recent_ids)

        if candidates:
            # Slightly prefer short quotes
            weighted_candidates = []
            for q in candidates:
                w = 2.0 if q.get("length") == "short" else 1.0
                weighted_candidates.append((q, w))
            chosen = random.choices(
                [c[0] for c in weighted_candidates],
                weights=[c[1] for c in weighted_candidates],
                k=1,
            )[0]
            logger.info("Selected quote %s from category '%s' (attempt %d).",
                        chosen["id"], category, attempt + 1)
            return chosen
        logger.debug("No candidates for category '%s', retrying.", category)

    # Fallback 1: relax cooldown to half
    logger.info("Fallback: relaxing cooldown to %d days.", cooldown_days // 2)
    relaxed_ids = get_recent_ids(history, cooldown_days // 2)
    for _ in range(3):
        category = _pick_category(weights)
        candidates = _filter_candidates(quotes, category, relaxed_ids)
        if candidates:
            chosen = random.choice(candidates)
            logger.info("Selected quote %s with relaxed cooldown.", chosen["id"])
            return chosen

    # Fallback 2: ignore category constraint
    logger.info("Fallback: ignoring category constraint.")
    candidates = [q for q in quotes if q["id"] not in relaxed_ids]
    if candidates:
        chosen = random.choice(candidates)
        logger.info("Selected quote %s ignoring category.", chosen["id"])
        return chosen

    # Fallback 3: reset history
    logger.info("Fallback: resetting history filter.")
    return random.choice(quotes)
