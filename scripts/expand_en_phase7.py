"""Phase 7 EN expansion: 20 quotes reinforcing under-represented axes.

Addresses author concentration by diversifying into:
    medical (4), nursing/care (3), existentialism (4),
    literature — non-abstract (5), interpersonal support (4)

Per-axis minimum 2; medical+nursing ≥ 6; max 2-3 per author (this batch = 1 each).
source_note is added for traceability; selector ignores unknown fields.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QPATH = ROOT / "quotes.json"

NEW = [
    # === 医療 (4) ===
    {
        "text": "We are here to add what we can to life, not to get what we can from it.",
        "author": "William Osler",
        "category": ["leadership", "reflection"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "A Way of Life, 1913 address to Yale students",
    },
    {
        "text": "Even if I'm dying, until I actually die, I am still living.",
        "author": "Paul Kalanithi",
        "category": ["endurance", "reflection"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "When Breath Becomes Air (2016)",
    },
    {
        "text": "Every act of perception is to some degree an act of creation, and every act of memory is to some degree an act of imagination.",
        "author": "Oliver Sacks",
        "category": ["reflection", "focus"],
        "length": "long",
        "verification_status": "verified",
        "source_note": "Musicophilia (2007)",
    },
    {
        "text": "The bedside examination is not simply a clinical encounter. It is a ritual.",
        "author": "Abraham Verghese",
        "category": ["leadership", "focus"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "A Doctor's Touch — TED Global 2011",
    },

    # === 看護・ケア (3) ===
    {
        "text": "Let us never consider ourselves finished nurses. We must be learning all of our lives.",
        "author": "Florence Nightingale",
        "category": ["discipline", "leadership"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "Letter to probationer nurses, St Thomas's, 1872",
    },
    {
        "text": "The nurse is temporarily the consciousness of the unconscious, the love of life for the suicidal, the leg of the amputee, the eyes of the newly blind.",
        "author": "Virginia Henderson",
        "category": ["leadership", "reflection"],
        "length": "long",
        "verification_status": "verified",
        "source_note": "The Nature of Nursing (1966)",
    },
    {
        "text": "Suffering is only intolerable when nobody cares.",
        "author": "Cicely Saunders",
        "category": ["leadership", "reflection"],
        "length": "short",
        "verification_status": "verified",
        "source_note": "Care of the Dying lectures, St Christopher's Hospice",
    },

    # === 実存主義 (4) ===
    {
        "text": "All real living is meeting.",
        "author": "Martin Buber",
        "category": ["reflection", "leadership"],
        "length": "short",
        "verification_status": "verified",
        "source_note": "I and Thou (1923, tr. Smith)",
    },
    {
        "text": "Loneliness is the pain of being alone; solitude is the glory of being alone.",
        "author": "Paul Tillich",
        "category": ["reflection", "rest"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "The Eternal Now (1963)",
    },
    {
        "text": "One's life has value so long as one attributes value to the life of others, by means of love, friendship, indignation, compassion.",
        "author": "Simone de Beauvoir",
        "category": ["leadership", "reflection"],
        "length": "long",
        "verification_status": "verified",
        "source_note": "La Vieillesse / The Coming of Age (1970)",
    },
    {
        "text": "Philosophy means: to be on the way. Its questions are more essential than its answers.",
        "author": "Karl Jaspers",
        "category": ["reflection", "focus"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "Way to Wisdom (1951)",
    },

    # === 文学 — 具体寄り (5) ===
    {
        "text": "The two most powerful warriors are patience and time.",
        "author": "Leo Tolstoy",
        "category": ["endurance", "discipline"],
        "length": "short",
        "verification_status": "verified",
        "source_note": "War and Peace (1869), Kutuzov's counsel",
    },
    {
        "text": "The mystery of human existence lies not in just staying alive, but in finding something to live for.",
        "author": "Fyodor Dostoevsky",
        "category": ["reflection", "endurance"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "The Brothers Karamazov (1880)",
    },
    {
        "text": "If you surrender to the wind, you can ride it.",
        "author": "Toni Morrison",
        "category": ["action", "endurance"],
        "length": "short",
        "verification_status": "verified",
        "source_note": "Song of Solomon (1977)",
    },
    {
        "text": "It is good to have an end to journey toward; but it is the journey that matters, in the end.",
        "author": "Ursula K. Le Guin",
        "category": ["reflection", "action"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "The Left Hand of Darkness (1969)",
    },
    {
        "text": "Wherever you turn your eyes the world can shine like transfiguration. You don't have to bring a thing to it except a little willingness to see.",
        "author": "Marilynne Robinson",
        "category": ["reflection", "gratitude"],
        "length": "long",
        "verification_status": "verified",
        "source_note": "Gilead (2004)",
    },

    # === 対人支援・関係性 (4) ===
    {
        "text": "Vulnerability is not weakness; it's our greatest measure of courage.",
        "author": "Brené Brown",
        "category": ["endurance", "leadership"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "Daring Greatly (2012)",
    },
    {
        "text": "Often when you think you're at the end of something, you're at the beginning of something else.",
        "author": "Fred Rogers",
        "category": ["endurance", "reflection"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "Dartmouth commencement address, 2002",
    },
    {
        "text": "The good life is a process, not a state of being. It is a direction, not a destination.",
        "author": "Carl Rogers",
        "category": ["discipline", "reflection"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "On Becoming a Person (1961)",
    },
    {
        "text": "The most precious gift we can offer anyone is our attention.",
        "author": "Thich Nhat Hanh",
        "category": ["focus", "leadership"],
        "length": "medium",
        "verification_status": "verified",
        "source_note": "The Miracle of Mindfulness (1975)",
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
    print(f"Added {len(added)} quotes:")
    for aid, author in added:
        print(f"  {aid}  {author}")
    if skipped:
        print(f"Skipped {len(skipped)} duplicates:")
        for a, t in skipped:
            print(f"  {a}: {t}")
    print(f"Total quotes: {len(quotes)}")


if __name__ == "__main__":
    main()
