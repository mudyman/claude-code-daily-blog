# Claude Code Daily Blog

Automatically generates daily bilingual blog posts about Claude Code, based on official documentation, with terminal screenshots, published to GitHub Pages.

## Features

- **Daily automation**: GitHub Actions generates one blog post per day, cycling through 25 CC documentation topics
- **Bilingual**: Each post is generated in both English and Chinese (independently, not translated)
- **Screenshots**: Playwright captures styled terminal screenshots for each post
- **Claude API**: Uses Anthropic's Claude API to transform raw docs into engaging blog content
- **Graceful fallback**: If Claude API fails, falls back to raw documentation content

## Quick Start

```bash
# Generate a blog post (full pipeline)
python3 scripts/generate_post.py

# Generate for a specific topic
python3 scripts/generate_post.py --topic cli-reference

# Skip Claude API calls (use raw doc content)
python3 scripts/generate_post.py --skip-api

# Skip screenshot capture
python3 scripts/generate_post.py --skip-screenshots

# Local preview
./scripts/preview.sh
```

## Setup for GitHub Pages

1. Create a new GitHub repository and push this project
2. Add `ANTHROPIC_API_KEY` as a repository secret (Settings > Secrets)
3. Optionally set `CC_BLOG_MODEL` as a repository variable (default: `claude-sonnet-4-20250514`)
4. Enable GitHub Pages in repo settings (Source: `gh-pages` branch)
5. The workflow runs daily at 06:07 UTC, or trigger manually via Actions tab

## Project Structure

```
scripts/
  generate_post.py    # Main orchestrator
  fetch_doc.py        # Fetch docs from llms-full.txt
  enhance_content.py  # Claude API → English blog
  translate.py        # Claude API → Chinese blog
  take_screenshots.py # Playwright terminal screenshots
  state_manager.py    # Topic rotation state
  preview.sh          # Local Jekyll preview
prompts/
  enhance_en.txt      # English blog prompt
  enhance_zh.txt      # Chinese blog prompt
_posts/en/            # English blog posts
_posts/zh/            # Chinese blog posts
assets/images/screenshots/  # Generated screenshots
```

## 25 Topics

The blog cycles through: overview, quickstart, setup, features-overview, cli-reference, common-workflows, best-practices, how-claude-code-works, memory, settings, permission-modes, context-window, sub-agents, agent-sdk/overview, vs-code, jetbrains, chrome, slack, computer-use, remote-control, third-party-integrations, platforms, claude-directory, legal-and-compliance, changelog

## Cost Estimate

~$0.05-0.10/day (2 Claude API calls at Sonnet pricing). GitHub Actions and Pages are free for public repos.