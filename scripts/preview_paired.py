"""MVP V4: 同じ名言で単純意訳 / 後半解説調 を両方生成し、ペア比較できるようにする。

ユーザー仮説の検証: シンプルな quote はシンプルに、難解な quote は解説調で補強する。

6 quote × 2 スタイル = 12 枚生成。ファイル名 preview_pair_<qid>_<style>.jpg で
qid ソート時にペアが隣同士に並ぶ。
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

# 6 quote × 2 スタイル = 12 件
# (qid, style) -> interpretation
PAIRED_INTERPRETATIONS: dict[tuple[str, str], str] = {
    # q099 Gandhi (簡単・直球)
    ("q099", "simple"):   "明日死ぬと思って生きよ。永遠に生きると思って学べ。",
    ("q099", "kaisetsu"): "今日を最後の日と思って生きる。学びだけは、終わりを知らぬ者の歩幅で。",

    # q421 Thich Nhat Hanh (簡単・象徴的)
    ("q421", "simple"):   "一歩一歩、大地に口づけするように歩きなさい。",
    ("q421", "kaisetsu"): "大地に口づけするように歩きなさい。踏みしめるのではなく、出会うように。",

    # q072 Mandela (中間)
    ("q072", "simple"):   "人生の輝きは、倒れないことではなく、倒れるたびに立ち上がることに宿る。",
    ("q072", "kaisetsu"): "人生の最大の栄光は、倒れないことにではない。倒れるたびに立ち上がる、その繰り返しにある。",

    # q151 Marcus Aurelius (中間・ストア哲学)
    ("q151", "simple"):   "心は自分のもの、出来事は自分のものではない。そう知るとき、力が生まれる。",
    ("q151", "kaisetsu"): "支配できるのは自分の心だけだ。外の出来事ではなく、内に向けた手綱を握る者に力は宿る。",

    # q232 Rilke (難解・抽象詩)
    ("q232", "simple"):   "心のなかの解けないものすべてに、辛抱強くあれ。問いそのものを、いとおしむように。",
    ("q232", "kaisetsu"): "心の解けないものすべてに、辛抱強くあれ。問いは、答えよりも長く人を育てる。",

    # q439 Nietzsche (難解・隠喩)
    ("q439", "simple"):   "踊る星を産み落とすには、まだ胸の内に混沌を抱えていなければならない。",
    ("q439", "kaisetsu"): "踊る星を生むには、胸の内に混沌を抱いていなければならない。秩序だけからは、何も踊り出さない。",
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
        for (qid, style), interpretation in PAIRED_INTERPRETATIONS.items():
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

    print(f"\n=== Generated {len(generated)} / 12 paired previews ===")
    print("\nファイル名で sort すれば qid ペアが隣同士に並びます:")
    print("  preview_pair_q072_kaisetsu.jpg")
    print("  preview_pair_q072_simple.jpg   ← Mandela ペア")
    print("  preview_pair_q099_kaisetsu.jpg")
    print("  preview_pair_q099_simple.jpg   ← Gandhi ペア")
    print("  ...")


if __name__ == "__main__":
    main()
