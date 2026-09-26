#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=repo, text=True, capture_output=True, check=check)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="adoption-selftest-") as tmp:
        target = Path(tmp) / "existing"
        target.mkdir()
        run(target, "git", "init", "-b", "main")
        run(target, "git", "config", "user.name", "Existing Project")
        run(target, "git", "config", "user.email", "existing@example.invalid")
        original_readme = "# Existing Project\n\nHistorical content must remain byte-for-byte unchanged.\n"
        (target / "README.md").write_text(original_readme, encoding="utf-8")
        (target / "app.txt").write_text("existing-application-data\n", encoding="utf-8")
        run(target, "git", "add", "-A")
        run(target, "git", "commit", "-m", "existing baseline")
        head = run(target, "git", "rev-parse", "HEAD").stdout.strip()

        plan = subprocess.run([
            sys.executable, str(ROOT / "scripts" / "adopt_existing_repository.py"),
            "--target", str(target),
            "--repository", "chainsolutions-wealthtech/existing-selftest",
            "--mode", "plan",
        ], cwd=ROOT, text=True, capture_output=True, check=True)
        payload = json.loads(plan.stdout)
        readme = next(item for item in payload["entries"] if item["path"] == "README.md")
        if readme["action"] != "PRESERVE_EXISTING":
            raise SystemExit("ADOPTION_SELFTEST_FAILED: existing README not preserved")
        if run(target, "git", "status", "--porcelain").stdout.strip():
            raise SystemExit("ADOPTION_SELFTEST_FAILED: plan mode modified target")

        applied = subprocess.run([
            sys.executable, str(ROOT / "scripts" / "adopt_existing_repository.py"),
            "--target", str(target),
            "--repository", "chainsolutions-wealthtech/existing-selftest",
            "--repository-scope", "ORGANIZATION",
            "--mode", "apply",
            "--expected-head", head,
        ], cwd=ROOT, text=True, capture_output=True, check=True)
        result = json.loads(applied.stdout)
        if result.get("existing_files_overwritten") != 0:
            raise SystemExit("ADOPTION_SELFTEST_FAILED: overwrite reported")
        if (target / "README.md").read_text(encoding="utf-8") != original_readme:
            raise SystemExit("ADOPTION_SELFTEST_FAILED: README changed")
        if (target / "app.txt").read_text(encoding="utf-8") != "existing-application-data\n":
            raise SystemExit("ADOPTION_SELFTEST_FAILED: application content changed")
        for relative in ["docs/control-plane", ".governance/control-plane-state", ".governance/control-plane-db"]:
            if (target / relative).exists():
                raise SystemExit("ADOPTION_SELFTEST_FAILED: source-only control-plane memory leaked: " + relative)

        profile = json.loads((target / ".governance" / "profile.json").read_text(encoding="utf-8"))
        if profile.get("initialization_mode") != "EXISTING_REPOSITORY_ADOPTION":
            raise SystemExit("ADOPTION_SELFTEST_FAILED: adoption mode missing")
        state = json.loads((target / ".governance" / "adoption" / "state.json").read_text(encoding="utf-8"))
        if state.get("existing_files_overwritten") != 0:
            raise SystemExit("ADOPTION_SELFTEST_FAILED: state reports overwrite")

        subprocess.run([sys.executable, "scripts/validate_governance.py"], cwd=target, check=True)
        print("REPOSITORY_ADOPTION_SELFTEST_PASS")


if __name__ == "__main__":
    main()
