#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
paths = [
    ".github/copilot-instructions.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
]

for rel in paths:
    text = (ROOT / rel).read_text(encoding="utf-8")
    assert "00_GSCC_ENTRY.md" in text, f"{rel}: missing GSCC entry pointer"

copilot = (ROOT / ".github/copilot-instructions.md").read_text(encoding="utf-8")
assert "priority over every other repository instruction" in copilot
assert "00_START_HERE.md" in copilot
assert "UNAVAILABLE" in copilot

agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
assert "PRIORITÉ ABSOLUE D'ENTRÉE" in agents

print("Agent auto-discovery pointers: PASS")
