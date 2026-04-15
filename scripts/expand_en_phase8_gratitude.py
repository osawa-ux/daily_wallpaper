"""Phase 8 EN expansion: reinforce gratitude axis with 7 quotes.

All entries use 'gratitude' as the PRIMARY category (first element).
Targets authors not already saturated in gratitude and diversifies
across philosophy / spiritual / literature / essayist / poetry / medical.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QPATH = ROOT / "quotes.json"

NEW = [
    {
        "text": "Be joyful though you have considered all the facts.",
        "author": "Wendell Berry",
        "category": ["gratitude", "endurance"],
        "length": "short",
        "verification_status": "verified",
        "source_note": "Manifesto: The Mad Farmer Liberation Front (1973)",
    },
    {
        "text": "I would maintain that thanks are the highest form of thought, and that gratitude is happiness doubled by wonder.",
        "author": "G.K. Chesterton",
        "category": ["gratitude", "reflection"],
        "length": "long",
        "verification_status": "verified",
        "source_note": "A Short History of England (1917), ch. 6",
    },
    {
        "text": "Gratitude is not only the greatest of virtues, but the parent of all others.",
        "author": "Cicero",
        "category": ["gratitude", "leadership"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "Pro Plancio 80 (oration, 54 BC)",
    },
    {
        "text": "In ordinary life we hardly realize that we receive a great deal more than we give, and that it is only with gratitude that life becomes rich.",
        "author": "Dietrich Bonhoeffer",
        "category": ["gratitude", "reflection"],
        "length": "long",
        "verification_status": "verified",
        "source_note": "Letters and Papers from Prison (1943)",
    },
    {
        "text": "I have been a sentient being, a thinking animal, on this beautiful planet, and that in itself has been an enormous privilege and adventure.",
        "author": "Oliver Sacks",
        "category": ["gratitude", "reflection"],
        "length": "long",
        "verification_status": "verified",
        "source_note": "Gratitude (2015), posthumous essay collection",
    },
    {
        "text": "The three most essential prayers are Help, Thanks, Wow.",
        "author": "Anne Lamott",
        "category": ["gratitude", "reflection"],
        "length": "short",
        "verification_status": "verified",
        "source_note": "Help, Thanks, Wow: The Three Essential Prayers (2012)",
    },
    {
        "text": "When it's over, I want to say: all my life I was a bride married to amazement.",
        "author": "Mary Oliver",
        "category": ["gratitude", "reflection"],
        "length": "long",
        "verification_status": "verified",
        "source_note": "When Death Comes — New and Selected Poems (1992)",
    },
]


def main() -> None:
    quotes = json.loads(QPATH.read_text(encoding="utf-8"))
    existing_texts = {q["text"].strip() for q in quotes}
    existing_ids = {q["id"] for q in quotes}
    next_num = max(int(q["id"][1:]) for q in quotes) + 1

    added, skipped = [], []
    for entry in NEW:
        if entry["text"].strip() in existing_texts:
            skipped.append((entry["author"], entry["text"][:60]))
            continue
        while f"q{next_num:03d}" in existing_ids:
            next_num += 1
        new_id = f"q{next_num:03d}"
        next_num += 1
        quotes.append({
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
            "source_note": entry["source_note"],
        })
        added.append((new_id, entry["author"]))

    QPATH.write_text(
        json.dumps(quotes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Added {len(added)} gratitude quotes:")
    for aid, author in added:
        print(f"  {aid}  {author}")
    if skipped:
        print(f"Skipped {len(skipped)} duplicates:")
        for a, t in skipped:
            print(f"  {a}: {t}")
    print(f"Total quotes: {len(quotes)}")


if __name__ == "__main__":
    main()
