"""Main orchestrator: generate a daily blog post from Claude Code docs."""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

from fetch_doc import fetch_topic
from enhance_content import enhance_topic
from translate import generate_chinese_post
from take_screenshots import (
    capture_topic_screenshots,
    parse_screenshot_markers,
    replace_screenshot_markers,
)
from state_manager import StateManager

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"


def _extract_title(content: str) -> str:
    """Extract the first H1 heading from markdown content."""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            title = re.sub(r'^[\U0001F300-\U0001F9FF]\s*', '', title)
            return title
    return ""


def _fix_doc_links(content: str) -> str:
    """Fix internal doc links by converting them to absolute CC docs URLs.

    Links like /en/quickstart should point to code.claude.com docs.
    """
    content = re.sub(
        r'\]\(/en/([\w-]+(?:/[\w-]+)*)\)',
        r'](https://code.claude.com/docs/en/\1)',
        content,
    )
    return content


def write_post(content: str, date_str: str, topic: dict, lang: str) -> Path:
    """Write a Jekyll post file and return its path."""
    lang_dir = POSTS_DIR / lang
    lang_dir.mkdir(parents=True, exist_ok=True)

    slug = topic["slug"].replace("/", "-")
    filename = f"{date_str}-{slug}.md"
    filepath = lang_dir / filename

    # Use the H1 title from generated content, fall back to topic title
    extracted_title = _extract_title(content)
    title = extracted_title or topic[f"title_{lang}"]

    other_lang = "zh" if lang == "en" else "en"
    other_slug = topic["slug"]
    # Jekyll permalink is /daily-digest/YYYY/MM/DD/slug.html (from categories)
    lang_switch = f"/claude-code-daily-blog/daily-digest/{date_str.replace('-', '/')}/{other_slug.replace('/', '-')}.html"

    # Extract description from first paragraph, escape YAML special chars
    desc_match = re.search(r"^(?!#|\s*<!--|\s*!)(.+)$", content, re.MULTILINE)
    description = desc_match.group(1)[:160] if desc_match else title
    description = description.replace('"', '\\"').replace("'", "\\'")

    front_matter = f"""---
layout: post
title: "{title}"
date: {date_str}
topic: {topic['slug']}
lang: {lang}
lang_switch: "{lang_switch}"
categories: [daily-digest]
tags: [claude-code, {slug}]
description: "{description}"
---

"""

    filepath.write_text(front_matter + content)
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Generate a daily blog post")
    parser.add_argument("--topic", type=str, default=None, help="Override topic slug")
    parser.add_argument("--skip-screenshots", action="store_true", help="Skip screenshot capture")
    parser.add_argument("--skip-api", action="store_true", help="Skip Claude API calls (use raw doc)")
    args = parser.parse_args()

    sm = StateManager()

    # Idempotency check
    if not args.topic and sm.is_already_published_today():
        print("A post was already published today. Use --topic to override.")
        return

    # Determine topic
    try:
        topic = sm.get_next_topic(override=args.topic)
    except ValueError as e:
        print(f"Error: {e}")
        return

    slug = topic["slug"]
    print(f"Generating blog post for: {slug} ({topic['title_en']})")

    # Get next topic for teaser
    next_topic = sm.get_next_topic_after(slug)
    next_title = next_topic["title_en"] if next_topic else ""

    # Step 1: Fetch raw documentation
    print("  [1/6] Fetching documentation...")
    try:
        raw_doc = fetch_topic(slug)
    except Exception as e:
        print(f"  Failed to fetch docs: {e}")
        return

    # Step 2: Enhance into English blog post
    print("  [2/6] Generating English blog post...")
    if args.skip_api:
        en_content = raw_doc["raw_markdown"]
    else:
        try:
            en_content = enhance_topic(raw_doc, slug, next_title)
        except Exception as e:
            print(f"  Claude API failed for English: {e}")
            en_content = raw_doc["raw_markdown"]

    # Step 3: Generate Chinese blog post
    print("  [3/6] Generating Chinese blog post...")
    next_title_zh = next_topic["title_zh"] if next_topic else ""
    if args.skip_api:
        zh_content = raw_doc["raw_markdown"]
    else:
        try:
            zh_content = generate_chinese_post(raw_doc, slug, next_title_zh)
        except Exception as e:
            print(f"  Claude API failed for Chinese: {e}")
            zh_content = raw_doc["raw_markdown"]

    # Step 4: Take screenshots
    print("  [4/6] Taking screenshots...")
    screenshots = {}
    if not args.skip_screenshots:
        try:
            en_markers = parse_screenshot_markers(en_content)
            zh_markers = parse_screenshot_markers(zh_content)
            all_markers = en_markers + [m for m in zh_markers if m not in en_markers]
            screenshots = capture_topic_screenshots(slug, all_markers if all_markers else None)
        except Exception as e:
            print(f"  Screenshot capture failed: {e}")

    # Step 5: Replace screenshot markers with actual images
    print("  [5/6] Assembling posts...")
    if screenshots:
        en_content = replace_screenshot_markers(en_content, screenshots)
        zh_content = replace_screenshot_markers(zh_content, screenshots)

    # Fix internal doc links: add baseurl prefix to /en/xxx links
    en_content = _fix_doc_links(en_content)
    zh_content = _fix_doc_links(zh_content)

    # Step 6: Write post files
    date_str = datetime.now().strftime("%Y-%m-%d")
    en_path = write_post(en_content, date_str, topic, "en")
    zh_path = write_post(zh_content, date_str, topic, "zh")
    print(f"  [6/6] Written:")
    print(f"    EN: {en_path}")
    print(f"    ZH: {zh_path}")

    # Update state
    sm.advance_topic(slug)
    print(f"  State updated. Next topic: {sm.get_next_topic()['slug']}")

    print("Done!")


if __name__ == "__main__":
    main()
