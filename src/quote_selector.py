"""Select a quote based on weighted category + diversity constraints.

Diversity layers (Plan C):
    1. School-of-thought: block quotes whose school was used in the last 2 days.
    2. Consecutive author: block the most recent author.
    3. Author 14-day window: block authors shown in the last 14 days.
    4. Author-frequency weighting: rarer authors get a small bonus.

Relaxation order when the strict filter yields nothing:
    school → consecutive-author → author 14-day window
(matches the order the user specified: drop school first, then consec, then 14d).

The school map is maintained here, not in quotes.json, so data stays clean.
SCHOOL_OVERRIDES_BY_ID offers a small escape hatch for rare exceptions.
"""

import hashlib
import logging
import math
import random
from collections import Counter
from datetime import date, timedelta
from typing import Any

from .utils import get_current_season, get_weekday_name
from .history_manager import get_recent_ids

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# School-of-thought classification
# ---------------------------------------------------------------------------

SCHOOL_MAP: dict[str, str] = {
    # --- Stoic ---
    "Marcus Aurelius": "stoic",
    "Seneca": "stoic",
    "Epictetus": "stoic",
    "Zeno of Citium": "stoic",
    # --- Ancient / classical philosophy ---
    "Heraclitus": "philosophy",
    "Plutarch": "philosophy",
    "Aristotle": "philosophy",
    "Plato": "philosophy",
    "Socrates": "philosophy",
    # --- Early-modern / modern philosophy ---
    "Michel de Montaigne": "philosophy",
    "Henry David Thoreau": "philosophy",
    "Ralph Waldo Emerson": "philosophy",
    "Blaise Pascal": "philosophy",
    # --- Existentialism ---
    "Søren Kierkegaard": "existential",
    "Friedrich Nietzsche": "existential",
    "Martin Buber": "existential",
    "Paul Tillich": "existential",
    "Simone de Beauvoir": "existential",
    "Karl Jaspers": "existential",
    "Jean-Paul Sartre": "existential",
    "Albert Camus": "existential",
    "Gabriel Marcel": "existential",
    "Rainer Maria Rilke": "existential",
    # --- Psychology ---
    "Viktor Frankl": "psychology",
    "Carl Jung": "psychology",
    "Alfred Adler": "psychology",
    "Sigmund Freud": "psychology",
    "Abraham Maslow": "psychology",
    "Angela Duckworth": "psychology",
    # --- Interpersonal / humanistic ---
    "Carl Rogers": "interpersonal",
    "Brené Brown": "interpersonal",
    "Fred Rogers": "interpersonal",
    "Nel Noddings": "interpersonal",
    # --- Buddhist / eastern ---
    "Thich Nhat Hanh": "buddhist",
    "Dalai Lama": "buddhist",
    "Pema Chödrön": "buddhist",
    "Shunryu Suzuki": "buddhist",
    "D.T. Suzuki": "buddhist",
    "Ram Dass": "buddhist",
    "Lao Tzu": "eastern",
    "Zhuangzi": "eastern",
    "Confucius": "eastern",
    "Mencius": "eastern",
    # --- Medical ---
    "William Osler": "medical",
    "Atul Gawande": "medical",
    "Paul Kalanithi": "medical",
    "Abraham Verghese": "medical",
    "Oliver Sacks": "medical",
    "Francis W. Peabody": "medical",
    "Rachel Naomi Remen": "medical",
    "Bernard Lown": "medical",
    "Victoria Sweet": "medical",
    # --- Nursing / care ---
    "Florence Nightingale": "nursing",
    "Cicely Saunders": "nursing",
    "Virginia Henderson": "nursing",
    "Jean Watson": "nursing",
    # --- Contemplative / spiritual ---
    "Henri Nouwen": "spiritual",
    "Parker Palmer": "spiritual",
    "Krista Tippett": "spiritual",
    "Dietrich Bonhoeffer": "spiritual",
    "Simone Weil": "spiritual",
    "Mark Nepo": "spiritual",
    "David Steindl-Rast": "spiritual",
    "Cole Arthur Riley": "spiritual",
    "Thomas Merton": "spiritual",
    "Christian Wiman": "spiritual",
    "C.S. Lewis": "spiritual",
    "Mother Teresa": "spiritual",
    # --- Poetry ---
    "Mary Oliver": "poetry",
    "Emily Dickinson": "poetry",
    "Jane Hirshfield": "poetry",
    "Naomi Shihab Nye": "poetry",
    "David Whyte": "poetry",
    "Antonio Machado": "poetry",
    "John O'Donohue": "poetry",
    "Ross Gay": "poetry",
    "Maggie Smith": "poetry",
    "Walt Whitman": "poetry",
    "Robert Frost": "poetry",
    "W.H. Auden": "poetry",
    "T.S. Eliot": "poetry",
    "Ada Limón": "poetry",
    "Ocean Vuong": "poetry",
    # --- Literature (novels / drama / essays) ---
    "Leo Tolstoy": "literature",
    "Fyodor Dostoevsky": "literature",
    "Anton Chekhov": "literature",
    "Virginia Woolf": "literature",
    "James Baldwin": "literature",
    "Toni Morrison": "literature",
    "Ursula K. Le Guin": "literature",
    "Marilynne Robinson": "literature",
    "Kazuo Ishiguro": "literature",
    "William Faulkner": "literature",
    "Samuel Beckett": "literature",
    "J.R.R. Tolkien": "literature",
    "Louisa May Alcott": "literature",
    "George Saunders": "literature",
    "Wendell Berry": "literature",
    "Herman Melville": "literature",
    "Ernest Hemingway": "literature",
    # --- Essayist / popular thinker ---
    "Maria Popova": "essayist",
    "Alain de Botton": "essayist",
    "Cheryl Strayed": "essayist",
    "Rebecca Solnit": "essayist",
    "Pico Iyer": "essayist",
    "Oliver Burkeman": "essayist",
    # --- Modern / productivity ---
    "James Clear": "modern",
    "Steve Jobs": "modern",
    "Angela Lee Duckworth": "modern",
    # --- Activist / leader ---
    "Frederick Douglass": "activist",
    "Martin Luther King Jr.": "activist",
    "Nelson Mandela": "activist",
    "Mahatma Gandhi": "activist",
    "Malcolm X": "activist",
    "Viola Davis": "activist",
}

