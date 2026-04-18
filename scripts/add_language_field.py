"""Add 'language' field to all quotes in quotes.json.

Rules:
- If text contains Japanese characters (hiragana/katakana/kanji) → "ja"
- Otherwise → "en"
- Does NOT modify 'translated' field (kept for backward compat)
"""

import json
import re
import sys

JA_PATTERN = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')

# Manual overrides: quote_id → language
OVERRIDES: dict[str, str] = {}

def detect_language(text: str) -> str:
    return "ja" if JA_PATTERN.search(text) else "en"

def main():
    path = "quotes.json"
    with open(path, encoding="utf-8") as f:
        quotes = json.load(f)

    ja_count = 0
    en_count = 0
    changed = 0

    for q in quotes:
        qid = q.get("id", "")
        if qid in OVERRIDES:
            lang = OVERRIDES[qid]
        else:
            lang = detect_language(q.get("text", ""))

        if q.get("language") != lang:
            changed += 1
        q["language"] = lang

        if lang == "ja":
            ja_count += 1
        else:
            en_count += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=2)

    print(f"total:   {len(quotes)}")
    print(f"ja:      {ja_count}")
    print(f"en:      {en_count}")
    print(f"changed: {changed}")

if __name__ == "__main__":
    main()
