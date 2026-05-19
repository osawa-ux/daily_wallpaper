"""MVP V3: 20 件比較プレビュー生成。

単純意訳 10 件 + 後半解説調 10 件をそれぞれ別ファイルとして出力し、
ユーザーが output ディレクトリで見比べて好みのスタイルを判定する。

出力ファイル命名:
- output/preview_v3_simple_<qid>.jpg (単純意訳)
- output/preview_v3_kaisetsu_<qid>.jpg (後半解説調)

wallpaper_today.jpg は事前バックアップ、終了時に復元。
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

INTERPRETATIONS_V3 = {
    # 単純意訳 10 件
    "q197": "顔をいつも陽のほうへ向けていなさい。影は、自然と背中の側に落ちていく。",
    "q232": "心のなかの解けないものすべてに、辛抱強くあれ。問いそのものを、いとおしむように。",
    "q236": "希望とは羽あるもの。魂に降りて、言葉なき歌を口ずさみ、決して止むことがない。",
    "q161": "世界はあらゆる人を打ち砕く。やがて多くの者は、その砕かれた場所でこそ強くなる。",
    "q082": "人生について学んだことを三語で言うなら――それでも、続いていく。",
    "q421": "一歩一歩、大地に口づけするように歩きなさい。",
    "q099": "明日死ぬと思って生きよ。永遠に生きると思って学べ。",
    "q298": "仲間と歩調が合わない者がいる。きっと、別の太鼓の音が聞こえているのだ。",
    "q439": "踊る星を産み落とすには、まだ胸の内に混沌を抱えていなければならない。",
    "q042": "背後にあるものも、行く手にあるものも、内にあるものに比べれば取るに足らない。",
    # 後半解説調 10 件
    "q151": "支配できるのは自分の心だけだ。外の出来事ではなく、内に向けた手綱を握る者に力は宿る。",
    "q091": "革新がリーダーと追随者を分ける。境界線は、生み出す側に立てるかどうかだ。",
    "q050": "成功者ではなく、価値ある者であろうと努めよ。残るのは、結果よりも為したことの中身だ。",
    "q156": "私は過去に起きたことではない。これから何になるかを、自分で選んだ者である。",
    "q333": "人を乱すのは出来事ではない。出来事をどう見たかが、心の波を立てるのだ。",
    "q072": "人生の最大の栄光は、倒れないことにではない。倒れるたびに立ち上がる、その繰り返しにある。",
    "q021": "成功は終点ではなく、失敗も終わりではない。問われるのは、それでも続ける勇気である。",
    "q163": "完璧とは、加えるものが尽きたときではない。削るものが、もう残っていないときに訪れる。",
    "q007": "簡潔さこそ、究極の洗練である。余分を削ぎ落とした先に、本物の品格が立つ。",
    "q289": "意味を決めるのは状況ではない。状況に与えた意味が、やがて自分自身の輪郭を決めていく。",
}

STYLES_V3 = {
    "q197": "単純意訳", "q232": "単純意訳", "q236": "単純意訳", "q161": "単純意訳", "q082": "単純意訳",
    "q421": "単純意訳", "q099": "単純意訳", "q298": "単純意訳", "q439": "単純意訳", "q042": "単純意訳",
    "q151": "後半解説調", "q091": "後半解説調", "q050": "後半解説調", "q156": "後半解説調", "q333": "後半解説調",
    "q072": "後半解説調", "q021": "後半解説調", "q163": "後半解説調", "q007": "後半解説調", "q289": "後半解説調",
}

PREFIX = {
    "単純意訳": "simple",
    "後半解説調": "kaisetsu",
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

    generated_simple: list[Path] = []
    generated_kaisetsu: list[Path] = []
    not_found: list[str] = []

    try:
        for i, (qid, interpretation) in enumerate(INTERPRETATIONS_V3.items(), 1):
            if qid not in by_id:
                not_found.append(qid)
                print(f"[{i:02d}/20] WARN: {qid} not found in quotes.json, skipping")
                continue

            style = STYLES_V3.get(qid, "unknown")
            prefix = PREFIX.get(style, "unknown")

            q = dict(by_id[qid])
            q["translation_ja"] = interpretation

            output = generate_wallpaper(q, config, BASE_DIR, bilingual=True)
            target = BASE_DIR / "output" / f"preview_v3_{prefix}_{qid}.jpg"
            shutil.move(str(output), str(target))

            if style == "単純意訳":
                generated_simple.append(target)
            else:
                generated_kaisetsu.append(target)

            author = q.get("author", "")
            title = q.get("author_title_ja", "")
            print(f"[{i:02d}/20] {style:7s} {qid} {author} ({title})")
            print(f"        → {target.name}")
    finally:
        if backup_path.exists():
            shutil.move(str(backup_path), str(today_path))
            print(f"\nRestored: {today_path}")

    print(f"\n=== Generated {len(generated_simple) + len(generated_kaisetsu)} / 20 previews (V3) ===")
    print(f"\n単純意訳 ({len(generated_simple)}):")
    for p in generated_simple:
        print(f"  {p.name}")
    print(f"\n後半解説調 ({len(generated_kaisetsu)}):")
    for p in generated_kaisetsu:
        print(f"  {p.name}")
    if not_found:
        print(f"\nNot found: {not_found}")


if __name__ == "__main__":
    main()
