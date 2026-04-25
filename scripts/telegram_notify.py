"""Send blog post notification to Telegram group."""

import os
import json
import requests

TELEGRAM_API = "https://api.telegram.org"


def _get_bot_token() -> str:
    return os.environ.get("TELEGRAM_BOT_TOKEN", "")


def _get_chat_id() -> str:
    return os.environ.get("TELEGRAM_CHAT_ID", "")


def _get_proxy() -> str | None:
    return os.environ.get("TELEGRAM_PROXY_URL") or None


def send_message(text: str, chat_id: str | None = None) -> bool:
    """Send a message to Telegram. Returns True on success."""
    token = _get_bot_token()
    cid = chat_id or _get_chat_id()
    if not token or not cid:
        print("  Telegram: missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False

    url = f"{TELEGRAM_API}/bot{token}/sendMessage"
    payload = {
        "chat_id": cid,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    proxies = None
    proxy = _get_proxy()
    if proxy:
        if proxy.startswith("socks5://"):
            host_port = proxy.replace("socks5://", "")
            proxies = {"https": f"socks5h://{host_port}", "http": f"socks5h://{host_port}"}

    try:
        resp = requests.post(url, json=payload, proxies=proxies, timeout=30)
        data = resp.json()
        if data.get("ok"):
            return True
        else:
            print(f"  Telegram error: {data.get('description')}")
            return False
    except Exception as e:
        print(f"  Telegram failed: {e}")
        return False


def notify_new_post(topic: dict, date_str: str, base_url: str = "https://mudyman.github.io/claude-code-daily-blog") -> bool:
    """Send a notification about a new blog post."""
    slug = topic["slug"].replace("/", "-")
    title_en = topic["title_en"]
    title_zh = topic["title_zh"]

    en_url = f"{base_url}/daily-digest/{date_str.replace('-', '/')}/{slug}.html"
    zh_url = f"{base_url}/daily-digest/{date_str.replace('-', '/')}/{slug}.html"

    text = (
        f"📝 <b>Claude Code Daily</b> — 新文章发布！\n\n"
        f"🇨🇳 {title_zh}\n"
        f"🇬🇧 {title_en}\n\n"
        f"🔗 <a href=\"{en_url}\">English</a> | <a href=\"{zh_url}\">中文</a>\n\n"
        f"📅 {date_str} | 主题: {slug}"
    )

    return send_message(text)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from state_manager import StateManager

    sm = StateManager()
    if sm.state["last_topic_slug"]:
        topic = None
        for t in sm.topics:
            if t["slug"] == sm.state["last_topic_slug"]:
                topic = t
                break
        if topic:
            ok = notify_new_post(topic, sm.state["last_published_date"])
            print("Sent!" if ok else "Failed")
        else:
            print("Topic not found")
    else:
        print("No posts published yet")