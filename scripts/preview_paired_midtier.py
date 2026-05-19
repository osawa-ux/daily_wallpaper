"""MVP V5: 中間ゾーン 5 quote × 2 スタイル = 10 枚追加生成。

既存 preview_paired.py の 12 枚 (q072/q099/q151/q232/q421/q439) と合わせて
合計 22 枚で仮説検証の解像度を上げる。

ファイル命名は preview_pair_<qid>_<style>.jpg で既存と統一。
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

# 5 quote × 2 スタイル = 10 件 (既存 v3 + 新規追加)
PAIRED_MIDTIER: dict[tuple[str, str], str] = {
    # q161 Hemingway (現実的だが哲学含意)
    ("q161", "simple"):   "世界はあらゆる人を打ち砕く。やがて多くの者は、その砕かれた場所でこそ強くなる。",
    ("q161", "kaisetsu"): "世界は誰をも打ち砕く。砕かれた跡こそが、後に人を支える芯となる。",

    # q091 Steve Jobs (現代・断言・抽象)
    ("q091", "simple"):   "革新こそが、率いる者と従う者とを隔てる一線である。",
    ("q091", "kaisetsu"): "革新がリーダーと追随者を分ける。境界線は、生み出す側に立てるかどうかだ。",

    # q050 Einstein (抽象的・教訓)
    ("q050", "simple"):   "成功する者となるよりも、価値ある者となろうと努めよ。",
    ("q050", "kaisetsu"): "成功者ではなく、価値ある者であろうと努めよ。残るのは、結果よりも為したことの中身だ。",

    # q021 Churchill (リズム・断言)
    ("q021", "simple"):   "成功は最終ではなく、失敗も致命ではない。要は、続ける勇気である。",
    ("q021", "kaisetsu"): "成功は終点ではなく、失敗も終わりではない。問われるのは、それでも続ける勇気である。",

    # q298 Thoreau (詩的・隠喩)
    ("q298", "simple"):   "仲間と歩調が合わない者がいる。きっと、別の太鼓の音が聞こえているのだ。",
    ("q298", "kaisetsu"): "歩調を合わせられぬ者がいる。その人は、別の鼓動を聴いて歩んでいる。",
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

    generated: list[Path] = []
    try:
        for (qid, style), interpretation in PAIRED_MIDTIER.items():
            if qid not in by_id:
                print(f"WARN: {qid} not found, skipping")
                continue

            q = dict(by_id[qid])
            q["translation_ja"] = interpretation

            output = generate_wallpaper(q, config, BASE_DIR, bilingual=True)
            target = BASE_DIR / "output" / f"preview_pair_{qid}_{style}.jpg"
            shutil.move(str(output), str(target))
            generated.append(target)

            author = q.get("author", "")
            print(f"[{qid} / {style:8s}] {author}")
            print(f"  {interpretation}")
            print(f"  → {target.name}")
    finally:
        if backup_path.exists():
            shutil.move(str(backup_path), str(today_path))
            print(f"\nRestored: {today_path}")

    print(f"\n=== Generated {len(generated)} / 10 midtier paired previews ===")
    print("既存 12 枚と合わせて、output/preview_pair_*.jpg = 計 22 枚")


if __name__ == "__main__":
    main()
