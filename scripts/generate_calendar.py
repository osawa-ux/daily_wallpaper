"""Generate calendar_assignments.json and calendar_reserve.json.

Maps 366 MM-DD slots (01-01 through 12-31 including 02-29) to quote IDs.
Remaining enabled quotes go into reserve.

Constraints:
- No same author on consecutive days
- No same school on consecutive days
- No same primary category on consecutive days
- Same author must be >= 14 days apart
- Avoid consecutive long quotes
- Distribute gratitude/reflection/poetry naturally across the year
"""

import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Import school map from existing codebase
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.quote_selector import SCHOOL_MAP, DEFAULT_SCHOOL

# ---- Calendar day list (366 days, Jan 1 to Dec 31 incl Feb 29) ----
DAYS_IN_MONTH = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def all_mmdd() -> list[str]:
    days = []
    for m_idx, days_count in enumerate(DAYS_IN_MONTH):
        m = m_idx + 1
        for d in range(1, days_count + 1):
            days.append(f"{m:02d}-{d:02d}")
    return days

ALL_DAYS = all_mmdd()
assert len(ALL_DAYS) == 366, f"Expected 366 days, got {len(ALL_DAYS)}"


def school_of(q: dict) -> str:
    return SCHOOL_MAP.get(q.get("author", ""), DEFAULT_SCHOOL)

def primary_category(q: dict) -> str:
    cats = q.get("category", [])
    return cats[0] if cats else ""

JA_PATTERN = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')


def build_calendar(quotes: list[dict], seed: int = 42) -> tuple[dict[str, str], list[str]]:
    """Return (calendar: {MM-DD: quote_id}, reserve: [quote_ids])."""
    rng = random.Random(seed)

    # Shuffle to remove insertion-order bias
    pool = list(quotes)
    rng.shuffle(pool)

    # Build lookup
    by_id = {q["id"]: q for q in pool}

    # Pre-sort: spread authors evenly by assigning each author a target
    # position proportional to their count
    author_groups: dict[str, list[dict]] = defaultdict(list)
    for q in pool:
        author_groups[q.get("author", "")].append(q)

    # Score each quote with a target slot for even distribution
    scored: list[tuple[float, dict]] = []
    for author, qs in author_groups.items():
        n = len(qs)
        rng.shuffle(qs)
        for i, q in enumerate(qs):
            # spread across 366 positions
            target = (i + rng.random()) * 366.0 / n
            scored.append((target, q))

    scored.sort(key=lambda x: x[0])
    ordered = [q for _, q in scored]

    # Greedy assignment with constraint checking
    calendar: dict[str, str] = {}
    used_ids: set[str] = set()
    day_list = list(ALL_DAYS)

    # Track recent assignments for constraint checking
    assignments: list[dict | None] = [None] * 366

    def violates(q: dict, day_idx: int) -> bool:
        """Check if placing q at day_idx violates constraints."""
        # Consecutive author
        if day_idx > 0 and assignments[day_idx - 1]:
            prev = assignments[day_idx - 1]
            if q.get("author") == prev.get("author"):
                return True
            s_q, s_p = school_of(q), school_of(prev)
            if s_q == s_p and s_q != DEFAULT_SCHOOL:
                return True
            if primary_category(q) == primary_category(prev):
                return True
            if q.get("length") == "long" and prev.get("length") == "long":
                return True

        # Check next day if already assigned
        if day_idx < 365 and assignments[day_idx + 1]:
            nxt = assignments[day_idx + 1]
            if q.get("author") == nxt.get("author"):
                return True
            s_q2, s_n = school_of(q), school_of(nxt)
            if s_q2 == s_n and s_q2 != DEFAULT_SCHOOL:
                return True
            if primary_category(q) == primary_category(nxt):
                return True
            if q.get("length") == "long" and nxt.get("length") == "long":
                return True

        # 14-day author window
        author = q.get("author", "")
        if author:
            start = max(0, day_idx - 14)
            end = min(366, day_idx + 15)
            for j in range(start, end):
                if j != day_idx and assignments[j] and assignments[j].get("author") == author:
                    return True

        return False

    # Phase 1: Place quotes greedily
    unplaced: list[dict] = []
    slot_idx = 0

    for q in ordered:
        placed = False
        # Try near the target slot
        for offset in range(0, 366):
            idx = (slot_idx + offset) % 366
            if assignments[idx] is not None:
                continue
            if not violates(q, idx):
                assignments[idx] = q
                used_ids.add(q["id"])
                placed = True
                break
        if not placed:
            unplaced.append(q)
        slot_idx = (slot_idx + 1) % 366

    # Phase 2: Fill remaining empty slots with unplaced (relaxed constraints)
    empty_slots = [i for i in range(366) if assignments[i] is None]
    rng.shuffle(unplaced)

    for q in list(unplaced):
        for idx in list(empty_slots):
            # Only check consecutive author (relaxed)
            ok = True
            if idx > 0 and assignments[idx - 1]:
                if q.get("author") == assignments[idx - 1].get("author"):
                    ok = False
            if idx < 365 and assignments[idx + 1]:
                if q.get("author") == assignments[idx + 1].get("author"):
                    ok = False
            if ok:
                assignments[idx] = q
                used_ids.add(q["id"])
                empty_slots.remove(idx)
                unplaced.remove(q)
                break

    # Phase 3: Force-fill any remaining (should be rare)
    for q in list(unplaced):
        if empty_slots:
            idx = empty_slots.pop(0)
            assignments[idx] = q
            used_ids.add(q["id"])
            unplaced.remove(q)

    # Build calendar dict
    for i, day in enumerate(day_list):
        if assignments[i]:
            calendar[day] = assignments[i]["id"]

    # Reserve = enabled but not in calendar
    reserve = [q["id"] for q in pool if q["id"] not in used_ids]

    return calendar, reserve


