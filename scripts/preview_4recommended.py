"""MVP V2: 評価の高いスタイル（単純意訳 / 二段構造）で 4 件意訳プロトタイプ生成。

Round 1 (文学/実用 並列評価) + Round 2 (統合判定) の結果採用スタイル:
- TOP 1 = 単純意訳 (両観点 TOP 1)
- TOP 2 = 二段構造 (実用観点 2 位、対比 quote 限定の spice)

bilingual モードで translation_ja を意訳に上書きして生成、output/preview_v2_<qid>.jpg に保存。
"""

import json
import shutil
import sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config_loader import load_config
from src.wallpaper_generator import generate_wallpaper

INTERPRETATIONS_V2 = {
    "q179": "冬の底で、私はついに知った。胸の奥に、消えぬ夏がある。",
    "q198": "水面を眺めるだけでは、向こう岸には届かない。",
    "q177": "努力と勇気だけでは足りない。要るのは目的と方向。",
    "q311": "より良くは可能だ。才能ではない、勤勉さだ。",
}

STYLES_V2 = {
    "q179": "単純意訳",
    "q198": "単純意訳",
    "q177": "二段構造",
    "q311": "二段構造",
}


def main() -> None:
    config = load_config(BASE_DIR)
    quotes_path = BASE_DIR / "quotes.json"
    all_quotes = json.loads(quotes_path.read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in all_quotes}

    today_path = BASE_DIR / "output" / "wallpaper_today.jpg"
    backup_path = BASE_DIR / "output" / "wallpaper_today.original.jpg"

    if today_path.exists():
        shutil.copy(today_path, backup_path)
        print(f"Backup: {backup_path}")

    generated = []
    try:
        for qid, interpretation in INTERPRETATIONS_V2.items():
            if qid not in by_id:
                print(f"WARN: {qid} not found, skipping")
                continue

            q = dict(by_id[qid])
            original_translation = q.get("translation_ja", "(no translation_ja)")
            q["translation_ja"] = interpretation

            output = generate_wallpaper(q, config, BASE_DIR, bilingual=True)
            target = BASE_DIR / "output" / f"preview_v2_{qid}.jpg"
            shutil.move(str(output), str(target))
            generated.append(target)

            print(f"\n[{qid}] {STYLES_V2.get(qid, '?')}")
            print(f"  English   : {q['text']}")
            print(f"  Author    : {q.get('author', '')} ({q.get('author_title_ja', '')})")
            print(f"  直訳 (元): {original_translation}")
            print(f"  意訳 (新): {interpretation}")
            print(f"  Output    : {target}")
    finally:
        if backup_path.exists():
            shutil.move(str(backup_path), str(today_path))
            print(f"\nRestored: {today_path}")

    print(f"\n=== Generated {len(generated)} previews (V2) ===")
    for p in generated:
        print(f"  {p}")


if __name__ == "__main__":
    main()