# Rare exceptions keyed by quote id. Keep tiny.
SCHOOL_OVERRIDES_BY_ID: dict[str, str] = {}

DEFAULT_SCHOOL = "other"


def _school_of(quote: dict[str, Any]) -> str:
    qid = quote.get("id", "")
    if qid in SCHOOL_OVERRIDES_BY_ID:
        return SCHOOL_OVERRIDES_BY_ID[qid]
    return SCHOOL_MAP.get(quote.get("author", ""), DEFAULT_SCHOOL)


def _school_from_history_entry(entry: dict[str, Any]) -> str:
    qid = entry.get("quote_id", "")
    if qid in SCHOOL_OVERRIDES_BY_ID:
        return SCHOOL_OVERRIDES_BY_ID[qid]
    return SCHOOL_MAP.get(entry.get("author", ""), DEFAULT_SCHOOL)


# ---------------------------------------------------------------------------
# Category weighting (unchanged)
# ---------------------------------------------------------------------------

def compute_category_weights(
    config: dict[str, Any],
    mood: str | None = None,
) -> dict[str, float]:
    """Compute final category weights from weekday + season + mood."""
    weekday = get_weekday_name()
    season = get_current_season()

    weekday_weights = config.get("weekday_category_weights", {})
    weights: dict[str, float] = dict(weekday_weights.get(weekday, {}))

    if not weights:
        logger.warning("No weekday weights for %s, using uniform.", weekday)
        for cat in ["action", "discipline", "focus", "leadership",
                     "endurance", "reflection", "rest", "gratitude"]:
            weights[cat] = 10.0

    seasonal = config.get("seasonal_adjustments", {}).get(season, {})
    for cat, adj in seasonal.items():
        weights[cat] = weights.get(cat, 0) + adj

    if mood:
        mood_adj = config.get("mood_adjustments", {}).get(mood, {})
        for cat, adj in mood_adj.items():
            weights[cat] = weights.get(cat, 0) + adj

    weights = {cat: w for cat, w in weights.items() if w > 0}
    logger.info("Final weights (weekday=%s, season=%s, mood=%s): %s",
                weekday, season, mood, weights)
    return weights


