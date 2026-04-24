"""Fetch and parse Claude Code documentation from llms-full.txt."""

import re
import requests
from pathlib import Path

LLMS_FULL_URL = "https://code.claude.com/docs/llms-full.txt"
CACHE_DIR = Path(__file__).parent.parent / "state"


def fetch_llms_full() -> str:
    """Download the full documentation text from llms-full.txt."""
    resp = requests.get(LLMS_FULL_URL, timeout=60)
    resp.raise_for_status()
    return resp.text


def parse_topic(raw: str, topic_slug: str) -> dict:
    """Extract a single topic's content from the full docs text.

    The llms-full.txt format uses sections like:
        # Title
        Source: https://code.claude.com/docs/en/topic-slug
        ...content...

    Returns a dict with: topic, title, source_url, raw_markdown, code_examples
    """
    # Split into sections by finding "Source:" lines
    source_pattern = re.compile(
        r"^#\s+(.+?)\s*$\n^Source:\s+(https?://\S+)$",
        re.MULTILINE,
    )

    sections = []
    for m in source_pattern.finditer(raw):
        sections.append({
            "title": m.group(1).strip(),
            "source_url": m.group(2).strip(),
            "start": m.end(),
        })

    # Add end positions
    for i in range(len(sections) - 1):
        sections[i]["end"] = sections[i + 1]["start"] - 1
    if sections:
        sections[-1]["end"] = len(raw)

    # Find the matching section by exact URL match
    # e.g. "overview" must match /en/overview not /en/agent-sdk/overview
    target_url = f"https://code.claude.com/docs/en/{topic_slug}"
    for sec in sections:
        if sec["source_url"].rstrip("/") == target_url:
            content = raw[sec["start"]:sec["end"]].strip()
            code_examples = _extract_code_examples(content)
            return {
                "topic": topic_slug,
                "title": sec["title"],
                "source_url": sec["source_url"],
                "raw_markdown": _clean_content(content),
                "code_examples": code_examples,
            }

    return None


def _extract_code_examples(markdown: str) -> list[dict]:
    """Extract code blocks from markdown."""
    pattern = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
    examples = []
    for m in pattern.finditer(markdown):
        examples.append({
            "language": m.group(1) or "text",
            "code": m.group(2).strip(),
        })
    return examples


def _clean_content(content: str) -> str:
    """Remove React component code and other non-doc artifacts."""
    # Remove React component definitions (export const ... = ...)
    content = re.sub(
        r"export\s+const\s+\w+.*?=\s*\(.*?\)\s*=>\s*\{.*?\};",
        "", content, flags=re.DOTALL,
    )
    # Remove CSS style blocks
    content = re.sub(r"<style>.*?</style>", "", content, flags=re.DOTALL)
    # Remove JSX/TSX component references like <InstallConfigurator ... />
    content = re.sub(r"<[A-Z]\w+[^>]*/?>", "", content)
    # Remove A/B experiment markers
    content = re.sub(r"\{/\*.*?\*/\}", "", content)
    # Collapse multiple blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()


def fetch_topic(topic_slug: str) -> dict:
    """Main entry: fetch docs and extract a single topic."""
    raw = fetch_llms_full()
    result = parse_topic(raw, topic_slug)
    if result is None:
        raise ValueError(f"Topic '{topic_slug}' not found in documentation")
    return result


if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "overview"
    data = fetch_topic(topic)
    print(f"Title: {data['title']}")
    print(f"Source: {data['source_url']}")
    print(f"Code examples: {len(data['code_examples'])}")
    print(f"Content length: {len(data['raw_markdown'])} chars")
    print("---")
    print(data["raw_markdown"][:2000])
