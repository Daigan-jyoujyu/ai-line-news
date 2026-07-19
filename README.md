# AI LINE News

GoogleニュースのRSSからAIニュースを5件集め、うち最大2件はAI動画生成関連を優先して、LINEのFlex Messageとして毎朝7時（日本時間）にブロードキャスト配信するプロジェクトです。

## 構成

- `scripts/`: RSS取得・カード生成・LINE送信のスクリプト
- `.github/workflows/`: GitHub Actionsの定期実行設定
- `.env`: ローカル用の秘密情報（Git管理対象外）
- `.env.example`: 環境変数の見本

## 秘密情報

必要な環境変数は `LINE_CHANNEL_ACCESS_TOKEN` のみです。送信にはLINE Messaging APIのブロードキャスト方式を使うため、`LINE_USER_ID` は使用しません。

ローカルでは `.env.example` を参考に、`.env` に `LINE_CHANNEL_ACCESS_TOKEN=<発行したトークン>` の形式で設定してください。GitHub Actionsでは、リポジトリの `Settings > Secrets and variables > Actions` に `LINE_CHANNEL_ACCESS_TOKEN` という名前で登録します。トークンをコードやワークフローへ直接記載しないでください。

> 現在の `scripts/main.py` は環境変数を確認する土台です。RSS取得・Flex Message生成・LINE送信は次の工程で実装します。
