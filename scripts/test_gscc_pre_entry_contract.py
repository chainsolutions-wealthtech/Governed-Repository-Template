#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

entry = (ROOT / "00_GSCC_ENTRY.md").read_text(encoding="utf-8")
start = (ROOT / "00_START_HERE.md").read_text(encoding="utf-8")
agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

assert "00_GSCC_ENTRY" in entry
assert "GSCC" in entry and "GSE" in entry and "GACR" in entry
assert "00_START_HERE.md" in entry
assert "START_HERE_STATUS = NOT_YET_APPLICABLE" in entry
assert "UNAVAILABLE" in entry
assert "FIRST_TOUCH" in entry and "CONTINUATION" in entry and "UNRESOLVED" in entry

assert "PRECONDITION ABSOLUE" in start
assert "00_GSCC_ENTRY.md" in start
assert "GSCC → GSE → GACR" in start
assert "revenir à `00_GSCC_ENTRY.md`" in start

assert "0. lire et satisfaire `00_GSCC_ENTRY.md`" in agents
assert "aucun agent ou nouvelle conversation ne peut entrer directement" in agents

print("GSCC pre-entry contract: PASS")
