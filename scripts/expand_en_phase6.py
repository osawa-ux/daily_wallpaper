"""Phase 6 EN expansion: 28 contemplative / literary quotes.

Curated from the user's priority 25 authors. Criteria: 静かな強さ, 挑戦と再起,
覚悟と責任, verifiable, 2-3 lines suitable for wallpaper.

Skipped for attribution/verification risk or poor brevity fit:
    Ada Limón, Ocean Vuong, Oliver Burkeman, second Maggie Smith line,
    second Hirshfield line.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QPATH = ROOT / "quotes.json"

NEW = [
    # === Priority 12 ===
    {
        "text": "Instructions for living a life: Pay attention. Be astonished. Tell about it.",
        "author": "Mary Oliver",
        "category": ["focus", "reflection"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "The world asks of us only the strength we have and we give it. Then it asks more, and we give it.",
        "author": "Jane Hirshfield",
        "category": ["endurance", "reflection"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Before you know kindness as the deepest thing inside, you must know sorrow as the other deepest thing.",
        "author": "Naomi Shihab Nye",
        "category": ["reflection", "gratitude"],
        "length": "long",
        "verification_status": "verified",
    },
    {
        "text": "Anything or anyone that does not bring you alive is too small for you.",
        "author": "David Whyte",
        "category": ["action", "reflection"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Start close in, don't take the second step or the third, start with the first thing close in, the step you don't want to take.",
        "author": "David Whyte",
        "category": ["action", "discipline"],
        "length": "long",
        "verification_status": "verified",
    },
    {
        "text": "The only choice we have as we mature is how we inhabit our vulnerability.",
        "author": "David Whyte",
        "category": ["reflection", "endurance"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Hope is not a lottery ticket you can sit on the sofa and clutch. It is an axe you break down doors with in an emergency.",
        "author": "Rebecca Solnit",
        "category": ["action", "endurance"],
        "length": "long",
        "verification_status": "verified",
    },
    {
        "text": "In an age of speed, nothing could be more invigorating than going slow. In an age of distraction, nothing can feel more luxurious than paying attention.",
        "author": "Pico Iyer",
        "category": ["focus", "reflection"],
        "length": "long",
        "verification_status": "verified",
    },
    {
        "text": "Before you tell your life what you intend to do with it, listen for what it intends to do with you.",
        "author": "Parker Palmer",
        "category": ["reflection", "discipline"],
        "length": "long",
        "verification_status": "verified",
    },
    {
        "text": "Self-care is never a selfish act — it is simply good stewardship of the only gift I have.",
        "author": "Parker Palmer",
        "category": ["discipline", "rest"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Words make worlds.",
        "author": "Krista Tippett",
        "category": ["leadership", "reflection"],
        "length": "short",
        "verification_status": "verified",
    },
    {
        "text": "There are a thousand thousand reasons to live this life, every one of them sufficient.",
        "author": "Marilynne Robinson",
        "category": ["reflection", "gratitude"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "You are the sky. Everything else — it's just the weather.",
        "author": "Pema Chödrön",
        "category": ["reflection", "endurance"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "May you listen to your longing to be free.",
        "author": "John O'Donohue",
        "category": ["reflection", "action"],
        "length": "short",
        "verification_status": "verified",
    },
    {
        "text": "Your soul knows the geography of your destiny.",
        "author": "John O'Donohue",
        "category": ["reflection", "focus"],
        "length": "medium",
        "verification_status": "verified",
    },

    # === Next 13 ===
    {
        "text": "It is my belief that the more you study delight, the more delight there is to study.",
        "author": "Ross Gay",
        "category": ["gratitude", "reflection"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "You could make this place beautiful.",
        "author": "Maggie Smith",
        "category": ["action", "reflection"],
        "length": "short",
        "verification_status": "verified",
    },
    {
        "text": "Faith is nothing more — but how much this is — than a motion of the soul toward God.",
        "author": "Christian Wiman",
        "category": ["reflection"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Critical thinking without hope is cynicism. Hope without critical thinking is naivety.",
        "author": "Maria Popova",
        "category": ["reflection", "discipline"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "You don't have a right to the cards you believe you should have been dealt. You have an obligation to play the hell out of the ones you're holding.",
        "author": "Cheryl Strayed",
        "category": ["endurance", "discipline"],
        "length": "long",
        "verification_status": "verified",
    },
    {
        "text": "Be brave enough to break your own heart.",
        "author": "Cheryl Strayed",
        "category": ["action", "endurance"],
        "length": "short",
        "verification_status": "verified",
    },
    {
        "text": "To love yourself is to understand that you don't have to be anyone but the one you are.",
        "author": "Mark Nepo",
        "category": ["reflection", "discipline"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Anyone who isn't embarrassed of who they were last year probably isn't learning enough.",
        "author": "Alain de Botton",
        "category": ["reflection", "discipline"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Own your slippers, own who you are, own how you look, own your family, own the talents you have, and own the ones you don't.",
        "author": "Abraham Verghese",
        "category": ["reflection", "discipline"],
        "length": "long",
        "verification_status": "verified",
    },
    {
        "text": "What I regret most in my life are failures of kindness.",
        "author": "George Saunders",
        "category": ["reflection", "leadership"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Err in the direction of kindness.",
        "author": "George Saunders",
        "category": ["leadership", "action"],
        "length": "short",
        "verification_status": "verified",
    },
    {
        "text": "It is not happiness that makes us grateful, but gratitude that makes us happy.",
        "author": "David Steindl-Rast",
        "category": ["gratitude", "reflection"],
        "length": "medium",
        "verification_status": "verified",
    },
    {
        "text": "Rest is not a prize for those who have earned it. It is a sacred inheritance.",
        "author": "Cole Arthur Riley",
        "category": ["rest", "reflection"],
        "length": "medium",
        "verification_status": "secondary",
    },
]


def main() -> None:
    quotes = json.loads(QPATH.read_text(encoding="utf-8"))
    existing_texts = {q["text"].strip() for q in quotes}
    existing_ids = {q["id"] for q in quotes}
    next_num = max(int(q["id"][1:]) for q in quotes) + 1

    added = []
    skipped = []
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
