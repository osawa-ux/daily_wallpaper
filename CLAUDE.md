# CLAUDE.md — daily_wallpaper

日替わり壁紙自動生成ツール。名言をデザインして壁紙として設定する。

## 上位原則
本repoは Obsidian の `30_Areas/開発運用原則.md` を上位原則として参照する。
repo固有ルールはこの CLAUDE.md に限定し、原則全文は複製しない。

## Secrets 運用

現時点では secrets は不要（外部 API を使用していない）。

### 将来 secrets を追加する場合

以下の共通ルールに従う:

- 原本: クラウド同期ストレージ配下の個人 Vault（例: `~/OneDrive/.secrets/daily_wallpaper/`）
- 実行用: `~/.secrets/daily_wallpaper/`
- コード内の参照順: 環境変数 → `~/.secrets/daily_wallpaper/` → フォールバック
- `.env`, `credentials*.json`, `token*.json`, `*.p12`, `*.pem` などの秘密情報は Git に入れない
- secret の実値をコードやコメントにハードコードしない
