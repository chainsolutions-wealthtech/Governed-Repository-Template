"""Observe the existing GRT bootstrap and emit the CASE 1 local handoff."""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import time
from urllib.parse import quote

from control_plane_create_repository import github_api
from control_plane_issue_bridge import api, emit_executor_outputs, extract_state, persist_state, render_response
from governed_request import CONTROL_PLANE_REPOSITORY, SHA40, apply_evidence
from project_continuity import IDENTITY, validate_projection


def attested_head(repository, branch, repository_id, initial_sha, read):
    ref = read(f"/repos/{repository}/git/ref/heads/{quote(branch, safe='')}")
    head = ref.get("object", {}).get("sha")
    if not isinstance(head, str) or not SHA40.fullmatch(head):
        raise ValueError("CUG_BOOTSTRAP_HEAD_UNVERIFIED")
    if head == initial_sha:
        return None
    raw = read(f"/repos/{repository}/contents/.governance/bootstrap-receipt.json?ref={head}", allow_404=True)
    if raw is None:
        return None
    if raw.get("encoding") != "base64":
        raise ValueError("CUG_BOOTSTRAP_RECEIPT_ENCODING_INVALID")
    receipt = json.loads(base64.b64decode(raw["content"]))
    subject = receipt.get("initialization_commit_sha")
    run_id = str(receipt.get("github_run_id") or "")
    version = receipt.get("template_revision")
    if (receipt.get("repository") != repository or receipt.get("canonical_branch") != branch
            or receipt.get("template_repository") != CONTROL_PLANE_REPOSITORY
            or receipt.get("input_head_sha") != initial_sha):
        raise ValueError("CUG_BOOTSTRAP_RECEIPT_TARGET_MISMATCH")
    if receipt.get("validation") == "PENDING":
        return None
    if (receipt.get("validation") != "PASS" or receipt.get("initialized") is not True
            or not isinstance(subject, str) or not SHA40.fullmatch(subject)
            or receipt.get("attestation_subject_sha") != subject
            or receipt.get("attestation_model") != "CHILD_COMMIT_ATTESTS_INITIALIZATION_COMMIT"
            or not re.fullmatch(r"[1-9][0-9]{0,19}", run_id)
            or not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version)):
        raise ValueError("CUG_BOOTSTRAP_RECEIPT_INVALID")
    for sha, parent in ((head, subject), (subject, initial_sha)):
        commit = read(f"/repos/{repository}/commits/{sha}")
        if commit.get("sha") != sha or [p.get("sha") for p in commit.get("parents", [])] != [parent]:
            raise ValueError("CUG_BOOTSTRAP_COMMIT_LINEAGE_MISMATCH")
    run = read(f"/repos/{repository}/actions/runs/{run_id}")
    if run.get("status") != "completed":
        return None
    if (str(run.get("id")) != run_id or str((run.get("repository") or {}).get("id")) != repository_id
            or str(run.get("path", "")).split("@", 1)[0] != ".github/workflows/governance-auto-bootstrap.yml"
            or run.get("head_sha") != initial_sha or run.get("conclusion") != "success"):
        raise ValueError("CUG_BOOTSTRAP_RUN_UNVERIFIED")
    jobs = read(f"/repos/{repository}/actions/runs/{run_id}/jobs").get("jobs", [])
    if not any(job.get("name") == "bootstrap" and job.get("conclusion") == "success"
               and any(step.get("name") == "Verify remote bootstrap attestation" and step.get("conclusion") == "success"
                       for step in job.get("steps", [])) for job in jobs):
        raise ValueError("CUG_BOOTSTRAP_ATTESTATION_STEP_UNVERIFIED")
    return {"bootstrap_success": True, "template_version": version, "final_head_sha": head, "run_id": run_id}


def prepare(state, repository, read, *, wait=time.sleep, attempts=12):
    identity = state[IDENTITY]
    info = read(f"/repos/{repository}")
    if info.get("full_name") != repository:
        raise ValueError("CUG_BOOTSTRAP_REPOSITORY_MISMATCH")
    validate_projection(identity, repository, info.get("id"))
    branch = info.get("default_branch")
    if not isinstance(branch, str) or not branch:
        raise ValueError("CUG_BOOTSTRAP_BRANCH_UNVERIFIED")
    if state.get("status") == "HANDOFF_READY":
        return state
    if (state.get("next_request") or {}).get("action_id") != "PREP-002":
        raise ValueError("CUG_BOOTSTRAP_UNEXPECTED_STATE")
    first = next(x["evidence"] for x in state["evidence"] if x["action_id"] == "PREP-001" and x["result"] == "PASS")
    if first["repository"] != repository or str(first["github_repository_id"]) != identity["github_repository_id"]:
        raise ValueError("CUG_BOOTSTRAP_CREATION_EVIDENCE_MISMATCH")
    for i in range(attempts):
        evidence = attested_head(repository, branch, identity["github_repository_id"], first["initial_head_sha"], read)
        if evidence is not None:
            new = apply_evidence(state, "PREP-002", "PASS", evidence)
            new = apply_evidence(new, "PREP-003", "PASS", {
                "server_status": "DISCOVERY_REQUIRED", "directory_status": "DISCOVERY_REQUIRED",
                "database_status": "UNRESOLVED", "access_status": "UNRESOLVED",
            })
            return apply_evidence(new, "PREP-004", "PASS", {
                "default_branch": branch, "head_sha": evidence["final_head_sha"],
            })
        if i + 1 < attempts:
            wait(10)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-number", required=True, type=int)
    args = parser.parse_args()
    issue = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{args.issue_number}")
    state = extract_state(issue.get("body"))
    if state.get("credential_provider") != "CUG":
        raise SystemExit("CUG_BOOTSTRAP_SOURCE_NOT_AUTHORIZED")
    if (state.get("next_request") or {}).get("action_id") == "PREP-001":
        raise SystemExit("CUG_CREATION_NOT_ATTESTED")
    if state.get("status") == "HANDOFF_READY":
        raise SystemExit("CUG_BOOTSTRAP_ALREADY_HANDED_OFF")
    target = state[IDENTITY]["github_repository"]
    token = os.environ["GOVERNED_BOOTSTRAP_READ_TOKEN"]
    result = prepare(state, target, lambda path, **options: github_api(token, "GET", path, **options))
    if result is None:
        print("CUG_BOOTSTRAP_WAITING_FOR_REMOTE_ATTESTATION")
        return
    persist_state(args.issue_number, issue.get("body"), result)
    api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{args.issue_number}/comments", {"body": render_response(result)})
    emit_executor_outputs(result, args.issue_number, local_start_payload={
        "target_repository": target, "expected_head": result["handoff"]["expected_head_sha"],
        "objective": result["initial_context"],
    })


if __name__ == "__main__":
    main()
