# Daily Minimal English Quote Wallpaper

毎日1回、英語のミニマルな quote 壁紙を自動生成し、Windows のデスクトップ背景に設定するツール。

---

## 🚀 スタッフ向けクイックセットアップ（Windows）

> 「自分のPCで毎日違う名言の壁紙を出したい」だけならここを読めばOK。所要時間 約10分。

### 必要なもの

1. **Git for Windows** — https://gitforwindows.org/ からインストール
2. **Python 3.12 以上** — https://www.python.org/downloads/ からインストール
   - インストーラーで **「Add python.exe to PATH」に必ずチェック**
3. **Claude Code**（AIに名言を編集してもらう用。任意だが推奨）

### セットアップ手順

PowerShell を開いて以下を順に実行してください。

```powershell
# 1. リポジトリを取得（好きな場所に clone）
cd $HOME
git clone https://github.com/osawa-ux/daily_wallpaper.git
cd daily_wallpaper

# 2. 仮想環境を作って依存ライブラリを入れる
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. 試しに実行（壁紙が変わればOK）
python main.py
```

デスクトップの壁紙が変わったら成功です。

### 毎日自動で壁紙を変える（タスクスケジューラ登録）

PowerShell で以下を実行してください（**clone した場所のパスに合わせてください**）。

```powershell
$repo = "$HOME\daily_wallpaper"   # ← clone した場所に合わせる
$python = "$repo\.venv\Scripts\python.exe"

$action = New-ScheduledTaskAction `
    -Execute $python `
    -Argument "main.py" `
    -WorkingDirectory $repo

$trigger = New-ScheduledTaskTrigger -Daily -At 7am

Register-ScheduledTask `
    -TaskName "DailyQuoteWallpaper" `
    -Action $action `
    -Trigger $trigger `
    -Description "Daily minimal quote wallpaper generator"
```

これで毎朝 7:00 に自動で新しい名言の壁紙に切り替わります。

**確認方法**: `Win + R` → `taskschd.msc` → タスクスケジューラライブラリに `DailyQuoteWallpaper` があればOK。右クリック「実行」で即時テストできます。

**時刻を変えたい / 削除したい**:
```powershell
# 削除
Unregister-ScheduledTask -TaskName "DailyQuoteWallpaper" -Confirm:$false
```

### 自分の好きな名言を追加する（Claude Code 推奨）

このツールでは `quotes.json` というファイルに名言データが入っています。**メモ帳でも編集できますが、Claude Code に頼むのを推奨します**（AIに慣れる練習も兼ねて）。

#### Claude Code での編集方法

1. PowerShell で `cd $HOME\daily_wallpaper`
2. `claude` と打って Claude Code を起動
3. 自然言語で頼むだけ。例:

```
quotes.json に以下の名言を追加してください：
- "明日できることを今日やるな" 著者:オスカー・ワイルド カテゴリ:rest
- "千里の道も一歩から" 著者:老子 カテゴリ:discipline
追加後 python main.py --validate-quotes で検証もお願いします。
```

```
quotes.json から悲しい雰囲気の名言を3つ削除してください
```

```
野球選手の名言を5つ追加して、追加後に1つずつ --explain-style で
スタイルがどう選ばれるか見せてください
```

Claude Code が `quotes.json` を編集 → 検証 → プレビューまで一気にやってくれます。

#### 自分で直接編集する場合

`quotes.json` をメモ帳や VSCode で開いて以下の形式で追加:

```json
{
  "id": "q101",
  "text": "Your quote text here.",
  "author": "Author Name",
  "category": ["action", "focus"],
  "translated": false,
  "verification_status": "verified",
  "mood_tags": [],
  "season_tags": [],
  "length": "short",
  "enabled": true
}
```

詳しいフィールド説明は後述の [quotes.json の編集方法](#quotesjson-の編集方法) を参照。

### よくあるトラブル

| 症状 | 対処 |
|---|---|
| `python` コマンドが見つからない | Python 再インストール時に「Add python.exe to PATH」をチェック |
| `Activate.ps1` が実行できない | PowerShell を**管理者権限**で開き `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `git` コマンドが見つからない | Git for Windows をインストール後、PowerShell を開き直す |
| 壁紙が変わらない | `python main.py --preview` で画像だけ作ってみて確認 |
| タスクが動かない | タスクスケジューラで右クリック「実行」→ 履歴タブでエラー確認 |

---

## デザイン方針

- **Dark, elegant, quiet** — Apple keynote のような静かな高級感
- Quote の性質に応じてフォントと背景を自動切り替え
- 文字が主役、背景は添え物
- Minimal だが flat ではなく deep

## セットアップ

