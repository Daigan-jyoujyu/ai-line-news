"""GoogleニュースのAI記事をLINE Flex Messageでブロードキャスト配信する。"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


RSS_URL = (
    "https://news.google.com/rss/search?"
    + urllib.parse.urlencode(
        {"q": "AI", "hl": "ja", "gl": "JP", "ceid": "JP:ja"}
    )
)
LINE_BROADCAST_URL = "https://api.line.me/v2/bot/message/broadcast"
MAX_ARTICLES = 5


def load_local_env() -> None:
    """ローカル用 .env を読み込む。GitHub Actionsでは既存の環境変数を使う。"""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    legacy_token: str | None = None
    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
        else:
            # 既存の値だけの形式をローカル移行時だけ受け付ける。
            legacy_token = line

    if not os.getenv("LINE_CHANNEL_ACCESS_TOKEN") and legacy_token:
        os.environ["LINE_CHANNEL_ACCESS_TOKEN"] = legacy_token
        print(
            "注意: .env を LINE_CHANNEL_ACCESS_TOKEN=<token> の形式へ更新してください。",
            file=sys.stderr,
        )


def fetch_articles() -> list[dict[str, str]]:
    request = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "ai-line-news/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    articles: list[dict[str, str]] = []
    for item in root.findall("./channel/item")[:MAX_ARTICLES]:
        source = (item.findtext("source") or "Googleニュース").strip()
        title = (item.findtext("title") or "無題").strip()
        suffix = f" - {source}"
        if title.endswith(suffix):
            title = title[: -len(suffix)].strip()

        published = parsedate_to_datetime(item.findtext("pubDate") or "")
        published_jst = published.astimezone(timezone(timedelta(hours=9)))
        articles.append(
            {
                "title": title,
                "source": source,
                "date": published_jst.strftime("%Y年%m月%d日 %H:%M"),
                "url": (item.findtext("link") or "").strip(),
            }
        )

    if len(articles) < MAX_ARTICLES:
        raise RuntimeError(f"RSSから取得できた記事が{len(articles)}件です（5件必要）。")
    return articles


def make_bubble(article: dict[str, str]) -> dict[str, object]:
    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#06C755",
            "paddingAll": "14px",
            "contents": [
                {
                    "type": "text",
                    "text": "AI NEWS",
                    "color": "#FFFFFF",
                    "weight": "bold",
                    "size": "sm",
                }
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": article["title"],
                    "weight": "bold",
                    "size": "lg",
                    "wrap": True,
                    "maxLines": 3,
                },
                {
                    "type": "text",
                    "text": article["source"],
                    "size": "sm",
                    "color": "#666666",
                    "wrap": True,
                },
                {
                    "type": "text",
                    "text": article["date"],
                    "size": "xs",
                    "color": "#999999",
                },
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#06C755",
                    "action": {
                        "type": "uri",
                        "label": "記事を読む",
                        "uri": article["url"],
                    },
                }
            ],
        },
    }


def make_payload(articles: list[dict[str, str]]) -> dict[str, object]:
    return {
        "messages": [
            {
                "type": "flex",
                "altText": "AIニュース 5件",
                "contents": {
                    "type": "carousel",
                    "contents": [make_bubble(article) for article in articles],
                },
            }
        ]
    }


def send_broadcast(payload: dict[str, object], token: str) -> None:
    request = urllib.request.Request(
        LINE_BROADCAST_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.status not in (200, 202):
                raise RuntimeError(f"LINE APIがHTTP {response.status} を返しました。")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LINE APIへの送信に失敗しました（HTTP {error.code}）。{detail}") from error


def main() -> None:
    load_local_env()
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKEN が設定されていません。")

    articles = fetch_articles()
    payload = make_payload(articles)
    if "--dry-run" in sys.argv:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    send_broadcast(payload, token)
    print("AIニュース5件をLINEへブロードキャスト送信しました。")


if __name__ == "__main__":
    main()
