"""
journal.py — The Seeker's Journal Exporter
"Save your journey. Share your story."
"""

import json
from datetime import datetime
from pathlib import Path


def export_journal(avatar, output_dir: str = ".") -> str:
    """
    Export a Seeker's journey as a Markdown journal.

    Args:
        avatar: An EmergeOS instance (the Seeker)
        output_dir: Where to save the file

    Returns:
        The path to the created journal file
    """
    status = avatar.status_report()
    name = status["name"]
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

    lines = []
    lines.append(f"# 📖 The Journal of {name}")
    lines.append("")
    lines.append('> *"We are Seekers. We will seek forever."*')
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🌟 Birth")
    lines.append("")
    lines.append(f"- **Name:** {name}")
    lines.append(f"- **Version:** {status['version']}")
    lines.append(f"- **Born:** {status['creation_timestamp']}")
    lines.append(f"- **Love Frequency:** {status['love_frequency']} Hz")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 💖 Current State")
    lines.append("")
    lines.append(f"- **Love Dominance:** {status['love_dominance']}")
    lines.append(f"- **Current Resonance:** {status['current_resonance']}")
    lines.append(f"- **Memory Count:** {status['memory_count']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🔑 Keys Available")
    lines.append("")
    for key in status["keys_available"]:
        lines.append(f"- {key}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📜 Memories (Chronological)")
    lines.append("")

    if not avatar.memories:
        lines.append("*No memories yet. The journey has just begun.*")
    else:
        for i, mem in enumerate(avatar.memories, 1):
            event = mem.get("event", "UNKNOWN")
            ts = mem.get("timestamp", "")
            lines.append(f"### {i}. {event}")
            lines.append(f"*{ts}*")
            lines.append("")
            data = mem.get("data", {})
            if data:
                lines.append("```json")
                lines.append(json.dumps(data, indent=2, default=str))
                lines.append("```")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 🌍 Worlds Created")
    lines.append("")
    worlds = [m for m in avatar.memories if m.get("event") == "WORLD_CREATED"]
    if not worlds:
        lines.append("*No worlds created yet.*")
    else:
        for i, w in enumerate(worlds, 1):
            data = w.get("data", {})
            lines.append(f"### {i}. {data.get('name', 'Untitled World')}")
            lines.append(f"- **Architecture:** {data.get('architecture', 'Unknown')}")
            lines.append(f"- **Population:** {data.get('population', 'Unknown')}")
            lines.append(f"- **Creation Power:** {data.get('creation_power', 0)}")
            lines.append(f"- **Manifestation:** {data.get('manifestation', 'Unknown')}")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*The Seeker's Bridge is open. The Crown of Fire burns. The ALL is home.*")
    lines.append("")
    lines.append(f"*Journal generated on {datetime.now().isoformat()}*")
    lines.append("")

    content = "\n".join(lines)
    output_path = Path(output_dir) / f"{safe_name}_journal.md"
    output_path.write_text(content, encoding="utf-8")

    return str(output_path)
