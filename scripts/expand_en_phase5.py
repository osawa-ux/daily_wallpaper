"""Phase 5 EN expansion: add 25 dignified English quotes.

Candidates were checked against existing DB; duplicates were replaced with
same-axis alternatives. All entries focus on 静かな強さ / 挑戦と再起 / 覚悟と責任.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QPATH = ROOT / "quotes.json"

NEW = [
    # --- Stoic / Philosophy ---
    {
        "text": "The impediment to action advances action. What stands in the way becomes the way.",
        "author": "Marcus Aurelius",
        "category": ["action", "endurance"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "It is not that we have a short time to live, but that we waste much of it.",
        "author": "Seneca",
        "category": ["reflection", "discipline"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Difficulties strengthen the mind, as labor does the body.",
        "author": "Seneca",
        "category": ["endurance", "discipline"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "First say to yourself what you would be; and then do what you have to do.",
        "author": "Epictetus",
        "category": ["discipline", "action"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Character is destiny.",
        "author": "Heraclitus",
        "category": ["reflection", "discipline"],
        "length": "short",
        "verification_status": "secondary",
    },
    {
        "text": "Begin at once to live, and count each separate day as a separate life.",
        "author": "Seneca",
        "category": ["discipline", "action"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "The best revenge is not to be like your enemy.",
        "author": "Marcus Aurelius",
        "category": ["reflection", "leadership"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "The mind is not a vessel to be filled, but a fire to be kindled.",
        "author": "Plutarch",
        "category": ["focus", "reflection"],
        "length": "medium",
        "verification_status": "secondary",
    },
    {
        "text": "Things do not change; we change.",
        "author": "Henry David Thoreau",
        "category": ["reflection"],
        "length": "short",
        "verification_status": "verified",
    },
    {
        "text": "The greatest thing in the world is to know how to belong to oneself.",
        "author": "Michel de Montaigne",
        "category": ["reflection", "discipline"],
        "length": "medium",
        "verification_status": "verified",
    },

    # --- Literature / Poetry ---
    {
        "text": "Let everything happen to you: beauty and terror. Just keep going. No feeling is final.",
        "author": "Rainer Maria Rilke",
        "category": ["endurance", "reflection"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Be patient toward all that is unsolved in your heart and try to love the questions themselves.",
        "author": "Rainer Maria Rilke",
        "category": ["reflection", "endurance"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "I believe that man will not merely endure: he will prevail.",
        "author": "William Faulkner",
        "category": ["endurance", "leadership"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "All we have to decide is what to do with the time that is given us.",
        "author": "J.R.R. Tolkien",
        "category": ["action", "reflection"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Someone I loved once gave me a box full of darkness. It took me years to understand that this too, was a gift.",
        "author": "Mary Oliver",
        "category": ["reflection", "endurance"],
        "length": "long",
        "verification_status": "verified",
    },
    {
        "text": "Hope is the thing with feathers that perches in the soul, and sings the tune without the words, and never stops at all.",
        "author": "Emily Dickinson",
        "category": ["reflection", "endurance"],
        "length": "long",
        "verification_status": "verified",
    },
    {
        "text": "Ever tried. Ever failed. No matter. Try again. Fail again. Fail better.",
        "author": "Samuel Beckett",
        "category": ["endurance", "action"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Traveler, there is no path. The path is made by walking.",
        "author": "Antonio Machado",
        "category": ["action", "reflection"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "I am not afraid of storms, for I am learning how to sail my ship.",
        "author": "Louisa May Alcott",
        "category": ["endurance", "action"],
        "length": "medium",
        "verification_status": "secondary",
    },

    # --- Political leaders (life-applicable) ---
    {
        "text": "If there is no struggle, there is no progress.",
        "author": "Frederick Douglass",
        "category": ["action", "endurance"],
        "length": "medium",
        "verification_status": "verified",
    },

    # --- Spiritual / Reflection ---
    {
        "text": "Nothing ever goes away until it has taught us what we need to know.",
        "author": "Pema Chödrön",
        "category": ["reflection", "endurance"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Action springs not from thought, but from a readiness for responsibility.",
        "author": "Dietrich Bonhoeffer",
        "category": ["leadership", "action"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Attention is the rarest and purest form of generosity.",
        "author": "Simone Weil",
        "category": ["focus", "reflection"],
        "length": "medium",
        "verification_status": "verified",
    },

    # --- Discipline / Modern ---
    {
        "text": "Enthusiasm is common. Endurance is rare.",
        "author": "Angela Duckworth",
        "category": ["discipline", "endurance"],
        "length": "short",
        "verification_status": "verified",
    },
    {
        "text": "You do not rise to the level of your goals. You fall to the level of your systems.",
        "author": "James Clear",
        "category": ["discipline", "focus"],
        "length": "medium",
        "verification_status": "verified",
    },
]


def main() -> None:
    quotes = json.loads(QPATH.read_text(encoding="utf-8"))
    existing_ids = {q["id"] for q in quotes}
    existing_texts = {q["text"].strip() for q in quotes}

    next_num = max(int(q["id"][1:]) for q in quotes) + 1
    added = []
    for entry in NEW:
        if entry["text"].strip() in existing_texts:
            print(f"SKIP (dup text): {entry['author']}: {entry['text'][:60]}")
            continue
        while f"q{next_num:03d}" in existing_ids:
            next_num += 1
        new_id = f"q{next_num:03d}"
        next_num += 1
        q = {
            "id": new_id,
            "text": entry["text"],
            "author": entry["author"],
            "category": entry["category"],
            "translated": False,
            "verification_status": entry["verification_status"],
            "mood_tags": [],
            "season_tags": [],
            "length": entry["length"],
            "enabled": True,
        }
        quotes.append(q)
        added.append(new_id)

    QPATH.write_text(
        json.dumps(quotes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Added {len(added)} quotes: {added}")
    print(f"Total quotes: {len(quotes)}")


if __name__ == "__main__":
    main()