def _pick_category(weights: dict[str, float], rng: random.Random) -> str:
    cats = list(weights.keys())
    w = [weights[c] for c in cats]
    return rng.choices(cats, weights=w, k=1)[0]


# ---------------------------------------------------------------------------
# History-derived context
# ---------------------------------------------------------------------------

def _recent_context(
    history: list[dict[str, Any]],
    author_cooldown_days: int,
    school_window: int,
) -> tuple[str | None, set[str], set[str]]:
    """Return (last_author, authors_in_Nday_window, schools_in_last_K_entries)."""
    last_author = history[-1].get("author") if history else None

    cutoff_14 = (date.today() - timedelta(days=author_cooldown_days)).isoformat()
    authors_14d = {
        e.get("author", "")
        for e in history
        if e.get("date", "") >= cutoff_14 and e.get("author")
    }

    last_k = history[-school_window:] if history else []
    recent_schools = {_school_from_history_entry(e) for e in last_k}
    recent_schools.discard("")  # defensive

    return last_author, authors_14d, recent_schools


# ---------------------------------------------------------------------------
# Filter / tier-based relaxation
# ---------------------------------------------------------------------------

def _apply_tier(
    candidates: list[dict[str, Any]],
    *,
    drop_school: bool,
    drop_consec: bool,
    drop_14d: bool,
    last_author: str | None,
    authors_14d: set[str],
    recent_schools: set[str],
) -> list[dict[str, Any]]:
    out = candidates
    if not drop_school and recent_schools:
        out = [q for q in out if _school_of(q) not in recent_schools]
    if not drop_consec and last_author:
        out = [q for q in out if q.get("author") != last_author]
    if not drop_14d and authors_14d:
        out = [q for q in out if q.get("author") not in authors_14d]
    return out


# Relaxation order the user specified: drop school → drop consec → drop 14d
_RELAX_TIERS: list[tuple[bool, bool, bool]] = [
    (False, False, False),  # strictest
    (True,  False, False),  # drop school
    (True,  True,  False),  # drop school + consec
    (True,  True,  True),   # drop all three
]


# ---------------------------------------------------------------------------
# Weighted pick (short-bonus + author-frequency bonus)
# ---------------------------------------------------------------------------

def _build_author_freq(quotes: list[dict[str, Any]]) -> Counter:
    return Counter(q.get("author", "") for q in quotes)


def _weight_for(quote: dict[str, Any], author_freq: Counter) -> float:
    base = 2.0 if quote.get("length") == "short" else 1.0
    n = max(1, author_freq.get(quote.get("author", ""), 1))
    # Rarity bonus: 1/sqrt(n). Author with 1 quote → 1.0; with 5 → ~0.45.
    rarity = 1.0 / math.sqrt(n)
    return base * rarity


def _weighted_pick(
    candidates: list[dict[str, Any]],
    rng: random.Random,
    author_freq: Counter,
) -> dict[str, Any]:
    weights = [_weight_for(q, author_freq) for q in candidates]
    return rng.choices(candidates, weights=weights, k=1)[0]


# ---------------------------------------------------------------------------
# Candidate assembly
# ---------------------------------------------------------------------------

