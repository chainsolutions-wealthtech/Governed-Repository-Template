from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from gacr_continuity_bus import make_dispatch_id, make_supervision_dispatch_id

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / ".governance/control-plane-state/namespace-work-registry.json"
DISPATCHES = ROOT / ".governance/control-plane-state/gacr-dispatches.json"


class GACRDispatchNamespaceAlignment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        namespaces = [n for n in data["namespaces"] if n.get("id") == "GACR-DISPATCH"]
        if len(namespaces) != 1:
            raise AssertionError("exactly one canonical GACR-D namespace required")
        cls.pattern = re.compile(namespaces[0]["pattern"])

    def test_live_dispatch_id_producers_match(self):
        cases = (
            make_dispatch_id("GACR-E-test", "session-test"),
            make_supervision_dispatch_id("GACR-SA-test"),
        )
        for value in cases:
            with self.subTest(dispatch_id=value):
                self.assertEqual(len(value.removeprefix("GACR-D-")), 16)
                self.assertIsNotNone(self.pattern.fullmatch(value))

    def test_current_persisted_dispatch_ids_match(self):
        persisted = json.loads(DISPATCHES.read_text(encoding="utf-8"))
        for item in persisted.get("items", []):
            dispatch_id = item.get("dispatch_id", "")
            if not dispatch_id.startswith("GACR-D-"):
                continue
            with self.subTest(dispatch_id=dispatch_id):
                self.assertIsNotNone(self.pattern.fullmatch(dispatch_id))

    def test_legacy_12_hex_is_preserved(self):
        self.assertIsNotNone(self.pattern.fullmatch("GACR-D-" + "a" * 12))

    def test_unknown_lengths_and_nonhex_are_denied(self):
        for value in (
            "GACR-D-" + "a" * 11,
            "GACR-D-" + "a" * 13,
            "GACR-D-" + "a" * 15,
            "GACR-D-" + "a" * 17,
            "GACR-D-" + "g" * 16,
        ):
            with self.subTest(value=value):
                self.assertIsNone(self.pattern.fullmatch(value))


if __name__ == "__main__":
    unittest.main()
