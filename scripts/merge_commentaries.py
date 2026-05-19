"""4 chunk の本番出力とパイロット 50 件を統合し、quotes.json を更新する。

入力:
- ~/.cache/wallpaper_production/chunk_{1-4}_output.json (本番 265 件)
- ハードコード: パイロット 50 件 (Round 6 改善版含む)

出力:
- ~/.cache/wallpaper_production/commentary_v1_complete.json (統合 dict、検証用)
- ~/daily_wallpaper/quotes.backup.20260519.json (バックアップ)
- ~/daily_wallpaper/quotes.json (commentary_ja / commentary_style 追加)
"""

import json
import shutil
import sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = Path.home() / ".cache" / "wallpaper_production"

# パイロット 50 件 (最終確定版)
PILOT_50 = {
    # パイロット 20 件 (Round 6 改善版含む)
    "q078": ("kaisetsu", "傷ついた場所こそ、光が射し入る入り口。痛みの隙間から、世界はあなたを照らす。"),
    "q186": ("kaisetsu", "同じ川に二度入ることはできない。流れも人も、すでに別物になっている。"),
    "q237": ("kaisetsu", "やってみた。失敗した。構わない、もう一度。失敗の質を、すこしずつ磨いてゆく。"),
    "q243": ("kaisetsu", "人に注意を向けること。それは、もっとも稀で純粋な、贈与のかたち。"),
    "q258": ("kaisetsu", "あなたという空。喜びも悲しみも、ただ流れてゆく天気にすぎない。"),
    "q280": ("kaisetsu", "無意識に気づかぬうちは、それが人生を動かす。人はそれをやがて、運命と呼ぶ。"),
    "q392": ("kaisetsu", "私たちにできるのは、試みること、それだけ。結果は、もう私たちの領分ではない。"),
    "q191": ("kaisetsu", "あなたを脅かす竜は、姫の化身かもしれない。勇気ある一歩を、ただ待っている。"),
    "q184": ("kaisetsu", "挑むとは、一瞬足場を失うこと。挑まぬとは、自分そのものを失うこと。"),
    "q409": ("kaisetsu", "真に生きるとは、誰かと出会うこと。出会いの外側に、生はない。"),
    "q005": ("simple", "人は繰り返す行いそのものである。だから卓越とは行為ではなく、習慣だ。"),
    "q014": ("simple", "感謝とは、いま手にあるものを、足ると言い直すこと。"),
    "q018": ("simple", "戦いが厳しいほど、勝ちとった日の手応えは深い。"),
    "q024": ("simple", "努力は裏切らない。ただし、正しい方角に進んでいる場合にかぎる。"),
    "q040": ("simple", "さまよう者がみな、道に迷っているわけではない。"),
    "q045": ("simple", "千里の旅も、足元のたった一歩から始まる。"),
    "q057": ("simple", "いまこの瞬間は、よろこびに満ちている。気づく人にだけ、それは姿を現す。"),
    "q065": ("simple", "始めるには、語るのをやめて、まず動き出すこと。"),
    "q063": ("simple", "人生とは、別の予定を立てている間に、起きてしまっているものだ。"),
    "q088": ("simple", "内側で成し遂げたものが、やがて外の世界をかたちづくる。"),

    # パイロット 30 件 (境界 3 件は新ルール反映版)
    "q250": ("kaisetsu", "すぐそばから始まる。二歩目でも三歩目でもなく、避けてきた最初の一歩こそが入口になる。"),
    "q259": ("kaisetsu", "自由を求めて胸が疼くなら、その音に耳を澄ませよ。願いは声になる前から、最初に動いている。"),
    "q263": ("kaisetsu", "信仰とは、心が静かに彼方へと傾くその動きにすぎない——だがそれが、すべて。"),
    "q395": ("kaisetsu", "愛とは、自分以外も確かに在ると気づく難しさだ。他者を風景にせず、輪郭ごと迎え入れる作業。"),
    "q412": ("kaisetsu", "哲学とは、答えに着くことではなく、問いの途上にあることだ。歩き続ける姿勢が、答えより深い。"),
    "q190": ("kaisetsu", "生きるとは変わること、変わるとは自分を作り続けることだ。完成形はなく、進行形のままが本来の姿。"),
    "q238": ("kaisetsu", "旅人よ、道はない。歩いた跡が道になる。地図を待たず、最初の一歩がそのまま地面を引く。"),
    "q310": ("kaisetsu", "完璧には届かない。それでも、近づき続けることはできる。その歩みそのものが人を磨く。"),
    "q386": ("kaisetsu", "大きな知性と深い心には、痛みは避けがたい。鈍さで身を守るより、痛みを受けて器が広がる。"),
    "q416": ("kaisetsu", "どこに目を向けても、世界は変容のように輝きうる。必要なのは見ようとする、ほんの少しの構え。"),
    "q152": ("simple", "苦しみの多くは、現実より想像の中にある。"),
    "q154": ("simple", "状況を変えられぬとき、問われるのは自分の変容だ。"),
    "q305": ("simple", "良き医師は病を診、優れた医師は病を負う人を診る。"),
    "q230": ("simple", "最も大いなることは、自分自身に帰属する術を知ること。"),
    "q309": ("simple", "私の成功は、言い訳を渡さず受け取らなかったことに尽きる。"),
    "q025": ("simple", "今いる場所で、あるもので、できることをせよ。"),
    "q033": ("simple", "苦難はしばしば、平凡な人を稀な運命へと整える。"),
    "q061": ("simple", "明日の実現を阻む唯一の壁は、今日抱く疑念である。"),
    "q308": ("simple", "あなたはあなたであるゆえに大切。生の終わりまで、ずっと。"),
    "q312": ("simple", "恐れがないとは言えない。それでも胸を満たすのは感謝だ。"),
    "q314": ("simple", "ありのままの自分を受け入れたとき、人は初めて変わる。"),
    "q015": ("simple", "前へ進む秘訣は、ただひとつ、始めることに尽きる。"),
    "q019": ("simple", "大抵のものは数分電源を抜けば動き出す。あなたも例外ではない。"),
    "q035": ("simple", "自分の行いが世界を変えると信じて動け。実際にそうなる。"),
    "q039": ("simple", "吟味されることのない人生は、生きるに値しない。"),
    "q200": ("simple", "立ち止まり恐れと向き合うたび、力と勇気と自信は育つ。"),
    "q265": ("simple", "望んだ手札を引く権利はない。配られた札を全力で切る義務だけがある。"),
    "q360": ("simple", "絶望のとき黙って隣にいてくれる人こそ、真の友だ。"),
    "q366": ("simple", "人間存在の問いに対する、健やかな答えはただ愛だけだ。"),
    "q254": ("simple", "人生に予定を告げる前に、人生があなたに望むことを聴け。"),
}


