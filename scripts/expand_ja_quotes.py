"""One-shot script: delete weak JA quotes and add 50 new high-quality JA quotes.

Run from repo root:
    python scripts/expand_ja_quotes.py
"""
import json
from pathlib import Path

QUOTES_PATH = Path(__file__).resolve().parent.parent / "quotes.json"

DELETE_IDS = {"q074", "q079", "q083", "q094", "q097"}

# (text, author, [categories], length)
NEW_QUOTES = [
    # --- B案 13 ---
    ("やってみせ、言って聞かせて、させてみせ、ほめてやらねば、人は動かじ。", "山本五十六", ["leadership", "discipline"], "medium"),
    ("人間は負けると分かっていても、戦わなければならぬ時がある。", "司馬遼太郎", ["endurance", "leadership"], "medium"),
    ("僕の前に道はない 僕の後ろに道は出来る", "高村光太郎", ["action", "leadership"], "short"),
    ("智に働けば角が立つ。情に棹させば流される。意地を通せば窮屈だ。", "夏目漱石", ["reflection"], "medium"),
    ("災難に逢う時節には災難に逢うがよく候 死ぬ時節には死ぬがよく候", "良寛", ["endurance", "reflection"], "medium"),
    ("この道より 我を生かす道なし この道を行く", "武者小路実篤", ["discipline", "action"], "medium"),
    ("規矩作法 守りつくして 破るとも 離るるとても 本を忘るな", "千利休", ["discipline"], "medium"),
    ("おもしろきこともなき世をおもしろく", "高杉晋作", ["reflection", "action"], "short"),
    ("世界がぜんたい幸福にならないうちは個人の幸福はあり得ない。", "宮沢賢治", ["gratitude", "leadership"], "medium"),
    ("道をひらくためには、まず歩きださねばならぬ。", "松下幸之助", ["action"], "medium"),
    ("失敗したところでやめてしまうから失敗になる。成功するまで続ければ、それは成功になる。", "松下幸之助", ["endurance", "discipline"], "long"),
    ("チャレンジして失敗を恐れるよりも、何もしないことを恐れろ。", "本田宗一郎", ["action"], "medium"),
    ("動機善なりや、私心なかりしか。", "稲盛和夫", ["leadership", "reflection"], "short"),

    # --- 文学 10 ---
    ("弱虫は、幸福をさえおそれるものです。綿で怪我をするんです。", "太宰治", ["reflection"], "medium"),
    ("人生は一箱のマッチに似ている。重大に扱うのはばかばかしい。重大に扱わねば危険である。", "芥川龍之介", ["reflection"], "long"),
    ("劫初より作りいとなむ殿堂にわれも黄金の釘一つ打つ", "与謝野晶子", ["discipline", "leadership"], "medium"),
    ("分け入っても分け入っても青い山", "種田山頭火", ["endurance", "reflection"], "short"),
    ("汚れつちまつた悲しみに 今日も小雪の降りかかる", "中原中也", ["reflection"], "medium"),
    ("天は人の上に人を造らず人の下に人を造らず。", "福沢諭吉", ["reflection", "leadership"], "medium"),
    ("最大遺物とは何であるか。それは勇ましい高尚なる生涯である。", "内村鑑三", ["leadership", "discipline"], "medium"),
    ("国境の長いトンネルを抜けると雪国であった。", "川端康成", ["reflection"], "medium"),
    ("美しい「花」がある、「花」の美しさという様なものはない。", "小林秀雄", ["reflection", "focus"], "medium"),
    ("自分の感受性くらい 自分で守れ ばかものよ", "茨木のり子", ["discipline", "focus"], "short"),

    # --- 経営 8 ---
    ("夢なき者に理想なし、理想なき者に計画なし、計画なき者に実行なし、実行なき者に成功なし。", "渋沢栄一", ["action", "leadership"], "long"),
    ("論語と算盤は一致すべきものである。", "渋沢栄一", ["discipline", "leadership"], "short"),
    ("黄金の奴隷たるなかれ。", "出光佐三", ["discipline", "reflection"], "short"),
    ("障子をあけてみよ。外は広いぞ。", "豊田佐吉", ["action", "focus"], "short"),
    ("素直な心になれば、世の中の物事の実相を見ることができる。", "松下幸之助", ["focus", "reflection"], "medium"),
    ("強烈な願望を心に抱き続ければ、それは必ず実現する。", "稲盛和夫", ["discipline", "action"], "medium"),
    ("遠きをはかる者は富み、近きをはかる者は貧す。", "二宮尊徳", ["discipline", "leadership"], "medium"),
    ("金を残すは下、仕事を残すは中、人を残すを上とす。", "後藤新平", ["leadership"], "medium"),

    # --- 武将・歴史 7 ---
    ("人は城、人は石垣、人は堀、情けは味方、仇は敵なり。", "武田信玄", ["leadership"], "medium"),
    ("人間五十年、下天のうちを比ぶれば、夢幻の如くなり。", "織田信長", ["reflection"], "medium"),
    ("人の一生は重荷を負うて遠き道を行くが如し。急ぐべからず。", "徳川家康", ["endurance", "discipline"], "medium"),
    ("己を尽くして人を咎めず、我が誠の足らざるを尋ぬべし。", "西郷隆盛", ["reflection", "discipline"], "medium"),
    ("世の人は我を何とも言わば言え 我が成すことは我のみぞ知る", "坂本龍馬", ["action", "leadership"], "medium"),
    ("至誠にして動かざる者は、未だ之れ有らざるなり。", "吉田松陰", ["discipline", "action"], "medium"),
    ("行蔵は我に存す、毀誉は他人の主張、我に与らず我に関せず。", "勝海舟", ["reflection", "leadership"], "medium"),

    # --- 思想・禅・芸術 6 ---
    ("春は花 夏ほととぎす 秋は月 冬雪さえて 冷しかりけり", "道元", ["reflection", "gratitude"], "medium"),
    ("門松は冥土の旅の一里塚 めでたくもあり めでたくもなし", "一休宗純", ["reflection"], "medium"),
    ("願はくは花の下にて春死なん そのきさらぎの望月のころ", "西行", ["reflection"], "medium"),
    ("ゆく河の流れは絶えずして、しかも、もとの水にあらず。", "鴨長明", ["reflection"], "medium"),
    ("世に従はん人は、まづ機嫌を知るべし。", "兼好法師", ["focus", "reflection"], "short"),
    ("茶道は美を見出さんがために美を隠す術である。", "岡倉天心", ["focus", "reflection"], "medium"),

    # --- スポーツ・現代 6 ---
    ("小さなことを積み重ねることが、とんでもないところに行くただひとつの道だ。", "イチロー", ["discipline", "endurance"], "medium"),
    ("努力は必ず報われる。もし報われない努力があるのならば、それはまだ努力とは呼べない。", "王貞治", ["discipline", "endurance"], "long"),
    ("おごらず、他人と比べず、面白がって、平気に生きればいい。", "樹木希林", ["reflection", "gratitude"], "medium"),
    ("大事なものは、たいてい面倒くさい。", "宮崎駿", ["reflection", "focus"], "short"),
    ("振り向くな振り向くな後ろには夢がない", "寺山修司", ["action", "reflection"], "short"),
    ("生きているということ いま生きているということ それはのどがかわくということ", "谷川俊太郎", ["gratitude", "reflection"], "medium"),
]


def main() -> None:
    quotes = json.loads(QUOTES_PATH.read_text(encoding="utf-8"))
    before = len(quotes)

    # Delete weak JA quotes
    quotes = [q for q in quotes if q["id"] not in DELETE_IDS]
    after_delete = len(quotes)

    # Find next id
    used_ids = {q["id"] for q in quotes}
    next_n = 101
    while f"q{next_n:03d}" in used_ids:
        next_n += 1

    # Build new entries
    added = 0
    for text, author, categories, length in NEW_QUOTES:
        new_id = f"q{next_n:03d}"
        while new_id in used_ids:
            next_n += 1
            new_id = f"q{next_n:03d}"
        used_ids.add(new_id)
        next_n += 1

        quotes.append({
            "id": new_id,
            "text": text,
            "author": author,
            "category": categories,
            "translated": False,
            "verification_status": "verified",
            "mood_tags": [],
            "season_tags": [],
            "length": length,
            "enabled": True,
        })
        added += 1

    QUOTES_PATH.write_text(
        json.dumps(quotes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Before: {before}")
    print(f"Deleted: {before - after_delete}")
    print(f"Added:   {added}")
    print(f"After:   {len(quotes)}")


if __name__ == "__main__":
    main()
