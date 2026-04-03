# CLAUDE.md — daily_wallpaper

日替わり壁紙自動生成ツール。名言をデザインして壁紙として設定する。

## Secrets 運用

現時点では secrets は不要（外部 API を使用していない）。

### 将来 secrets を追加する場合

以下の共通ルールに従う:

- 原本: `C:\Users\Motoi\OneDrive\個人用 Vault\.secrets\daily_wallpaper\`
- 実行用: `C:\Users\Motoi\.secrets\daily_wallpaper\`
- コード内の参照順: 環境変数 → `~/.secrets/daily_wallpaper/` → フォールバック
- `.env`, `credentials*.json`, `token*.json`, `*.p12`, `*.pem` などの秘密情報は Git に入れない
- secret の実値をコードやコメントにハードコードしない
