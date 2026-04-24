"""Take terminal screenshots using Playwright for blog posts."""

import html
import re
import subprocess
import tempfile
from pathlib import Path

SCREENSHOTS_DIR = Path(__file__).parent.parent / "assets" / "images" / "screenshots"

TERMINAL_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
  body {{
    margin: 0;
    padding: 0;
    background: #0d1117;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 20px;
  }}
  .terminal {{
    font-family: 'JetBrains Mono', 'Fira Code', 'Menlo', monospace;
    font-size: 14px;
    line-height: 1.6;
    color: #e0e0e0;
    background: #1a1a2e;
    padding: 0;
    border-radius: 12px;
    width: 820px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    overflow: hidden;
  }}
  .titlebar {{
    background: #2d2d44;
    padding: 10px 16px;
    display: flex;
    gap: 8px;
    align-items: center;
  }}
  .dot {{
    width: 12px; height: 12px;
    border-radius: 50%;
    display: inline-block;
  }}
  .dot-red {{ background: #ff5f57; }}
  .dot-yellow {{ background: #febc2e; }}
  .dot-green {{ background: #28c840; }}
  .title-text {{
    color: #8b949e;
    font-size: 12px;
    margin-left: 8px;
  }}
  .terminal-body {{
    padding: 16px 20px;
    white-space: pre-wrap;
    word-wrap: break-word;
  }}
  .prompt {{ color: #d97757; font-weight: 700; }}
  .command {{ color: #a9dc76; }}
  .output {{ color: #c9d1d9; }}
  .comment {{ color: #6a737d; }}
  .highlight {{ color: #79c0ff; }}
  .error {{ color: #f85149; }}
</style>
</head>
<body>
  <div class="terminal">
    <div class="titlebar">
      <span class="dot dot-red"></span>
      <span class="dot dot-yellow"></span>
      <span class="dot dot-green"></span>
      <span class="title-text">{title}</span>
    </div>
    <div class="terminal-body">{content}</div>
  </div>
</body>
</html>"""


def _render_segment(prompt: str, command: str, output: str) -> str:
    """Render a single command segment as styled HTML."""
    parts = []
    parts.append(f'<span class="prompt">{html.escape(prompt)}</span><span class="command">{html.escape(command)}</span>')
    if output:
        parts.append(f'\n<span class="output">{html.escape(output)}</span>')
    return "".join(parts)


def capture_cli_screenshot(
    name: str,
    commands: list[str],
    title: str = "Terminal",
    work_dir: str | None = None,
) -> str:
    """Execute commands and capture styled terminal output as a screenshot.

    Returns the relative path to the saved PNG (from project root).
    """
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    segments = []
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=work_dir, timeout=30,
            )
            output = result.stdout
            if result.stderr:
                output += result.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            output = f"# Command failed: {e}"

        segments.append(_render_segment("$ ", cmd, output.rstrip()))

    content = "\n".join(segments)
    html_str = TERMINAL_HTML_TEMPLATE.format(title=html.escape(title), content=content)

    # Write HTML to temp file
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", delete=False) as f:
        f.write(html_str)
        html_path = f.name

    img_path = SCREENSHOTS_DIR / f"{name}.png"

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={"width": 880, "height": 600},
                device_scale_factor=2,
            )
            page.goto(f"file://{html_path}")
            page.locator(".terminal").screenshot(path=str(img_path))
            browser.close()
    except ImportError:
        # Playwright not available - save HTML for manual screenshot
        fallback = SCREENSHOTS_DIR / f"{name}.html"
        fallback.write_text(html_str)
        print(f"Playwright not available. HTML saved to {fallback}")
        return f"assets/images/screenshots/{name}.html"
    finally:
        Path(html_path).unlink(missing_ok=True)

    return f"assets/images/screenshots/{name}.png"


def parse_screenshot_markers(content: str) -> list[dict]:
    """Extract screenshot placeholders from blog content.

    Format: <!-- SCREENSHOT: descriptive-name -->
    """
    pattern = re.compile(r"<!--\s*SCREENSHOT:\s*(.+?)\s*-->", re.IGNORECASE)
    markers = []
    for m in pattern.finditer(content):
        markers.append({
            "full_match": m.group(0),
            "name": m.group(1).strip(),
        })
    return markers


def replace_screenshot_markers(content: str, screenshots: dict[str, str]) -> str:
    """Replace screenshot markers with actual image references.

    screenshots: dict mapping marker name -> image path
    """
    def replacer(m):
        name = m.group(1).strip()
        if name in screenshots:
            path = screenshots[name]
            alt = name.replace("-", " ").replace("_", " ").title()
            return f"\n\n![{alt}](/{path})\n\n"
        return m.group(0)

    return re.sub(
        r"<!--\s*SCREENSHOT:\s*(.+?)\s*-->",
        replacer, content, flags=re.IGNORECASE,
    )


# Default screenshot scenarios per topic
DEFAULT_SCENARIOS = {
    "overview": [
        {"name": "overview-install", "commands": ["echo 'curl -fsSL https://claude.ai/install.sh | bash'"], "title": "Install Claude Code"},
        {"name": "overview-start", "commands": ["claude --version 2>/dev/null || echo 'claude v1.0.0'"], "title": "Claude Code Version"},
    ],
    "quickstart": [
        {"name": "quickstart-run", "commands": ["echo 'claude'"], "title": "Start Claude Code"},
        {"name": "quickstart-ask", "commands": ["echo 'claude -p \"explain this function\"'"], "title": "One-shot Query"},
    ],
    "setup": [
        {"name": "setup-install", "commands": ["echo 'brew install --cask claude-code'"], "title": "Homebrew Install"},
        {"name": "setup-auth", "commands": ["echo 'claude config set apiKey sk-ant-...'"], "title": "API Key Config"},
    ],
    "features-overview": [
        {"name": "features-extensions", "commands": ["echo 'claude mcp add-server ...'"], "title": "MCP Extensions"},
    ],
    "cli-reference": [
        {"name": "cli-help", "commands": ["claude --help 2>/dev/null || echo 'claude --help output'"], "title": "CLI Help"},
        {"name": "cli-print", "commands": ["echo 'claude -p \"list files\"'"], "title": "Print Mode"},
        {"name": "cli-continue", "commands": ["echo 'claude --continue'"], "title": "Continue Session"},
    ],
    "common-workflows": [
        {"name": "workflow-commit", "commands": ["echo 'claude \"commit these changes\"'"], "title": "Git Workflow"},
        {"name": "workflow-debug", "commands": ["echo 'claude \"fix the bug in auth.py\"'"], "title": "Debug Workflow"},
    ],
    "best-practices": [
        {"name": "best-practices-claude-md", "commands": ["echo 'cat CLAUDE.md'"], "title": "CLAUDE.md"},
        {"name": "best-practices-tips", "commands": ["echo 'claude \"review my code for best practices\"'"], "title": "Best Practices Review"},
    ],
    "how-claude-code-works": [
        {"name": "how-works-architecture", "commands": ["echo 'Claude Code Architecture: Agent Loop → Tools → Context'"], "title": "Architecture Overview"},
    ],
    "memory": [
        {"name": "memory-directory", "commands": ["echo 'ls .claude/'"], "title": ".claude Directory"},
        {"name": "memory-claude-md", "commands": ["echo 'cat .claude/CLAUDE.md'"], "title": "CLAUDE.md Memory"},
    ],
    "settings": [
        {"name": "settings-config", "commands": ["echo 'cat .claude/settings.json'"], "title": "Settings File"},
        {"name": "settings-global", "commands": ["echo 'cat ~/.claude/settings.json'"], "title": "Global Settings"},
    ],
    "permission-modes": [
        {"name": "permission-modes", "commands": ["echo 'claude --permission-mode plan'"], "title": "Permission Modes"},
        {"name": "permission-accept", "commands": ["echo 'claude --allowedTools Edit,Bash'"], "title": "Allowed Tools"},
    ],
    "context-window": [
        {"name": "context-window-size", "commands": ["echo 'claude --max-turns 10'"], "title": "Context Management"},
    ],
    "sub-agents": [
        {"name": "sub-agents-example", "commands": ["echo 'claude \"use sub-agent to analyze this file\"'"], "title": "Sub-agent Usage"},
    ],
    "agent-sdk/overview": [
        {"name": "agent-sdk-python", "commands": ["echo 'pip install claude-agent-sdk'"], "title": "Agent SDK Install"},
    ],
    "vs-code": [
        {"name": "vscode-extension", "commands": ["echo 'Install Claude Code extension from VS Code marketplace'"], "title": "VS Code Extension"},
    ],
    "jetbrains": [
        {"name": "jetbrains-plugin", "commands": ["echo 'Install Claude Code plugin from JetBrains marketplace'"], "title": "JetBrains Plugin"},
    ],
    "chrome": [
        {"name": "chrome-extension", "commands": ["echo 'Install Claude Code Chrome extension'"], "title": "Chrome Extension"},
    ],
    "slack": [
        {"name": "slack-integration", "commands": ["echo 'Add Claude Code bot to Slack workspace'"], "title": "Slack Integration"},
    ],
    "computer-use": [
        {"name": "computer-use-demo", "commands": ["echo 'claude \"use computer-use to browse this website\"'"], "title": "Computer Use"},
    ],
    "remote-control": [
        {"name": "remote-control-api", "commands": ["echo 'claude --remote-control'"], "title": "Remote Control"},
    ],
    "third-party-integrations": [
        {"name": "third-party-config", "commands": ["echo 'claude config set provider amazon-bedrock'"], "title": "Third-party Provider"},
    ],
    "platforms": [
        {"name": "platforms-list", "commands": ["echo 'Available: Terminal, VS Code, JetBrains, Desktop, Web'"], "title": "Available Platforms"},
    ],
    "claude-directory": [
        {"name": "claude-dir-structure", "commands": ["echo 'ls -la .claude/'"], "title": ".claude Directory Structure"},
    ],
    "legal-and-compliance": [
        {"name": "legal-compliance", "commands": ["echo 'cat .claude/settings.json | grep compliance'"], "title": "Compliance Settings"},
    ],
    "changelog": [
        {"name": "changelog-version", "commands": ["claude --version 2>/dev/null || echo 'claude v1.0.0'"], "title": "Current Version"},
    ],
}


def capture_topic_screenshots(topic: str, markers: list[dict] | None = None) -> dict[str, str]:
    """Capture screenshots for a topic. Returns dict of marker name -> image path."""
    screenshots = {}

    # Use markers from content if available, otherwise use default scenarios
    if markers:
        for marker in markers:
            name = marker["name"]
            # Try to find a matching default scenario
            scenarios = DEFAULT_SCENARIOS.get(topic, [])
            matched = next((s for s in scenarios if s["name"] == name), None)
            if matched:
                path = capture_cli_screenshot(
                    name=matched["name"],
                    commands=matched["commands"],
                    title=matched.get("title", "Terminal"),
                )
            else:
                # Generic screenshot with just the name
                path = capture_cli_screenshot(
                    name=name,
                    commands=[f"echo 'Screenshot: {name}'"],
                    title=name.replace("-", " ").title(),
                )
            screenshots[name] = path
    else:
        # Use default scenarios for the topic
        scenarios = DEFAULT_SCENARIOS.get(topic, [])
        for scenario in scenarios:
            path = capture_cli_screenshot(
                name=scenario["name"],
                commands=scenario["commands"],
                title=scenario.get("title", "Terminal"),
            )
            screenshots[scenario["name"]] = path

    return screenshots


if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "overview"
    result = capture_topic_screenshots(topic)
    for name, path in result.items():
        print(f"  {name}: {path}")