```bash
cd daily_wallpaper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 実行方法

```bash
python main.py                          # 壁紙生成 + 設定（自動スタイル選択）
python main.py --mood motivated         # mood 補正あり
python main.py --preview                # 画像のみ生成（壁紙変更なし）
python main.py --quote-id q001          # 特定 quote を指定
python main.py --no-set-wallpaper       # 壁紙変更なし
```

## 自動スタイルルーティング

Quote のカテゴリと文字数に応じて、フォント・背景が自動選択されます。

| ルール | 条件 | フォント | 背景 | 印象 |
|---|---|---|---|---|
| `action_short` | action/discipline 系 & 短文(<=50字) | Segoe UI Light (larger) | spotlight | sharp, strong, focused |
| `action_long` | action/discipline 系 & 長文 | Segoe UI Light (refined) | spotlight | clean, cool, minimal |
| `reflective` | reflection/gratitude/rest 系 | Garamond | deep_gradient | quiet, elegant, indigo |
| `default` | 上記に該当しない | Garamond | deep_gradient | dark, elegant, deep |

### カテゴリ分類

- **Action 系**: action, discipline, focus, leadership, endurance
- **Reflective 系**: reflection, gratitude, rest

### Short quote の判定

- 文字数 50 文字以下 **かつ** semantic split で 2 行以下

すべて `config.json` の `style_routing` で調整可能です。

## 背景スタイル

| スタイル | 特徴 |
|---|---|
| `deep_gradient` | 上部は黒、下部に deep navy / indigo の色味。静かで深い |
| `spotlight` | 中央に青い光の pool。文字が浮き上がる |
| `textured_dark` | indigo ベース + 縦方向のムラ + ノイズ質感 |
| `default` | 微妙なグラデーション + radial glow（従来版） |

## フォントスタイル

| プリセット | フォント | 用途 |
|---|---|---|
| `garamond` | Garamond | Serif 系デフォルト。エレガント |
| `refined` | Segoe UI Light | Sans 系デフォルト。クリーン |
| `larger` | Segoe UI Light (115%) | 短文 action 系。大きく表示 |
| `serif` | Georgia | クラシック serif |
| `palatino` | Palatino Linotype | 温かみ、上品 |
| `bookantiqua` | Book Antiqua | 文芸的、クリーン |

## CLI オプション一覧

| オプション | 説明 |
|---|---|
| `--mood MOOD` | mood 補正（tired, motivated, stressed, uncertain, brave） |
| `--preview` | 壁紙設定をせず画像生成のみ |
| `--quote-id ID` | 指定 quote を強制表示 |
| `--no-set-wallpaper` | 画像ファイル生成のみ |
| `--variants` | v1/v2/v3 スタイルバリアント生成 |
| `--compare-author` | author サイズ比較（0.24 / 0.26 / 0.28） |
| `--compare-bg` | 背景スタイル比較（spotlight / deep_gradient / textured_dark） |
| `--compare-font` | フォント比較（Georgia / Garamond / Palatino / Book Antiqua） |
| `--demo` | 各ルーティングルールのデモ壁紙を一括生成 |
| `--explain-style` | スタイル選択の判断理由を表示（画像生成なし） |

### explain-style の出力例

```
python main.py --quote-id q001 --explain-style

--- Style Routing ---
  quote_id:   q001
  category:   action, growth
  length:     26 chars, 2 lines
  rule:       action_short
  font:       larger
  background: spotlight
  reason:     short action quote (26 chars, 2 lines, categories: {'action'})
```

## 出力ディレクトリ構成

```
output/
  wallpaper_today.jpg          # 本番壁紙（毎日上書き）
  history.json                 # 表示履歴
  previews/                    # 比較・プレビュー用（Git管理外）
    variants/                  # --variants の出力
    author_compare/            # --compare-author の出力
    bg_compare/                # --compare-bg の出力
    font_compare/              # --compare-font の出力
    demos/                     # --demo の出力
