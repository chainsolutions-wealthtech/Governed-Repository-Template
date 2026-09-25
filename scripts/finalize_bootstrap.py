#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA40 = re.compile(r"^[0-9a-f]{40}$")
ATTESTATION_MODEL = "CHILD_COMMIT_ATTESTS_INITIALIZATION_COMMIT"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--initialization-commit-sha", required=True)
    args = p.parse_args()
    initialization_commit_sha = args.initialization_commit_sha.lower()
    if not SHA40.fullmatch(initialization_commit_sha):
        raise SystemExit("BOOTSTRAP_ATTESTATION_FAILED: initialization commit SHA must be 40 lowercase hex characters")

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    receipt_path = ROOT / ".governance" / "bootstrap-receipt.json"
    state_path = ROOT / ".governance" / "bootstrap-state.json"
    memory_path = ROOT / ".governance" / "canonical-memory" / "current.json"
    status_path = ROOT / "STATUS.md"
    loop_state_path = ROOT / "LOOP_STATE.md"
    work_log_path = ROOT / "WORK_LOG.md"
    suivi_path = ROOT / "SUIVI.md"

    receipt = read_json(receipt_path)
    state = read_json(state_path)
    memory = read_json(memory_path)

    receipt["initialization_commit_sha"] = initialization_commit_sha
    receipt["attestation_subject_sha"] = initialization_commit_sha
    receipt["attestation_model"] = ATTESTATION_MODEL
    receipt["validation"] = "PASS"
    receipt["attested_at"] = now

    state["status"] = "PASS"
    state["attested_initialization_commit_sha"] = initialization_commit_sha
    state["attestation_subject_sha"] = initialization_commit_sha
    state["attestation_model"] = ATTESTATION_MODEL
    state["attested_at"] = now

    # This SHA is the content state being attested. The attestation commit that
    # contains this value is necessarily its child: a commit cannot embed its
    # own final SHA without changing that SHA.
    memory["observed_head_sha"] = initialization_commit_sha
    memory["bootstrap_attestation_subject_sha"] = initialization_commit_sha
    memory["attestation_model"] = ATTESTATION_MODEL
    memory["freshness"] = "ATTESTED"
    memory["current_checkpoint"] = "bootstrap"
    memory["canonical_revision"] = max(1, int(memory.get("canonical_revision", 0)))
    memory["work_revision"] = max(1, int(memory.get("work_revision", 0)))

    write_json(receipt_path, receipt)
    write_json(state_path, state)
    write_json(memory_path, memory)

    repository = receipt.get("repository") or "UNKNOWN"
    canonical_branch = receipt.get("canonical_branch") or "UNKNOWN"
    input_head = receipt.get("input_head_sha") or "UNKNOWN"
    next_action = receipt.get("next_action") or memory.get("next_action") or "DISCOVER_PROJECT_BASELINE"
    status_path.write_text(
        "# STATUS — État courant\n\n"
        "> State: `GOVERNANCE_INITIALIZED_BASELINE_REQUIRED`\n\n"
        f"- Repository: `{repository}`\n"
        f"- Branch: `{canonical_branch}`\n"
        f"- Bootstrap input HEAD: `{input_head}`\n"
        f"- Attested initialization commit: `{initialization_commit_sha}`\n"
        "- Governance validation: `PASS`\n"
        "- Governance freshness: `ATTESTED`\n"
        f"- Next action: `{next_action}`\n\n"
        "The attestation commit is the Git child commit containing this state; "
        "its remote presence is verified by the bootstrap workflow.\n\n"
        "No production, deployment, compliance, legal, financial or operational status is implied.\n",
        encoding="utf-8",
    )

    loop_state_path.write_text(
        "# LOOP_STATE — État de la boucle\n\n"
        "```json\n"
        "{\n"
        '  "loop_id": "LOOP-INIT-001",\n'
        '  "state": "IN_PROGRESS",\n'
        '  "phase": "DISCOVER",\n'
        f'  "repository": "{repository}",\n'
        f'  "canonical_branch": "{canonical_branch}",\n'
        '  "baseline_head": "TO_CAPTURE",\n'
        f'  "next_action": "{next_action}",\n'
        '  "last_verification": "GOVERNANCE_BOOTSTRAP_ATTESTED"\n'
        "}\n"
        "```\n",
        encoding="utf-8",
    )

    work_log = work_log_path.read_text(encoding="utf-8")
    if "- Result: `PENDING`" in work_log:
        work_log = work_log.replace("- Result: `PENDING`", "- Result: `PASS`", 1)
    if "- Bootstrap attestation: `PASS`" not in work_log:
        work_log = work_log.rstrip() + (
            "\n- Bootstrap attestation: `PASS`"
            f"\n- Attested initialization commit: `{initialization_commit_sha}`"
            f"\n- GitHub run: `{receipt.get('github_run_id') or 'UNKNOWN'}`\n"
        )
    work_log_path.write_text(work_log, encoding="utf-8")

    suivi = suivi_path.read_text(encoding="utf-8")
    if "- State: `INITIALIZATION_REQUIRED`" in suivi:
        suivi = suivi.replace(
            "- State: `INITIALIZATION_REQUIRED`",
            "- State: `GOVERNANCE_INITIALIZED_BASELINE_REQUIRED`",
            1,
        )
    if "- Bootstrap attestation: `PASS`" not in suivi:
        suivi = suivi.rstrip() + (
            "\n\n## Bootstrap attestation\n\n"
            "- Bootstrap attestation: `PASS`\n"
            f"- Attested initialization commit: `{initialization_commit_sha}`\n"
            "- Next action: `DISCOVER_PROJECT_BASELINE`\n"
        )
    suivi_path.write_text(suivi, encoding="utf-8")

    print(f"BOOTSTRAP_ATTESTATION_PASS: {initialization_commit_sha}")


if __name__ == "__main__":
    main()
