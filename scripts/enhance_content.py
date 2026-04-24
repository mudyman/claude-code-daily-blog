"""Enhance raw documentation into an engaging English blog post using Claude API."""

import os

import anthropic
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
MODEL = os.environ.get("CC_BLOG_MODEL", "astron-code-latest")
MAX_TOKENS = 8000


def _get_client() -> anthropic.Anthropic:
    """Create Anthropic client using CC's current base_url and api_key.

    Reads config from hermes auth.json if available, otherwise from env vars.
    """
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "")
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")

    # Try reading from hermes auth.json as fallback
    if not api_key:
        auth_path = Path.home() / ".hermes" / "auth.json"
        if auth_path.exists():
            import json
            auth = json.loads(auth_path.read_text())
            for creds in auth.get("credential_pool", {}).values():
                for c in creds:
                    if "xf-yun.com" in (c.get("base_url") or ""):
                        api_key = c["access_token"]
                        base_url = c["base_url"].rstrip("/") + "/anthropic"
                        break
                if api_key:
                    break

    return anthropic.Anthropic(base_url=base_url or None, api_key=api_key)


def enhance_topic(raw_doc: dict, topic: str, next_topic_title: str = "") -> str:
    """Transform raw doc into an English blog post via Claude API."""
    system_prompt = (PROMPTS_DIR / "enhance_en.txt").read_text()

    user_content = f"Topic: {topic}\n"
    if next_topic_title:
        user_content += f"Next topic in series: {next_topic_title}\n"
    user_content += f"\nRaw documentation:\n\n{raw_doc['raw_markdown']}"

    client = _get_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text


if __name__ == "__main__":
    import sys
    import json
    from fetch_doc import fetch_topic

    topic = sys.argv[1] if len(sys.argv) > 1 else "overview"
    raw = fetch_topic(topic)
    result = enhance_topic(raw, topic)
    print(result)