def _filter_candidates(
    quotes: list[dict[str, Any]],
    category: str,
    recent_ids: set[str],
) -> list[dict[str, Any]]:
    return [
        q for q in quotes
        if category in q.get("category", []) and q["id"] not in recent_ids
    ]


def _make_deterministic_seed(mood: str | None) -> int:
    seed_str = f"{date.today().isoformat()}:{mood or ''}"
    digest = hashlib.md5(seed_str.encode()).hexdigest()
    return int(digest, 16) % (2 ** 32)


# ---------------------------------------------------------------------------
# Main selection entry point
# ---------------------------------------------------------------------------

def select_quote(
    quotes: list[dict[str, Any]],
    config: dict[str, Any],
    history: list[dict[str, Any]],
    mood: str | None = None,
    force_id: str | None = None,
) -> dict[str, Any] | None:
    """Select a single quote with diversity constraints.

    Returns None only if quotes list is empty.
    """
    if not quotes:
        logger.error("No quotes available.")
        return None

    if force_id:
        for q in quotes:
            if q["id"] == force_id:
                logger.info("Forced quote: %s", force_id)
                return q
        logger.warning("Quote ID %s not found, falling back to random.", force_id)

    seed = _make_deterministic_seed(mood)
    rng = random.Random(seed)
    logger.info("Selection seed (date+mood): %d", seed)

    cooldown_days = config.get("cooldown_days", 45)
    author_cooldown_days = config.get("author_cooldown_days", 14)
    school_window = config.get("school_window", 2)

    recent_ids = get_recent_ids(history, cooldown_days)
    last_author, authors_14d, recent_schools = _recent_context(
        history, author_cooldown_days, school_window,
    )
    logger.info(
        "Diversity context: last_author=%s, authors_14d=%d, recent_schools=%s",
        last_author, len(authors_14d), sorted(recent_schools),
    )

    author_freq = _build_author_freq(quotes)

    weights = compute_category_weights(config, mood)
    if not weights:
        logger.warning("All category weights are zero, picking random quote.")
        return rng.choice(quotes)

    # Tier loop: up to 5 category attempts, each tries all 4 relaxation tiers
    for attempt in range(5):
        category = _pick_category(weights, rng)
        base = _filter_candidates(quotes, category, recent_ids)
        if not base:
            logger.debug("No candidates for category '%s', retrying.", category)
            continue

        for tier_idx, (drop_school, drop_consec, drop_14d) in enumerate(_RELAX_TIERS):
            pool = _apply_tier(
                base,
                drop_school=drop_school,
                drop_consec=drop_consec,
                drop_14d=drop_14d,
                last_author=last_author,
                authors_14d=authors_14d,
                recent_schools=recent_schools,
            )
            if pool:
                chosen = _weighted_pick(pool, rng, author_freq)
                logger.info(
                    "Selected %s from category '%s' attempt=%d tier=%d (school_dropped=%s, consec_dropped=%s, 14d_dropped=%s).",
                    chosen["id"], category, attempt + 1, tier_idx,
                    drop_school, drop_consec, drop_14d,
                )
                return chosen

    # Fallback 1: relax ID cooldown to half
    logger.info("Fallback: relaxing ID cooldown to %d days.", cooldown_days // 2)
    relaxed_ids = get_recent_ids(history, cooldown_days // 2)
    for _ in range(3):
        category = _pick_category(weights, rng)
        candidates = _filter_candidates(quotes, category, relaxed_ids)
        if candidates:
            chosen = _weighted_pick(candidates, rng, author_freq)
            logger.info("Selected %s with relaxed ID cooldown.", chosen["id"])
            return chosen

    # Fallback 2: ignore category
    logger.info("Fallback: ignoring category constraint.")
    candidates = [q for q in quotes if q["id"] not in relaxed_ids]
    if candidates:
        chosen = _weighted_pick(candidates, rng, author_freq)
        logger.info("Selected %s ignoring category.", chosen["id"])
        return chosen

    logger.info("Fallback: resetting history filter.")
    return rng.choice(quotes)
