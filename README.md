# AI LINE News

GoogleニュースのRSSからAIニュースを5件集め、うち最大2件はAI動画生成関連を優先して、LINEのFlex Messageとして毎朝7時（日本時間）にブロードキャスト配信するプロジェクトです。

## 構成

- `scripts/`: RSS取得・カード生成・LINE送信のスクリプト
- `.github/workflows/`: GitHub Actionsの定期実行設定
- `.env`: ローカル用の秘密情報（Git管理対象外）
- `.env.example`: 環境変数の見本
- `last_run.txt`: 最終配信日時の記録（自動更新／後述）

## 秘密情報

必要な環境変数は `LINE_CHANNEL_ACCESS_TOKEN` のみです。送信にはLINE Messaging APIのブロードキャスト方式を使うため、`LINE_USER_ID` は使用しません。

ローカルでは `.env.example` を参考に、`.env` に `LINE_CHANNEL_ACCESS_TOKEN=<発行したトークン>` の形式で設定してください。GitHub Actionsでは、リポジトリの `Settings > Secrets and variables > Actions` に `LINE_CHANNEL_ACCESS_TOKEN` という名前で登録します。トークンをコードやワークフローへ直接記載しないでください。

## 定期実行と自動無効化対策

GitHub Actionsは「60日間コミットがない定期実行ワークフロー」を自動的に無効化する仕様があります。本プロジェクトの配信スクリプトはLINEに送るだけでリポジトリへ書き込みを行わないため、放置するとこの仕様に該当して配信が止まってしまいます。

これを防ぐため、`daily-news.yml` では配信成功のたびに `last_run.txt` へ最終配信日時を書き込み、リポジトリへ自動コミット＆pushしています。これによりリポジトリの活動が維持され、自動無効化が発生しません。追加のSecretは不要で、GitHub Actions標準の `GITHUB_TOKEN` で動作します。
