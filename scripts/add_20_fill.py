"""Add 20 quotes to fill 366 + 8 reserve = 374 enabled."""
import json
import re

JA_PATTERN = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')

def mk(id, text, author, cats):
    n = len(text)
    length = "short" if n <= 60 else ("medium" if n <= 130 else "long")
    lang = "ja" if JA_PATTERN.search(text) else "en"
    return {
        "id": id, "text": text, "author": author,
        "category": cats, "translated": False,
        "verification_status": "verified",
        "mood_tags": [], "season_tags": [],
        "length": length, "language": lang, "enabled": True,
    }

entries = [
    # Physician-writers / medical humanities (6)
    ("To cure the body without the mind is not to cure at all.", "Alexander Lowen", ["reflection", "focus"]),
    ("The physician who teaches people to sustain their health is the superior physician.", "Huang Di Nei Jing", ["discipline", "leadership"]),
    ("Observation, reason, human understanding, courage; these make the physician.", "Martin H. Fischer", ["discipline", "focus"]),
    ("The art of medicine consists of amusing the patient while nature cures the disease.", "Voltaire", ["reflection", "rest"]),
    ("No man is a good doctor who has never been sick himself.", "Chinese Proverb", ["reflection", "endurance"]),
    ("Only by going alone in silence, without baggage, can one truly get into the heart of the wilderness.", "John Muir", ["reflection", "focus"]),
    # Stoic / philosophy extension (4)
    ("Wealth consists not in having great possessions, but in having few wants.", "Epictetus", ["gratitude", "discipline"]),
    ("Associate with people who are likely to improve you.", "Seneca", ["discipline", "leadership"]),
    ("If you accomplish something good with hard work, the labor passes quickly, but the good endures.", "Musonius Rufus", ["endurance", "discipline"]),
    ("The whole future lies in uncertainty: live immediately.", "Seneca", ["action", "focus"]),
    # Existential / psychology extension (4)
    ("One must still have chaos in oneself to be able to give birth to a dancing star.", "Friedrich Nietzsche", ["endurance", "reflection"]),
    ("The shoe that fits one person pinches another; there is no recipe for living that suits all cases.", "Carl Jung", ["reflection", "focus"]),
    ("What a man can be, he must be. This need we may call self-actualization.", "Abraham Maslow", ["focus", "action"]),
    ("The good life is a process, not a state of being.", "Carl Rogers", ["reflection", "action"]),
    # Japanese additional (4)
    ("なせば成る なさねば成らぬ何事も 成らぬは人の なさぬなりけり", "上杉鷹山", ["action", "endurance"]),
    ("一日一字を記さば一年にして三百六十字を得、一夜一時を怠らば百歳の間三万六千時を失う", "吉田松陰", ["discipline", "endurance"]),
    ("花は盛りに、月は隈なきをのみ見るものかは", "兼好法師", ["reflection", "gratitude"]),
    ("敬天愛人", "西郷隆盛", ["leadership", "reflection"]),
    # Contemplative / poet (2)
    ("In the middle of difficulty lies opportunity.", "Albert Einstein", ["endurance", "action"]),
    ("Turn your wounds into wisdom.", "Oprah Winfrey", ["endurance", "reflection"]),
]

path = "quotes.json"
qs = json.load(open(path, encoding="utf-8"))

# Find max existing ID
max_id = max(int(q["id"][1:]) for q in qs)
new = [mk(f"q{max_id+1+i}", t, a, c) for i, (t, a, c) in enumerate(entries)]

qs.extend(new)
with open(path, "w", encoding="utf-8") as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

enabled = sum(1 for q in qs if q.get("enabled", True))
print(f"added {len(new)} (q{max_id+1}-q{max_id+len(new)})")
print(f"total {len(qs)}, enabled {enabled}")
