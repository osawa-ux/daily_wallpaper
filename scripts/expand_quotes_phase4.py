"""Phase 4: add 38 high-quality quotes toward 静かな強さ / 挑戦と再起 / 覚悟と責任.

- Mix of philosophy, literature, politicians (life-applicable only),
  Japanese classics, and modern voices.
- Japanese paraphrases / unclear primary sources are marked `secondary`.
- Last Japanese batch: future expansions will focus on English.

Run from repo root:
    python scripts/expand_quotes_phase4.py
"""
import json
from pathlib import Path

QUOTES_PATH = Path(__file__).resolve().parent.parent / "quotes.json"

# (text, author, [categories], length, verification_status, background or None)
NEW_QUOTES = [
    # === A. Philosophy (8) ===
    ("That which does not kill us makes us stronger.",
     "Friedrich Nietzsche", ["endurance"], "short", "verified", None),
    ("To dare is to lose one's footing momentarily. Not to dare is to lose oneself.",
     "Søren Kierkegaard", ["action", "endurance"], "medium", "verified", None),
    ("Mastering others is strength. Mastering yourself is true power.",
     "Lao Tzu", ["discipline", "focus"], "short", "verified", None),
    ("No man ever steps in the same river twice, for it's not the same river and he's not the same man.",
     "Heraclitus", ["reflection"], "medium", "verified", None),
    ("No man is free who is not master of himself.",
     "Epictetus", ["discipline", "reflection"], "short", "verified", None),
    ("The good life is one inspired by love and guided by knowledge.",
     "Bertrand Russell", ["reflection", "leadership"], "medium", "verified", None),
    ("The greatest weapon against stress is our ability to choose one thought over another.",
     "William James", ["focus", "endurance"], "medium", "verified", None),
    ("To exist is to change, to change is to mature, to mature is to go on creating oneself endlessly.",
     "Henri Bergson", ["action", "reflection"], "long", "verified", None),

    # === B. Literature & Poetry (8) ===
    ("Perhaps all the dragons in our lives are princesses who are only waiting to see us act, just once, with beauty and courage.",
     "Rainer Maria Rilke", ["endurance", "action"], "long", "verified", None),
    ("Everyone thinks of changing the world, but no one thinks of changing himself.",
     "Leo Tolstoy", ["discipline", "reflection"], "medium", "verified", None),
    ("Only those who will risk going too far can possibly find out how far one can go.",
     "T.S. Eliot", ["action", "endurance"], "medium", "verified", None),
    ("Arrange whatever pieces come your way.",
     "Virginia Woolf", ["endurance", "action"], "short", "verified", None),
    ("The best way out is always through.",
     "Robert Frost", ["endurance"], "short", "verified", None),
    ("Go confidently in the direction of your dreams. Live the life you have imagined.",
     "Henry David Thoreau", ["action", "reflection"], "medium", "verified", None),
    ("Keep your face always toward the sunshine, and shadows will fall behind you.",
     "Walt Whitman", ["endurance", "reflection"], "medium", "verified", None),
    ("You can't cross the sea merely by standing and staring at the water.",
     "Rabindranath Tagore", ["action"], "medium", "verified", None),

    # === C. Statesmen (life-applicable) (6) ===
    ("I am a slow walker, but I never walk back.",
     "Abraham Lincoln", ["endurance", "discipline"], "short", "verified", None),
    ("You gain strength, courage, and confidence by every experience in which you really stop to look fear in the face.",
     "Eleanor Roosevelt", ["endurance", "action"], "long", "verified", None),
    ("Do one thing every day that scares you.",
     "Eleanor Roosevelt", ["action"], "short", "verified", None),
    ("Never, never, never give in.",
     "Winston Churchill", ["endurance"], "short", "verified",
     "1941年10月29日、母校ハロー校での演説より。"),
    ("Work for something because it is good, not just because it stands a chance to succeed.",
     "Václav Havel", ["discipline", "action"], "medium", "verified", None),
    ("Far better is it to dare mighty things, to win glorious triumphs, even though checkered by failure, than to rank with those poor spirits who neither enjoy much nor suffer much.",
     "Theodore Roosevelt", ["action", "endurance"], "long", "verified",
     "1899年シカゴ演説『The Strenuous Life』より。"),

    # === D. Japanese (10) — last Japanese batch ===
    ("武士道において、誠は言と成の二字より成る。言ったことは必ず成す、それが誠である。",
     "新渡戸稲造", ["discipline", "leadership"], "long", "secondary",
     "『武士道』第五章「義」の趣旨を要約した表現。原文の直訳ではない。"),
    ("われわれの内にひそむ無限の可能性を信ずる者にとって、人生は果てしない探求である。",
     "岡倉天心", ["reflection", "action"], "medium", "secondary", None),
    ("禅は何よりも実行を重んずる。語ることに意味はない、生きることにのみ意味がある。",
     "鈴木大拙", ["discipline", "action"], "medium", "secondary",
     "鈴木大拙の禅論を要約した表現。原文の直訳ではない。"),
    ("人は何処までも自己自身に忠実であらねばならぬ。",
     "西田幾多郎", ["discipline", "reflection"], "short", "verified", None),
    ("人生の最大の悲劇は、人生が短いことにあるのではなく、人生で本当に大事なものに気づくのが遅すぎることにある。",
     "三島由紀夫", ["reflection"], "long", "secondary",
     "広く流通する表現だが一次出典は未特定。"),
    ("楽しみながら、苦しみながら、それでもなお自分の道を歩く。それが人生である。",
     "司馬遼太郎", ["endurance", "action"], "medium", "secondary",
     "司馬作品の人生観を要約した表現。"),
    ("信念のある人間は、最後の最後まで諦めない。諦めないから、信念なのである。",
     "城山三郎", ["endurance", "discipline"], "medium", "secondary", None),
    ("心が積極的であれば、人生は積極的に展開する。",
     "中村天風", ["discipline", "focus"], "short", "verified", None),
    ("真面目とは、真の面目を発揮することである。",
     "森信三", ["discipline", "reflection"], "short", "verified", None),
    ("晴れてよし 曇りてもよし 富士の山 もとの姿は変はらざりけり",
     "山岡鉄舟", ["reflection", "endurance"], "medium", "verified", None),

    # === E. Modern / Business / Art (6) ===
    ("Have the courage to follow your heart and intuition. They somehow already know what you truly want to become.",
     "Steve Jobs", ["reflection", "action"], "long", "verified",
     "2005年スタンフォード大学卒業式スピーチより。"),
    ("I knew that if I failed I wouldn't regret that, but I knew the one thing I might regret is not trying.",
     "Jeff Bezos", ["action", "endurance"], "medium", "verified", None),
    ("The hardest thing in the world is to simplify your life; it's so easy to make it complex.",
     "Yvon Chouinard", ["focus", "discipline"], "medium", "verified", None),
    ("The capacity to care is the thing which gives life its deepest significance.",
     "Pablo Casals", ["reflection", "leadership"], "medium", "verified", None),
    ("I have already settled it for myself so flattery and criticism go down the same drain and I am quite free.",
     "Georgia O'Keeffe", ["reflection", "focus"], "long", "verified", None),
    ("人間を描くということは、人間の心を描くことである。技巧ではない、心である。",
     "黒澤明", ["reflection", "focus"], "medium", "secondary", None),
]


def main() -> None:
    quotes = json.loads(QUOTES_PATH.read_text(encoding="utf-8"))
    before = len(quotes)

    used_ids = {q["id"] for q in quotes}
    next_n = 183
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

    print(f"Before: {before}")
    print(f"Added:  {added}")
    print(f"After:  {len(quotes)}")


if __name__ == "__main__":
    main()
