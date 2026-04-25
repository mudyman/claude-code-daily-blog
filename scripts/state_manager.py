"""Track which topic was last published for the daily blog cycle."""

import json
from datetime import datetime
from pathlib import Path

import yaml

STATE_FILE = Path(__file__).parent.parent / "state" / "last_topic.json"
TOPICS_FILE = Path(__file__).parent.parent / "_data" / "topics.yml"


class StateManager:
    def __init__(self):
        self.state = self._load_state()
        self.topics = self._load_topics()

    def _load_state(self) -> dict:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return json.load(f)
        return {
            "last_topic_slug": None,
            "last_topic_index": -1,
            "last_published_date": None,
            "cycle_number": 1,
            "history": [],
        }

    def _load_topics(self) -> list[dict]:
        with open(TOPICS_FILE) as f:
            data = yaml.safe_load(f)
        return data["topics"]

    def get_next_topic(self, override: str | None = None) -> dict:
        """Get the next topic to publish. Returns the topic dict with slug and titles."""
        if override:
            for t in self.topics:
                if t["slug"] == override:
                    return t
            raise ValueError(f"Topic '{override}' not found in topics list")

        next_index = (self.state["last_topic_index"] + 1) % len(self.topics)
        return self.topics[next_index]

    def get_next_topic_after(self, slug: str) -> dict | None:
        """Get the topic that follows the given slug (for 'Coming Tomorrow' teaser)."""
        for i, t in enumerate(self.topics):
            if t["slug"] == slug:
                next_i = (i + 1) % len(self.topics)
                return self.topics[next_i]
        return None

    def advance_topic(self, topic_slug: str):
        """Record that a topic has been published."""
        index = next(
            i for i, t in enumerate(self.topics)
            if t["slug"] == topic_slug
        )
        today = datetime.now().strftime("%Y-%m-%d")

        # Detect cycle wrap
        if index == 0 and self.state["last_topic_index"] >= 0:
            self.state["cycle_number"] += 1

        self.state["last_topic_slug"] = topic_slug
        self.state["last_topic_index"] = index
        self.state["last_published_date"] = today

        self.state["history"].append({
            "date": today,
            "topic": topic_slug,
            "index": index,
            "cycle": self.state["cycle_number"],
        })

        # Keep only last 100 entries
        self.state["history"] = self.state["history"][-100:]
        self._save_state()

    def is_already_published_today(self) -> bool:
        """Check if a post was already published today."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.state["last_published_date"] == today

    def _save_state(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)


if __name__ == "__main__":
    sm = StateManager()
    next_topic = sm.get_next_topic()
    print(f"Next topic: {next_topic['slug']} ({next_topic['title_zh']})")
    print(f"Current cycle: {sm.state['cycle_number']}")
    print(f"Last published: {sm.state['last_published_date']}")
