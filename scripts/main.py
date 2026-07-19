"""AIニュース配信処理のエントリーポイント。"""

import os


def main() -> None:
    """今後、RSS取得・Flex Message生成・ブロードキャスト送信を実装する。"""
    if not os.getenv("LINE_CHANNEL_ACCESS_TOKEN"):
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKEN が設定されていません。")

    print("環境変数を確認しました。ニュース配信処理は次の工程で実装します。")


if __name__ == "__main__":
    main()