```

## Windows タスクスケジューラへの登録

冒頭の [スタッフ向けクイックセットアップ](#-スタッフ向けクイックセットアップwindows) を参照。

## quotes.json の編集方法

```json
{
  "id": "q061",
  "text": "Your quote text here.",
  "author": "Author Name",
  "category": ["action", "focus"],
  "translated": false,
  "verification_status": "verified",
  "mood_tags": ["motivated"],
  "season_tags": ["spring"],
  "length": "short",
  "enabled": true
}
```

### フィールド説明

| フィールド | 説明 |
|---|---|
| `id` | ユニーク ID（`q001` 形式） |
| `category` | `action`, `discipline`, `focus`, `leadership`, `endurance`, `reflection`, `rest`, `gratitude` から複数 |
| `translated` | 翻訳 quote は `true` |
| `verification_status` | `verified`（検証済）, `translated`（翻訳）, `original`（オリジナル） |
| `length` | `short`, `medium`, `long` |
| `enabled` | `false` で選択対象から除外 |
| `mood_tags` | mood 補正との関連（参考情報） |
| `season_tags` | 季節との関連（参考情報） |

### 100本構成への拡張時の注意

- `id` はユニークに保つ（`q061` 以降を連番で追加）
- `category` は必ず1つ以上指定（スタイルルーティングに使用）
- `enabled: false` で一時無効化可能
- 将来 `source` フィールドを追加しても既存コードは壊れない

## config.json の編集方法

### スタイルルーティング設定

```json
"style_routing": {
  "reflective_categories": ["reflection", "gratitude", "rest"],
  "action_categories": ["action", "discipline", "focus", "leadership", "endurance"],
  "short_quote_max_chars": 50,
  "short_quote_max_lines": 2,
  "preset_mappings": {
    "action_short":  { "font_preset": "larger",   "bg_style": "spotlight" },
    "action_long":   { "font_preset": "refined",  "bg_style": "spotlight" },
    "reflective":    { "font_preset": "garamond",  "bg_style": "deep_gradient" },
    "default":       { "font_preset": "garamond",  "bg_style": "deep_gradient" }
  }
}
```

### レイアウト設定

| 設定 | デフォルト | 説明 |
|---|---|---|
| `author_size_ratio` | 0.26 | Author / Quote のサイズ比 |
| `line_spacing_ratio` | 0.50 | 行間の比率 |
| `author_gap_ratio` | 1.0 | Author までの距離 |
| `vertical_offset` | null (自動) | 垂直オフセット |

## 背景画像の差し替え

1. `assets/backgrounds/` に JPG/PNG 画像を配置
2. `config.json` で `"use_background_images": true` に変更

## フォントの差し替え

1. `assets/fonts/` に `.ttf` / `.ttc` フォントを配置
2. `config.json` の `font_quote` / `font_author` にパスを指定

## Quote 追加ガイド

### 壁紙向き quote の基準

- **短く、強く、静か**: 壁紙は毎日見るもの。うるさくない、でも印象に残る quote
- **1〜3行に収まる**: 長すぎると文字が小さくなる
- **推奨文字数**: 20〜90 文字（英語）。100文字超は控えめに
- **普遍的なメッセージ**: 時事ネタ、特定宗教、政治的内容は避ける

### Category の選び方

| Category | 向いている quote |
|---|---|
| `action` | 行動を促す、始める力 |
| `discipline` | 習慣、継続、規律 |
| `focus` | 集中、シンプルさ、本質 |
| `leadership` | リーダーシップ、影響力、責任 |
| `endurance` | 忍耐、困難を乗り越える |
| `reflection` | 内省、人生の意味、哲学 |
| `rest` | 休息、回復、余白 |
| `gratitude` | 感謝、幸福、他者への思い |

- **必ず1つ以上指定**（スタイルルーティングに使用）
- 複数指定可。最も近い2つまでが理想
- category によってフォント・背景が自動切替される

### Author あり / なし の使い分け

- **author あり**: 有名人の quote。信頼性と重みが出る
- **author なし**: オリジナル格言、出典不明の名言。`author: ""` で空にする
- author が空なら壁紙上には表示されない

### Translated の扱い

- 日本語の quote や、日本人の言葉を翻訳した quote は `translated: true`
- `verification_status: "translated"` とセットで使う
- 壁紙上には translated ラベルは通常表示しない（config で ON/OFF 可能）

### 追加手順

1. `quotes.json` に新しいエントリを追加（`id` は `q101` 以降）
2. `python main.py --validate-quotes` でバリデーション実行
3. `python main.py --quote-id q101 --preview` で見た目確認
4. `python main.py --quote-id q101 --explain-style` でルーティング確認

## Quote バリデーション

```bash
python main.py --validate-quotes
```

チェック項目:
- `id` の重複
- `category` が空でないか
- `enabled` フィールドの存在
- `text` が空でないか
- 未知の category 使用
- `verification_status` の不正値
- `length` の不正値
- カテゴリ別の本数統計

## よくあるエラーと対処

| エラー | 対処 |
|---|---|
| `No quotes found` | `quotes.json` が空か全 quote が `enabled: false` |
| `Failed to set wallpaper` | 管理者権限で実行、または `--preview` で確認 |
| フォントが見つからない | `assets/fonts/` にフォントを配置し config で指定 |
| 文字化け | 日本語対応フォントを設定 |

## ファイル構成

```
daily_wallpaper/
  main.py                     # CLI エントリポイント
  config.json                 # 全設定（ルーティング、重み、レイアウト）
  quotes.json                 # Quote データ（60件）
  requirements.txt            # Pillow, numpy
  src/
    config_loader.py           # 設定・quote 読み込み
    quote_selector.py          # 重み計算・quote 選択
    wallpaper_generator.py     # 画像生成・スタイルルーティング
    wallpaper_setter.py        # Windows 壁紙設定
    history_manager.py         # 履歴管理
    utils.py                   # 共通関数
  assets/
    backgrounds/               # 背景画像（任意）
    fonts/                     # カスタムフォント（任意）
  output/
    wallpaper_today.jpg        # 本番壁紙
    history.json               # 表示履歴
    previews/                  # 比較用出力（Git管理外）
  logs/
    app.log                    # 実行ログ
```

## 今後の拡張ポイント

- quotes.json を 100 件以上に拡充
- 4K / マルチモニター対応
- カスタムフォント（Google Fonts など）の導入
- GUI / トレイアプリ化
- 壁紙アーカイブ（日付別保存）
- API 連携で quote 自動取得
