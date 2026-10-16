from __future__ import annotations

import ast
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SOURCE = SCRIPTS / "gscc" / "admission_harvester.py"
MODULE = "gscc_gacr.admission_gse_projection"
SYMBOL = "project_pre_gacr_admission_gse_state"


class HarvesterImportParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        matches = [
            node for node in cls.tree.body
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id == "__package__"
        ]
        if len(matches) != 1:
            raise AssertionError("expected exactly one package/direct-script import switch")
        cls.mode = matches[0]

    def test_projection_imported_in_both_execution_modes(self):
        for label, statements in (
            ("package", self.mode.body),
            ("direct-script", self.mode.orelse),
        ):
            with self.subTest(mode=label):
                imported = {
                    alias.name
                    for node in statements
                    if isinstance(node, ast.ImportFrom)
                    and node.module == MODULE
                    for alias in node.names
                }
                self.assertIn(SYMBOL, imported)

    def test_projector_is_actually_invoked(self):
        calls = [
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == SYMBOL
        ]
        self.assertTrue(calls, "projector must be called by harvester")

    def test_both_python_entry_modes_start(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(SCRIPTS) + os.pathsep + env.get("PYTHONPATH", "")
        commands = (
            [sys.executable, str(SOURCE), "--help"],
            [sys.executable, "-m", "gscc.admission_harvester", "--help"],
        )
        for command in commands:
            with self.subTest(command=command):
                proc = subprocess.run(
                    command, cwd=ROOT, env=env, capture_output=True,
                    text=True, check=False, timeout=30,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
