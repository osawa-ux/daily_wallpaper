"""MVP: 5 つの名言で意訳和訳プロトタイプを生成する。

bilingual モードの translation_ja を意訳に置き換えて、既存の generate_wallpaper
の位置・フォントで描画する。5 つの異なるスタイルで意訳を試す。

各 quote について:
1. quote dict をコピーして translation_ja を意訳で上書き
2. generate_wallpaper(bilingual=True) で生成
3. output/wallpaper_today.jpg として書き出される
4. preview_5quotes_<qid>.jpg にリネーム

wallpaper_today.jpg は事前にバックアップ → 終了時に復元する。
"""

import json
import shutil
import sys
from pathlib import Path

# Windows console: UTF-8
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config_loader import load_config
from src.wallpaper_generator import generate_wallpaper

# 5 つの意訳（subagent 生成、各スタイル違い）
INTERPRETATIONS = {
    "q003": "未来とは予測すべきものではない。自らの手で築き上げてゆくものだ。",  # 二段構造
    "q229": "変わるのは我々のほうだ。物事はそのままに、見る者の心が世界を別物にする。",  # 後半解説調
    "q235": "かつて愛した人が、闇に満ちた箱をくれた。それも贈り物だったと気づくのに、長い年月を要した。",  # 単純意訳
    "q221": "行く手を阻むもの、それすなわち道。妨げこそが、進むべき径となる。",  # 体言止め
    "q009": "歩みの遅さは問題にならぬ。立ち止まらぬ者として在り続ける限りは。",  # 補強助詞
}

STYLE_LABELS = {
    "q003": "二段構造",
    "q229": "後半解説調",
    "q235": "単純意訳",
    "q221": "体言止め",
    "q009": "補強助詞",
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
        for qid, interpretation in INTERPRETATIONS.items():
            if qid not in by_id:
                print(f"WARN: {qid} not found in quotes.json, skipping")
                continue

            q = dict(by_id[qid])
            original_translation = q.get("translation_ja", "(no translation_ja)")
            q["translation_ja"] = interpretation

            output = generate_wallpaper(q, config, BASE_DIR, bilingual=True)
            target = BASE_DIR / "output" / f"preview_5quotes_{qid}.jpg"
            shutil.move(str(output), str(target))
            generated.append(target)

            print(f"\n[{qid}] {STYLE_LABELS.get(qid, '?')}")
            print(f"  English   : {q['text']}")
            print(f"  Author    : {q.get('author', '')} ({q.get('author_title_ja', '')})")
            print(f"  直訳 (元): {original_translation}")
            print(f"  意訳 (新): {interpretation}")
            print(f"  Output    : {target}")
    finally:
        if backup_path.exists():
            shutil.move(str(backup_path), str(today_path))
            print(f"\nRestored: {today_path}")

    print(f"\n=== Generated {len(generated)} previews ===")
    for p in generated:
        print(f"  {p}")


if __name__ == "__main__":
    main()