def validate_calendar(calendar: dict[str, str], quotes_by_id: dict[str, dict]) -> list[str]:
    """Check constraints and report violations."""
    issues = []
    days = ALL_DAYS
    prev = None
    author_last_seen: dict[str, int] = {}

    for i, day in enumerate(days):
        qid = calendar.get(day)
        if not qid:
            issues.append(f"{day}: EMPTY SLOT")
            prev = None
            continue
        q = quotes_by_id.get(qid)
        if not q:
            issues.append(f"{day}: unknown quote ID {qid}")
            prev = None
            continue

        author = q.get("author", "")

        if prev:
            if author == prev.get("author"):
                issues.append(f"{day}: consecutive author '{author}'")
            s_q, s_p = school_of(q), school_of(prev)
            if s_q == s_p and s_q != DEFAULT_SCHOOL:
                issues.append(f"{day}: consecutive school '{s_q}'")
            if primary_category(q) == primary_category(prev):
                issues.append(f"{day}: consecutive primary category '{primary_category(q)}'")
            if q.get("length") == "long" and prev.get("length") == "long":
                issues.append(f"{day}: consecutive long quotes")

        if author and author in author_last_seen:
            gap = i - author_last_seen[author]
            if gap < 14:
                issues.append(f"{day}: author '{author}' repeated within {gap} days")

        if author:
            author_last_seen[author] = i
        prev = q

    return issues


def print_distribution(calendar: dict[str, str], quotes_by_id: dict[str, dict]) -> None:
    """Print distribution stats."""
    cats = Counter()
    schools = Counter()
    langs = Counter()
    lengths = Counter()
    authors = Counter()

    for day, qid in calendar.items():
        q = quotes_by_id.get(qid, {})
        for c in q.get("category", []):
            cats[c] += 1
        schools[school_of(q)] += 1
        langs[q.get("language", "?")] += 1
        lengths[q.get("length", "?")] += 1
        authors[q.get("author", "?")] += 1

    print("\n=== Calendar Distribution ===")
    print(f"  Days assigned: {len(calendar)}/366")
    print(f"  Unique authors: {len(authors)}")
    print(f"  Language: {dict(langs)}")
    print(f"  Length: {dict(lengths)}")
    print(f"  Category: {dict(sorted(cats.items(), key=lambda x: -x[1]))}")
    print(f"  School: {dict(sorted(schools.items(), key=lambda x: -x[1]))}")


def main():
    base = Path(__file__).resolve().parent.parent
    quotes_path = base / "quotes.json"
    cal_path = base / "calendar_assignments.json"
    reserve_path = base / "calendar_reserve.json"

    all_quotes = json.loads(quotes_path.read_text(encoding="utf-8"))
    enabled = [q for q in all_quotes if q.get("enabled", True)]
    print(f"Enabled quotes: {len(enabled)}")

    if len(enabled) < 366:
        print(f"ERROR: Need at least 366 enabled quotes, have {len(enabled)}")
        sys.exit(1)

    quotes_by_id = {q["id"]: q for q in all_quotes}

    calendar, reserve = build_calendar(enabled, seed=42)

    print(f"Calendar: {len(calendar)} days assigned")
    print(f"Reserve:  {len(reserve)} quotes")

    # Validate
    issues = validate_calendar(calendar, quotes_by_id)
    if issues:
        print(f"\nConstraint violations: {len(issues)}")
        for issue in issues[:20]:
            print(f"  {issue}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more")
    else:
        print("\nAll constraints satisfied.")

    print_distribution(calendar, quotes_by_id)

    # Write files
    with open(cal_path, "w", encoding="utf-8") as f:
        json.dump(calendar, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {cal_path}")

    with open(reserve_path, "w", encoding="utf-8") as f:
        json.dump(reserve, f, ensure_ascii=False, indent=2)
    print(f"Wrote {reserve_path}")


if __name__ == "__main__":
    main()
