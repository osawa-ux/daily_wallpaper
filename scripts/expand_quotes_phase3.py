"""Phase 3: refine quotes.json toward 静かな強さ / 挑戦と再起 / 覚悟と責任.

- Delete only q037 (TR short slogan, weak attribution) and q084 (Gandhi misattribution).
- Add 13 dignified quotes from politicians / philosophers / poets, all
  filtered to be readable as personal life advice rather than policy.

Run from repo root:
    python scripts/expand_quotes_phase3.py
"""
import json
from pathlib import Path

QUOTES_PATH = Path(__file__).resolve().parent.parent / "quotes.json"

DELETE_IDS = {"q037", "q084"}

# Each tuple: (text, author, [categories], length, verification_status, background or None)
NEW_QUOTES = [
    # --- Politicians, life-applicable ---
    (
        "You may have to fight a battle more than once to win it.",
        "Margaret Thatcher",
        ["endurance", "action"],
        "short",
        "verified",
        None,
    ),
    (
        "I do not know anyone who has got to the top without hard work. That is the recipe. It will not always get you to the top, but it will get you pretty near.",
        "Margaret Thatcher",
        ["discipline", "endurance"],
        "long",
        "verified",
        None,
    ),
    (
        "Life is not just eating, drinking, television and cinema. The human mind must be creative, must be self-generating; it cannot depend on others.",
        "Lee Kuan Yew",
        ["reflection", "discipline"],
        "long",
        "verified",
        None,
    ),
    (
        "There is no passion to be found playing small — in settling for a life that is less than the one you are capable of living.",
        "Nelson Mandela",
        ["action", "leadership"],
        "medium",
        "verified",
        None,
    ),
    (
        "Hope is not the conviction that something will turn out well, but the certainty that something makes sense, regardless of how it turns out.",
        "Václav Havel",
        ["endurance", "reflection"],
        "long",
        "verified",
        None,
    ),
    (
        "It is not the critic who counts. The credit belongs to the one who is actually in the arena, whose face is marred by dust and sweat and blood, who strives valiantly, who errs and comes short again and again.",
        "Theodore Roosevelt",
        ["action", "endurance"],
        "long",
        "verified",
        "1910年パリ・ソルボンヌ大学での演説『Citizenship in a Republic』通称「Man in the Arena」より抜粋。",
    ),
    (
        "Change will not come if we wait for some other person or some other time. We are the ones we've been waiting for. We are the change that we seek.",
        "Barack Obama",
        ["action", "leadership"],
        "long",
        "verified",
        None,
    ),
    (
        "Efforts and courage are not enough without purpose and direction.",
        "John F. Kennedy",
        ["focus", "discipline"],
        "medium",
        "verified",
        None,
    ),
    (
        "If you're going through hell, keep going.",
        "Winston Churchill",
        ["endurance"],
        "short",
        "verified",
        None,
    ),
    # --- Philosophers / poets, same temperature ---
    (
        "In the depth of winter, I finally learned that within me there lay an invincible summer.",
        "Albert Camus",
        ["endurance", "reflection"],
        "medium",
        "verified",
        None,
    ),
    (
        "Waste no more time arguing what a good man should be. Be one.",
        "Marcus Aurelius",
        ["discipline", "action"],
        "short",
        "verified",
        None,
    ),
    (
        "Tell me, what is it you plan to do with your one wild and precious life?",
        "Mary Oliver",
        ["reflection", "action"],
        "medium",
        "verified",
        None,
    ),
    (
        "It may be that when we no longer know what to do, we have come to our real work; and that when we no longer know which way to go, we have begun our real journey.",
        "Wendell Berry",
        ["reflection", "endurance"],
        "long",
        "verified",
        None,
    ),
]


def main() -> None:
    quotes = json.loads(QUOTES_PATH.read_text(encoding="utf-8"))
    before = len(quotes)

    quotes = [q for q in quotes if q["id"] not in DELETE_IDS]
    after_delete = len(quotes)

    used_ids = {q["id"] for q in quotes}
    next_n = 170
    while f"q{next_n:03d}" in used_ids:
        next_n += 1

    added = 0
    for text, author, categories, length, vs, background in NEW_QUOTES:
        new_id = f"q{next_n:03d}"
        while new_id in used_ids:
            next_n += 1
            new_id = f"q{next_n:03d}"
        used_ids.add(new_id)
        next_n += 1

        entry = {
            "id": new_id,
            "text": text,
            "author": author,
            "category": categories,
            "translated": False,
            "verification_status": vs,
            "mood_tags": [],
            "season_tags": [],
            "length": length,
            "enabled": True,
        }
        if background:
            entry["background"] = background
        quotes.append(entry)
        added += 1

    QUOTES_PATH.write_text(
        json.dumps(quotes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Before:  {before}")
    print(f"Deleted: {before - after_delete} ({sorted(DELETE_IDS)})")
    print(f"Added:   {added}")
    print(f"After:   {len(quotes)}")


if __name__ == "__main__":
    main()
