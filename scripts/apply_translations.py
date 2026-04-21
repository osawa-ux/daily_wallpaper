"""Apply translation_ja and author_title_ja to quotes.json.

Usage:
    python scripts/apply_translations.py data.json

data.json format:
    { "q004": { "translation_ja": "...", "author_title_ja": "..." }, ... }

Preserves existing field ordering and only modifies targeted quotes.
Skips any quote where translation_ja/author_title_ja already present (non-empty).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def apply(data_path: Path) -> None:
    quotes_path = BASE / "quotes.json"
    quotes = json.loads(quotes_path.read_text(encoding="utf-8"))
    mapping = json.loads(data_path.read_text(encoding="utf-8"))

    by_id = {q["id"]: q for q in quotes}

    added_tr = 0
    added_title = 0
    skipped = []
    unknown = []

    for qid, fields in mapping.items():
        if qid not in by_id:
            unknown.append(qid)
            continue
        q = by_id[qid]
        tr = (fields.get("translation_ja") or "").strip()
        title = (fields.get("author_title_ja") or "").strip()

        if tr and not (q.get("translation_ja") or "").strip():
            # Insert translation_ja right after "text" for readability
            new_q = {}
            for k, v in q.items():
                new_q[k] = v
                if k == "text":
                    new_q["translation_ja"] = tr
            q.clear()
            q.update(new_q)
            added_tr += 1
        elif tr:
            skipped.append(f"{qid}:tr-already-set")

        if title and q.get("author", "").strip():
            if not (q.get("author_title_ja") or "").strip():
                # Insert author_title_ja right after "author"
                new_q = {}
                for k, v in q.items():
                    new_q[k] = v
                    if k == "author":
                        new_q["author_title_ja"] = title
                q.clear()
                q.update(new_q)
                added_title += 1
            else:
                skipped.append(f"{qid}:title-already-set")

    quotes_path.write_text(
        json.dumps(quotes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Added translation_ja: {added_tr}")
    print(f"Added author_title_ja: {added_title}")
    if skipped:
        print(f"Skipped (already set): {len(skipped)}")
    if unknown:
        print(f"Unknown quote ids: {unknown}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/apply_translations.py <data.json>")
        sys.exit(1)
    apply(Path(sys.argv[1]))
