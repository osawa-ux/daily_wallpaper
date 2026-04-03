# Daily Minimal English Quote Wallpaper

毎日1回、英語のミニマルな quote 壁紙を自動生成し、Windows のデスクトップ背景に設定するツール。

## セットアップ

### 1. 仮想環境の作成

```bash
cd daily_wallpaper
python -m venv .venv
.venv\Scripts\activate
```

### 2. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

## 実行方法

```bash
# 基本実行（壁紙生成 + 設定）
python main.py

# mood を指定して実行
python main.py --mood motivated

# プレビューのみ（壁紙設定しない）
python main.py --preview

# 特定の quote を指定して確認
python main.py --quote-id q001

# 画像生成のみ（壁紙変更なし）
python main.py --no-set-wallpaper
```

## CLI オプション一覧

| オプション | 説明 |
|---|---|
| `--mood MOOD` | mood 補正を適用（tired, motivated, stressed, uncertain, brave） |
| `--preview` | 壁紙設定をせず画像生成のみ |
| `--quote-id ID` | 指定 quote を強制表示（例: `q001`） |
| `--no-set-wallpaper` | 画像ファイル生成のみ、壁紙は変更しない |

## Windows タスクスケジューラへの登録

毎日自動実行するには、タスクスケジューラに登録します。

1. 「タスク スケジューラ」を開く
2. 「基本タスクの作成」をクリック
3. 名前: `DailyQuoteWallpaper`
4. トリガー: 毎日、好きな時刻（例: 07:00）
5. 操作: プログラムの開始
   - プログラム: `C:\Users\Motoi\daily_wallpaper\.venv\Scripts\python.exe`
   - 引数: `main.py`
   - 開始: `C:\Users\Motoi\daily_wallpaper`
6. 「最上位の特権で実行する」にチェック（任意）

PowerShell でワンライナー登録する場合:

```powershell
$action = New-ScheduledTaskAction -Execute "C:\Users\Motoi\daily_wallpaper\.venv\Scripts\python.exe" -Argument "main.py" -WorkingDirectory "C:\Users\Motoi\daily_wallpaper"
$trigger = New-ScheduledTaskTrigger -Daily -At 7am
Register-ScheduledTask -TaskName "DailyQuoteWallpaper" -Action $action -Trigger $trigger -Description "Daily minimal quote wallpaper generator"
```

## quotes.json の編集方法

`quotes.json` は JSON 配列で、各 quote は以下の形式:

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

- `id`: ユニークな ID（`q001` 形式推奨）
- `category`: `action`, `discipline`, `focus`, `leadership`, `endurance`, `reflection`, `rest`, `gratitude` から複数選択可
- `translated`: 翻訳 quote の場合 `true`
- `verification_status`: `verified`（検証済み）, `translated`（翻訳）, `original`（オリジナル）
- `length`: `short`, `medium`, `long`
- `enabled`: `false` にすると選択対象から除外

## config.json の編集方法

主な設定項目:

| 設定 | 説明 | デフォルト |
|---|---|---|
| `wallpaper_width` | 壁紙の横幅 | 1920 |
| `wallpaper_height` | 壁紙の高さ | 1080 |
| `cooldown_days` | 同じ quote を再表示しない日数 | 45 |
| `show_author` | author 表示の ON/OFF | true |
| `show_translated_label` | translated ラベルの ON/OFF | false |
| `overlay_opacity` | 背景画像使用時のオーバーレイ透明度 | 0.55 |
| `use_background_images` | 背景画像を使用するか | false |
| `font_quote` | quote 用フォントパス | null (自動検出) |
| `font_author` | author 用フォントパス | null (自動検出) |
| `default_mood` | デフォルト mood | null |

曜日別カテゴリ重み、季節補正、mood 補正もすべて config.json で調整可能。

## 背景画像の差し替え

1. `assets/backgrounds/` に JPG/PNG 画像を配置
2. `config.json` で `"use_background_images": true` に変更
3. ランダムに1枚が選ばれ、半透明オーバーレイ付きで使用される

## フォントの差し替え

1. `assets/fonts/` に `.ttf` / `.ttc` フォントを配置
2. `config.json` の `font_quote` / `font_author` にパスを指定

```json
{
  "font_quote": "assets/fonts/MyFont-Regular.ttf",
  "font_author": "assets/fonts/MyFont-Light.ttf"
}
```

未指定時は Windows 標準フォント（Segoe UI → Arial → Calibri）が使用される。日本語を含む場合は Yu Gothic 等に自動フォールバック。

## よくあるエラーと対処

| エラー | 対処 |
|---|---|
| `No quotes found` | `quotes.json` が空か、全 quote が `enabled: false` |
| `Failed to set wallpaper` | 管理者権限で実行、または `--preview` で画像のみ確認 |
| フォントが見つからない | `assets/fonts/` にフォントを配置し `config.json` で指定 |
| 文字化け | 日本語対応フォントを `font_quote` / `font_author` に設定 |

## ファイル構成

```
daily_wallpaper/
  main.py              # エントリポイント・CLI
  config.json          # 設定ファイル
  quotes.json          # quote データ
  requirements.txt     # 依存ライブラリ
  src/
    config_loader.py   # 設定・quote 読み込み
    quote_selector.py  # 重み計算・quote 選択
    wallpaper_generator.py  # 画像生成
    wallpaper_setter.py     # Windows 壁紙設定
    history_manager.py      # 履歴管理
    utils.py                # 共通関数
  assets/
    backgrounds/       # 背景画像（任意）
    fonts/             # カスタムフォント（任意）
  output/
    wallpaper_today.jpg  # 生成された壁紙
    history.json         # 表示履歴
  logs/
    app.log            # 実行ログ
```

## 今後の拡張ポイント

- quote を 100 件以上に拡充
- API 連携で quote を自動取得
- 複数解像度対応（4K, マルチモニター）
- テーマ切り替え（ライトモード、カラーテーマ）
- GUI 設定画面
- 壁紙アーカイブ機能（日付別保存）
- システムトレイ常駐アプリ化
