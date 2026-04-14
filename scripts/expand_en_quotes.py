"""One-shot script: delete weak EN quotes and add 16 high-quality EN quotes.

Run from repo root:
    python scripts/expand_en_quotes.py
"""
import json
from pathlib import Path

QUOTES_PATH = Path(__file__).resolve().parent.parent / "quotes.json"

# Anonymous / generic / weak attribution
DELETE_IDS = {
    "q029", "q030", "q031", "q034", "q053", "q054", "q055",
    "q081", "q089", "q100",
    "q075", "q085", "q017", "q032", "q060",
}

# (text, author, [categories], length)
NEW_QUOTES = [
    # --- Philosophy / Reflection (8) ---
    ("You have power over your mind — not outside events. Realize this, and you will find strength.",
     "Marcus Aurelius", ["reflection", "discipline"], "medium"),
    ("We suffer more often in imagination than in reality.",
     "Seneca", ["reflection"], "short"),
    ("It's not what happens to you, but how you react to it that matters.",
     "Epictetus", ["reflection", "endurance"], "medium"),
    ("When we are no longer able to change a situation, we are challenged to change ourselves.",
     "Viktor Frankl", ["reflection", "endurance"], "medium"),
    ("Life can only be understood backwards; but it must be lived forwards.",
     "Søren Kierkegaard", ["reflection"], "medium"),
    ("I am not what happened to me, I am what I choose to become.",
     "Carl Jung", ["reflection", "action"], "medium"),
    ("Don't ask what the world needs. Ask what makes you come alive, and go do it. Because what the world needs is people who have come alive.",
     "Howard Thurman", ["action", "reflection"], "long"),
    ("Nothing in life is to be feared, it is only to be understood. Now is the time to understand more, so that we may fear less.",
     "Marie Curie", ["reflection", "endurance"], "long"),

    # --- Literature / Art (7) ---
    ("I've learned that people will forget what you said, people will forget what you did, but people will never forget how you made them feel.",
     "Maya Angelou", ["leadership", "reflection"], "long"),
    ("Not everything that is faced can be changed, but nothing can be changed until it is faced.",
     "James Baldwin", ["action", "reflection"], "medium"),
    ("The world breaks everyone, and afterward many are strong at the broken places.",
     "Ernest Hemingway", ["endurance", "reflection"], "medium"),
    ("And the day came when the risk to remain tight in a bud was more painful than the risk it took to blossom.",
     "Anaïs Nin", ["action", "reflection"], "long"),
    ("Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.",
     "Antoine de Saint-Exupéry", ["focus", "discipline"], "medium"),
    ("How we spend our days is, of course, how we spend our lives.",
     "Annie Dillard", ["reflection", "focus"], "short"),
    ("If you want to fly, you have to give up the things that weigh you down.",
     "Toni Morrison", ["action", "reflection"], "medium"),

    # --- Business / Practice (1) ---
    ("The big money is not in the buying and the selling, but in the waiting.",
     "Charlie Munger", ["discipline", "endurance"], "medium"),
]


def main() -> None:
    quotes = json.loads(QUOTES_PATH.read_text(encoding="utf-8"))
    before = len(quotes)

    quotes = [q for q in quotes if q["id"] not in DELETE_IDS]
    after_delete = len(quotes)

    used_ids = {q["id"] for q in quotes}
    next_n = 151
    while f"q{next_n:03d}" in used_ids:
        next_n += 1

    added = 0
    for text, author, categories, length in NEW_QUOTES:
        new_id = f"q{next_n:03d}"
        while new_id in used_ids:
            next_n += 1
            new_id = f"q{next_n:03d}"
        used_ids.add(new_id)
        next_n += 1

        quotes.append({
            "id": new_id,
            "text": text,
            "author": author,
            "category": categories,
            "translated": False,
            "verification_status": "verified",
            "mood_tags": [],
            "season_tags": [],
            "length": length,
            "enabled": True,
        })
        added += 1

    QUOTES_PATH.write_text(
        json.dumps(quotes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Before:  {before}")
    print(f"Deleted: {before - after_delete}")
    print(f"Added:   {added}")
    print(f"After:   {len(quotes)}")


if __name__ == "__main__":
    main()
