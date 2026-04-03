# Daily Minimal English Quote Wallpaper

毎日1回、英語のミニマルな quote 壁紙を自動生成し、Windows のデスクトップ背景に設定するツール。

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

```powershell
$action = New-ScheduledTaskAction -Execute "C:\Users\Motoi\daily_wallpaper\.venv\Scripts\python.exe" -Argument "main.py" -WorkingDirectory "C:\Users\Motoi\daily_wallpaper"
$trigger = New-ScheduledTaskTrigger -Daily -At 7am
Register-ScheduledTask -TaskName "DailyQuoteWallpaper" -Action $action -Trigger $trigger -Description "Daily minimal quote wallpaper generator"
```

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