def main() -> None:
    all_commentaries: dict[str, dict] = {}

    # パイロット 50 件を統合
    for qid, (style, commentary) in PILOT_50.items():
        all_commentaries[qid] = {
            "style": style,
            "commentary_ja": commentary,
        }
    print(f"Pilot 50 added: {len(PILOT_50)}")

    # 4 chunk を統合
    chunk_total = 0
    for i in range(1, 5):
        chunk_path = CACHE_DIR / f"chunk_{i}_output.json"
        with open(chunk_path, encoding="utf-8") as f:
            chunk_data = json.load(f)
        for item in chunk_data:
            qid = item["id"]
            if qid in all_commentaries:
                print(f"  WARN: {qid} already in commentaries (chunk {i})")
                continue
            all_commentaries[qid] = {
                "style": item["style"],
                "commentary_ja": item["commentary_ja"],
            }
            chunk_total += 1
        print(f"Chunk {i} added: {len(chunk_data)}")

    print(f"\nTotal commentaries: {len(all_commentaries)}")
    print(f"  Pilot 50 + Chunks {chunk_total} = expected {50 + chunk_total}")

    # スタイル集計
    style_count = {"simple": 0, "kaisetsu": 0}
    for v in all_commentaries.values():
        style_count[v["style"]] += 1
    print(f"  simple: {style_count['simple']}")
    print(f"  kaisetsu: {style_count['kaisetsu']}")

    # 統合 dict を保存
    merged_path = CACHE_DIR / "commentary_v1_complete.json"
    with open(merged_path, "w", encoding="utf-8") as f:
        json.dump(all_commentaries, f, ensure_ascii=False, indent=2)
    print(f"\nMerged saved: {merged_path}")

    # quotes.json バックアップ
    quotes_path = BASE_DIR / "quotes.json"
    backup_path = BASE_DIR / "quotes.backup.20260519.json"
    shutil.copy(quotes_path, backup_path)
    print(f"Backup: {backup_path}")

    # quotes.json 更新
    with open(quotes_path, encoding="utf-8") as f:
        quotes = json.load(f)

    updated_count = 0
    not_in_quotes = []
    for q in quotes:
        qid = q["id"]
        if qid in all_commentaries:
            q["commentary_ja"] = all_commentaries[qid]["commentary_ja"]
            q["commentary_style"] = all_commentaries[qid]["style"]
            updated_count += 1

    # all_commentaries に含まれるが quotes に無い ID をチェック
    quote_ids = {q["id"] for q in quotes}
    for qid in all_commentaries:
        if qid not in quote_ids:
            not_in_quotes.append(qid)

    # 一時ファイル → rename で atomic write
    tmp_path = quotes_path.with_suffix(".tmp.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=2)
    tmp_path.replace(quotes_path)
    print(f"\nquotes.json updated:")
    print(f"  total quotes: {len(quotes)}")
    print(f"  updated with commentary: {updated_count}")
    if not_in_quotes:
        print(f"  WARN: commentaries but not in quotes.json: {not_in_quotes}")

    # 字数サマリ
    print(f"\n字数サマリ:")
    simple_lens = []
    kaisetsu_lens = []
    for v in all_commentaries.values():
        l = len(v["commentary_ja"])
        if v["style"] == "simple":
            simple_lens.append(l)
        else:
            kaisetsu_lens.append(l)
    if simple_lens:
        print(f"  simple: min={min(simple_lens)} max={max(simple_lens)} avg={sum(simple_lens)/len(simple_lens):.1f}")
    if kaisetsu_lens:
        print(f"  kaisetsu: min={min(kaisetsu_lens)} max={max(kaisetsu_lens)} avg={sum(kaisetsu_lens)/len(kaisetsu_lens):.1f}")

    # 字数違反チェック
    violations = []
    for qid, v in all_commentaries.items():
        l = len(v["commentary_ja"])
        if v["style"] == "simple" and not (20 <= l <= 45):
            violations.append(f"{qid} simple {l}字")
        if v["style"] == "kaisetsu" and not (30 <= l <= 55):
            violations.append(f"{qid} kaisetsu {l}字")
    if violations:
        print(f"\n字数違反 {len(violations)} 件:")
        for v in violations[:10]:
            print(f"  {v}")


if __name__ == "__main__":
    main()
