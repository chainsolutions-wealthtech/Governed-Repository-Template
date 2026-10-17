#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from governed_hold_review import MERGED_PR_REF, reexamine_authority_hold
from governed_plan_reconciliation import reconcile_existing_merged_lab
from governed_gr302_reconciliation import reconcile_stale_lab_plan, BRANCH as GR302_BRANCH

from governed_request import (
    CREATE_OWNER_CANONICAL,
    apply_answer,
    apply_evidence,
    decode_state,
    encode_state,
    new_request,
)

CONTROL_PLANE_REPOSITORY = "chainsolutions-wealthtech/Governed-Repository-Template"
MARKER_RE = re.compile(r"\n?<!-- GOVERNED_REQUEST_STATE:([A-Za-z0-9_-]+) -->\s*$", re.S)


def api(method: str, path: str, payload: dict | None = None) -> dict:
    token = os.environ["GITHUB_TOKEN"]
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "governed-repository-control-plane",
        },
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {body}") from exc


def strip_marker(body: str | None) -> str:
    return MARKER_RE.sub("", body or "").rstrip()


def extract_state(body: str | None) -> dict:
    match = MARKER_RE.search(body or "")
    if not match:
        raise ValueError("governed request state marker is missing")
    return decode_state(match.group(1))


def persist_state(issue_number: int, original_body: str | None, state: dict) -> None:
    clean = strip_marker(original_body)
    encoded = encode_state(state)
    body = clean + f"\n\n<!-- GOVERNED_REQUEST_STATE:{encoded} -->\n"
    api("PATCH", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{issue_number}", {"body": body})


def parse_command(body: str) -> tuple[str, dict] | None:
    stripped = body.strip()
    if stripped == "/governed-execute":
        return "execute", {}
    if stripped.startswith("/governed-review-hold "):
        return "review_hold", json.loads(stripped[len("/governed-review-hold "):].strip())
    if stripped.startswith("/governed-reconcile-gr302 "):
        return "reconcile_gr302", json.loads(stripped[len("/governed-reconcile-gr302 "):].strip())
    if stripped.startswith("/governed-reconcile-plan "):
        return "reconcile_plan", json.loads(stripped[len("/governed-reconcile-plan "):].strip())
    if stripped.startswith("/governed-answer"):
        raw = stripped[len("/governed-answer"):].strip()
        return "answer", json.loads(raw)
    if stripped.startswith("/governed-evidence"):
        raw = stripped[len("/governed-evidence"):].strip()
        return "evidence", json.loads(raw)
    if stripped.startswith("/governed-upgrade-local-entry"):
        raw = stripped[len("/governed-upgrade-local-entry"):].strip()
        return "upgrade_local_entry", json.loads(raw)
    if stripped.startswith("/governed-local-command"):
        raw = stripped[len("/governed-local-command"):].strip()
        return "local_command", json.loads(raw)
    if stripped.startswith("/governed-local-start"):
        raw = stripped[len("/governed-local-start"):].strip()
        return "local_start", json.loads(raw)
    return None


def pretty_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def render_response(state: dict) -> str:
    lines = [
        f"## Governed Control Plane — {state['request_id']}",
        "",
        f"- Status: `{state['status']}`",
        f"- Phase: `{state['phase']}`",
        f"- Revision: `{state['revision']}`",
        "",
    ]
    next_request = state.get("next_request")
    if next_request:
        kind = next_request.get("kind")
        lines.append(f"### {kind}")
        lines.append("")
        lines.append(next_request.get("text", ""))
        lines.append("")
        if next_request.get("choices") is not None:
            lines.append("Choix autorisés :")
            lines.append("")
            for choice in next_request["choices"]:
                lines.append(f"- `{json.dumps(choice, ensure_ascii=False)}`")
            lines.append("")
        if kind in {"QUESTION", "AGENT_REQUEST", "PLAN_APPROVAL"}:
            field = next_request.get("field")
            lines.extend([
                "Répondre avec :",
                "",
                "```text",
                "/governed-answer",
                pretty_json({"field": field, "value": "<value>"}),
                "```",
                "",
            ])
            if next_request.get("required_response"):
                lines.extend([
                    "Réponse structurée attendue pour `value` :",
                    "",
                    "```json",
                    pretty_json(next_request["required_response"]),
                    "```",
                    "",
                ])
            if kind == "PLAN_APPROVAL":
                lines.extend([
                    "Plan préparatoire proposé :",
                    "",
                    "```json",
                    pretty_json(next_request.get("plan", [])),
                    "```",
                    "",
                ])
        elif kind == "ACTION_REQUEST":
            lines.extend([
                f"Target: `{next_request.get('target')}`",
                f"Mutation class: `{next_request.get('mutation_class')}`",
                "",
                "Une fois l'action exécutée par l'agent connecté et les preuves recueillies :",
                "",
                "```text",
                "/governed-evidence",
                pretty_json({
                    "action_id": next_request["action_id"],
                    "result": "PASS",
                    "evidence": next_request.get("required_evidence", {}),
                }),
                "```",
                "",
            ])
        elif kind == "HANDOFF":
            lines.extend([
                "### HANDOFF READY",
                "",
                "```json",
                pretty_json(next_request.get("handoff")),
                "```",
                "",
                "Le control plane a terminé la préparation. Réobserver le HEAD indiqué avant toute écriture dans le repository cible.",
            ])

    if state.get("status") == "HOLD_FOR_REVIEW":
        lines.extend([
            "### HOLD_FOR_REVIEW",
            "",
            state.get("hold_reason") or "La demande est bloquée jusqu'à résolution explicite.",
        ])
    return "\n".join(lines)


def emit_executor_outputs(
    state: dict,
    issue_number: int,
    upgrade_payload: dict | None = None,
    local_command_payload: dict | None = None,
    local_start_payload: dict | None = None,
) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    next_request = state.get("next_request") or {}
    required = (
        state.get("answers", {}).get("entry_action") == "CREATE_NEW_REPOSITORY"
        and next_request.get("kind") == "ACTION_REQUEST"
        and next_request.get("action_id") == "PREP-001"
    )
    lines = [
        f"executor_required={'true' if required else 'false'}",
        f"upgrade_required={'true' if upgrade_payload else 'false'}",
        f"local_command_required={'true' if local_command_payload else 'false'}",
        f"local_start_required={'true' if local_start_payload else 'false'}",
        f"issue_number={issue_number}",
    ]
    if upgrade_payload:
        target_repository = str(upgrade_payload.get("target_repository") or "")
        expected_head = str(upgrade_payload.get("expected_head") or "")
        if "/" not in target_repository or len(expected_head) != 40:
            raise ValueError("upgrade payload requires target_repository owner/name and expected_head")
        lines.extend([
            f"upgrade_target_repository={target_repository}",
            f"upgrade_target_owner={target_repository.split('/',1)[0]}",
            f"upgrade_expected_head={expected_head}",
        ])
    if local_command_payload:
        expected = {"target_repository", "issue_number", "expected_head", "command"}
        if set(local_command_payload) != expected:
            raise ValueError("local command payload must contain target_repository, issue_number, expected_head and command")
        target_repository = str(local_command_payload.get("target_repository") or "")
        target_issue = local_command_payload.get("issue_number")
        expected_head = str(local_command_payload.get("expected_head") or "")
        command = local_command_payload.get("command")
        if "/" not in target_repository or not isinstance(target_issue, int) or target_issue < 1:
            raise ValueError("local command target_repository/issue_number invalid")
        if not re.fullmatch(r"[0-9a-f]{40}", expected_head):
            raise ValueError("local command expected_head must be a lowercase 40-char SHA")
        if not isinstance(command, dict) or command.get("kind") not in {"execute", "answer"}:
            raise ValueError("local command kind must be execute or answer")
        if command.get("kind") == "answer" and set(command) != {"kind", "field", "value"}:
            raise ValueError("local answer command requires kind, field and value")
        if command.get("kind") == "execute" and set(command) != {"kind"}:
            raise ValueError("local execute command requires only kind")
        command_b64 = base64.urlsafe_b64encode(
            json.dumps(command, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ).decode("ascii").rstrip("=")
        lines.extend([
            f"local_command_kind={command.get('kind','')}",
            f"local_command_target_repository={target_repository}",
            f"local_command_target_owner={target_repository.split('/',1)[0]}",
            f"local_command_target_issue={target_issue}",
            f"local_command_expected_head={expected_head}",
            f"local_command_b64={command_b64}",
        ])
    if local_start_payload:
        expected = {"target_repository", "expected_head", "objective"}
        if set(local_start_payload) != expected:
            raise ValueError("local start payload must contain target_repository, expected_head and objective")
        target_repository = str(local_start_payload.get("target_repository") or "")
        expected_head = str(local_start_payload.get("expected_head") or "")
        objective = str(local_start_payload.get("objective") or "").strip()
        if "/" not in target_repository:
            raise ValueError("local start target_repository invalid")
        if not re.fullmatch(r"[0-9a-f]{40}", expected_head):
            raise ValueError("local start expected_head must be a lowercase 40-char SHA")
        if not objective:
            raise ValueError("local start objective is required")
        objective_b64 = base64.urlsafe_b64encode(objective.encode("utf-8")).decode("ascii").rstrip("=")
        lines.extend([
            f"local_start_target_repository={target_repository}",
            f"local_start_target_owner={target_repository.split('/',1)[0]}",
            f"local_start_expected_head={expected_head}",
            f"local_start_objective_b64={objective_b64}",
        ])
    if required:
        lines.extend([
            f"target_owner_label={state['answers'].get('creation_target_owner', '')}",
            f"target_owner_canonical={CREATE_OWNER_CANONICAL.get(state['answers'].get('creation_target_owner', ''), '')}",
            f"repository_name={state['answers'].get('repository_name', '')}",
            f"visibility={state['answers'].get('visibility', '')}",
        ])
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def handle_opened(event: dict) -> None:
    issue = event["issue"]
    if not str(issue.get("title", "")).startswith("[Governed Request]"):
        return
    number = issue["number"]
    request_id = f"GR-{number:06d}"
    actor = (event.get("sender") or {}).get("login")
    state = new_request(request_id, actor, "github", strip_marker(issue.get("body")))
    persist_state(number, issue.get("body"), state)
    api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{number}/comments", {"body": render_response(state)})
    emit_executor_outputs(state, number)


def handle_comment(event: dict) -> None:
    issue = event["issue"]
    if not str(issue.get("title", "")).startswith("[Governed Request]"):
        return
    comment = event["comment"]
    command = parse_command(comment.get("body") or "")
    if command is None:
        return

    kind, payload = command
    if kind == "reconcile_gr302":
        try:
            if issue.get("number") != 302 or not isinstance(payload, dict) or set(payload) != {
                "expected_revision", "expected_head", "reason"
            }:
                raise ValueError("GR302_EXACT_ISSUE_AND_FIELDS_REQUIRED")
            actor = str((event.get("sender") or {}).get("login") or "")
            author = str((comment.get("user") or {}).get("login") or "")
            association = str(comment.get("author_association") or "")
            comment_id = comment.get("id")
            if actor != "Wealthtechinnovations" or author != actor or (
                not isinstance(comment_id, int) or comment_id <= 0
            ):
                raise ValueError("GR302_AUTHENTICATED_OWNER_COMMENT_REQUIRED")
            target = f"/repos/{CONTROL_PLANE_REPOSITORY}"
            latest = api("GET", f"{target}/issues/302")
            if latest.get("number") != 302:
                raise ValueError("GR302_ISSUE_MISMATCH")
            old = extract_state(latest.get("body"))
            observed = api("GET", f"{target}/branches/main")
            live_head = (observed.get("commit") or {}).get("sha")
            # Only authenticated 404 means absence. Never convert 403/5xx into absence.
            try:
                api("GET", f"{target}/branches/lab%2Fchainflow-live-poc")
            except RuntimeError as error:
                if f"GitHub API GET {target}/branches/lab%2Fchainflow-live-poc failed: 404 " not in str(error):
                    raise
            else:
                raise ValueError("GR302_LAB_ALREADY_EXISTS")
            updated = reconcile_stale_lab_plan(
                old,
                expected_revision=payload["expected_revision"],
                expected_head=payload["expected_head"],
                observed_head=live_head,
                owner_actor=actor,
                event_author=author,
                author_association=association,
                branch_absent=True,
                observation_evidence=f"github-issue-comment:{comment_id}",
                reason=payload["reason"],
            )
            # Re-read both source revision and mutable HEAD directly before PATCH.
            # This is an optimistic recheck; no false claim of GitHub issue CAS.
            immediately_before = api("GET", f"{target}/issues/302")
            current_head = api("GET", f"{target}/branches/main")
            if (immediately_before.get("body") != latest.get("body") or
                    (current_head.get("commit") or {}).get("sha") != live_head):
                raise ValueError("GR302_PRE_PERSIST_CONCURRENT_CHANGE")
            persist_state(302, immediately_before.get("body"), updated)
            api("POST", f"{target}/issues/302/comments", {
                "body": (
                    "### GR-000302 stale PREP-003 reconciled, not executed\n\n"
                    f"Reconciliation: {updated['preparation_reconciliation_history'][-1]['id']}\n"
                    f"Rev {old['revision']} -> {updated['revision']}; main {live_head}\n"
                    "PREP-001/002 original PASS proofs archived verbatim. "
                    "A new owner plan approval and PREP-002R live read proof are required. "
                    "No LAB created, no GACR claim, lease, WRITE or merge grant."
                )
            })
            api("POST", f"{target}/issues/302/comments", {"body": render_response(updated)})
            emit_executor_outputs(updated, 302)
        except Exception as exc:
            api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/302/comments", {
                "body": (
                    "### GR302 reconciliation refused\n\n"
                    f"{type(exc).__name__}: {exc}\n"
                    "No reconciled state, branch or grant is attested by this refusal."
                )
            })
        return

    if kind == "reconcile_plan":
        try:
            if not isinstance(payload, dict) or set(payload) != {
                "expected_revision", "expected_head", "reason"
            }:
                raise ValueError("LAB_PLAN_RECONCILE_EXACT_FIELDS_REQUIRED")
            actor = str((event.get("sender") or {}).get("login") or "")
            commenter = str(((comment.get("user") or {}).get("login") or ""))
            association = str(comment.get("author_association") or "")
            if not actor or actor != commenter:
                raise ValueError("LAB_PLAN_RECONCILE_EVENT_ACTOR_MISMATCH")
            number = issue["number"]
            latest = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{number}")
            if latest.get("number") != number:
                raise ValueError("LAB_PLAN_RECONCILE_ISSUE_MISMATCH")
            state = extract_state(latest.get("body"))
            canonical = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/branches/main")
            current_head = (canonical.get("commit") or {}).get("sha")
            historical = api(
                "GET",
                f"/repos/{CONTROL_PLANE_REPOSITORY}/branches/lab%2Fcodeagent-gscc-f1-q12-renewal-284",
            )
            branch_head = (historical.get("commit") or {}).get("sha")
            merged_pr = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/pulls/316")
            updated = reconcile_existing_merged_lab(
                state,
                expected_revision=payload["expected_revision"],
                expected_main_head=payload["expected_head"],
                live_main_head=current_head,
                owner_actor=actor,
                author_association=association,
                branch_head=branch_head,
                merged_pr=merged_pr,
                reason=payload["reason"],
            )
            persist_state(number, latest.get("body"), updated)
            journal = updated["plan_reconciliation_history"][-1]
            api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{number}/comments", {
                "body": (
                    "### Existing merged LAB — original plan superseded (read-only)\n\n"
                    f"Review: `{journal['id']}`\n"
                    f"Revision: `{journal['revision_before']}` → `{journal['revision_after']}`\n"
                    f"main HEAD: `{current_head}`\n"
                    f"Existing branch HEAD: `{branch_head}`\n"
                    "Verified PR #316 merged into main; previous plan remains in "
                    "`plan_reconciliation_history`. All replacement steps are read-only. "
                    "The previous `lab_authority=true` answer does not grant a work claim, "
                    "write authority or a new LAB. A new explicit plan approval is required."
                )
            })
            api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{number}/comments", {
                "body": render_response(updated)
            })
            emit_executor_outputs(updated, number)
        except Exception as exc:
            api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{issue['number']}/comments", {
                "body": (
                    "### Existing LAB plan reconciliation refused\n\n"
                    f"`{type(exc).__name__}: {exc}`\n\n"
                    "No branch, authority, claim, or plan state was advanced by this refusal."
                )
            })
        return

    if kind == "review_hold":
        try:
            if not isinstance(payload, dict) or set(payload) != {
                "expected_revision", "expected_head", "reason", "evidence_refs"
            }:
                raise ValueError("HOLD_REVIEW_EXACT_FIELDS_REQUIRED")
            actor = str((event.get("sender") or {}).get("login") or "")
            comment_author = str((comment.get("user") or {}).get("login") or "")
            author_association = str(comment.get("author_association") or "")
            if not actor or actor != comment_author:
                raise ValueError("HOLD_REVIEW_EVENT_ACTOR_MISMATCH")
            # The issue payload on an issue_comment webhook can be stale.
            # Reload the SAME issue body from GitHub just before transition.
            number = issue["number"]
            latest_issue = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{number}")
            if latest_issue.get("number") != number:
                raise ValueError("HOLD_REVIEW_ISSUE_MISMATCH")
            state = extract_state(latest_issue.get("body"))
            # Independently read canonical branch HEAD, rather than trusting
            # a user-supplied SHA in a comment or historical arrival.
            branch = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/branches/main")
            observed_head = ((branch.get("commit") or {}).get("sha"))
            evidence_refs = payload["evidence_refs"]
            if (not isinstance(evidence_refs, list) or len(evidence_refs) > 8
                    or not evidence_refs or any(
                        not isinstance(ref, str) or not MERGED_PR_REF.fullmatch(ref)
                        for ref in evidence_refs
                    )):
                raise ValueError("HOLD_REVIEW_MERGED_PR_REFERENCES_REQUIRED")
            for ref in evidence_refs:
                pr_number = int(MERGED_PR_REF.fullmatch(ref).group(1))
                pr = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/pulls/{pr_number}")
                if (pr.get("number") != pr_number or not pr.get("merged_at")
                        or ((pr.get("base") or {}).get("ref") != "main")):
                    raise ValueError("HOLD_REVIEW_EVIDENCE_PR_NOT_MERGED_TO_MAIN")
            updated = reexamine_authority_hold(
                state,
                expected_revision=payload["expected_revision"],
                expected_head=payload["expected_head"],
                observed_head=observed_head,
                owner_actor=actor,
                author_association=author_association,
                evidence_refs=evidence_refs,
                reason=payload["reason"],
            )
            persist_state(number, latest_issue.get("body"), updated)
            history = updated["hold_review_history"][-1]
            api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{number}/comments", {
                "body": (
                    "### Governed HOLD review — question reopened, no authority granted\\n\\n"
                    f"Review: `{history['id']}`\\n"
                    f"Old revision: `{history['revision_before']}`; "
                    f"new revision: `{history['revision_after']}`\\n"
                    f"Verified branch HEAD: `{history['verified_head']}`\\n"
                    f"Owner actor: `{actor}`\\n"
                    f"Merged evidence: {', '.join(evidence_refs)}\\n"
                    "Original denial retained in hold_review_history. "
                    "A new target HEAD observation and a new explicit owner LAB authority "
                    "answer are required; neither a LAB grant nor a claim nor merge authority was issued."
                )
            })
            api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{number}/comments", {
                "body": render_response(updated)
            })
            emit_executor_outputs(updated, number)
        except Exception as exc:
            api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{issue['number']}/comments", {
                "body": (
                    "### Governed HOLD review refused\\n\\n"
                    f"`{type(exc).__name__}: {exc}`\\n\\n"
                    "No successful owner-authority re-examination is attested by this refusal."
                )
            })
        return

    state = extract_state(issue.get("body"))
    try:
        if kind == "answer":
            if set(payload) != {"field", "value"}:
                raise ValueError("answer payload must contain exactly field and value")
            if state.get("gr302_reconciliation_pending") and payload["field"] == "plan_approved":
                actor = str((event.get("sender") or {}).get("login") or "")
                author = str((comment.get("user") or {}).get("login") or "")
                association = str(comment.get("author_association") or "")
                if (issue.get("number") != 302 or actor != "Wealthtechinnovations"
                        or author != actor or association not in {"OWNER", "MEMBER", "COLLABORATOR"}):
                    raise ValueError("GR302_REAPPROVAL_OWNER_REQUIRED")
                baseline = state["preparation_reconciliation_history"][-1]["observed_new_head"]
                observed = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/branches/main")
                if (observed.get("commit") or {}).get("sha") != baseline:
                    raise ValueError("GR302_REAPPROVAL_HEAD_MOVED")
                try:
                    api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/branches/lab%2Fchainflow-live-poc")
                except RuntimeError as error:
                    if "failed: 404 " not in str(error):
                        raise
                else:
                    raise ValueError("GR302_REAPPROVAL_LAB_ALREADY_EXISTS")
            if state.get("hold_review_pending"):
                field = payload["field"]
                if field in {"lab_authority", "plan_approved"}:
                    actor = str((event.get("sender") or {}).get("login") or "")
                    author = str(((comment.get("user") or {}).get("login") or ""))
                    association = str(comment.get("author_association") or "")
                    if (actor != "Wealthtechinnovations" or author != actor
                            or association not in {"OWNER", "MEMBER", "COLLABORATOR"}):
                        raise ValueError("HOLD_REVIEW_REANSWER_OWNER_REQUIRED")
                if field == "target_observation":
                    declared = payload["value"]
                    if not isinstance(declared, dict):
                        raise ValueError("HOLD_REVIEW_BASELINE_OBJECT_REQUIRED")
                    target = str((state.get("answers") or {}).get("target_repository") or "")
                    if target != CONTROL_PLANE_REPOSITORY:
                        raise ValueError("HOLD_REVIEW_TARGET_NOT_CANONICAL_SOURCE")
                    observed = api("GET", f"/repos/{target}")
                    branch_name = str(observed.get("default_branch") or "")
                    ref = api("GET", f"/repos/{target}/branches/{branch_name}")
                    actual = ((ref.get("commit") or {}).get("sha"))
                    if (declared.get("exists") is not True
                            or declared.get("default_branch") != branch_name
                            or declared.get("head_sha") != actual
                            or observed.get("full_name") != target):
                        raise ValueError("HOLD_REVIEW_BASELINE_LIVE_MISMATCH")
            state = apply_answer(state, payload["field"], payload["value"])
        elif kind == "evidence":
            if set(payload) != {"action_id", "result", "evidence"}:
                raise ValueError("evidence payload must contain exactly action_id, result and evidence")
            if not isinstance(payload["evidence"], dict):
                raise ValueError("evidence must be an object")
            if state.get("gr302_reconciliation_pending") and payload["action_id"] == "PREP-002R":
                if issue.get("number") != 302 or payload["result"] != "PASS":
                    raise ValueError("GR302_REBASELINE_READ_PASS_REQUIRED")
                expected = next(p["required_evidence"] for p in state["execution_plan"]
                                if p["id"] == "PREP-002R")
                if payload["evidence"] != expected:
                    raise ValueError("GR302_REBASELINE_EVIDENCE_MISMATCH")
                live = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/branches/main")
                if (live.get("commit") or {}).get("sha") != expected["canonical_head_sha"]:
                    raise ValueError("GR302_REBASELINE_HEAD_MOVED")
                try:
                    api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/branches/lab%2Fchainflow-live-poc")
                except RuntimeError as error:
                    if "failed: 404 " not in str(error):
                        raise
                else:
                    raise ValueError("GR302_REBASELINE_BRANCH_EXISTS")
            if state.get("plan_reconciliation_pending"):
                if state.get("request_id") != "GR-000284":
                    raise ValueError("LAB_PLAN_RECONCILE_GR_MISMATCH")
                if payload["result"] != "PASS":
                    raise ValueError("LAB_PLAN_RECONCILE_ONLY_VERIFIED_PASS")
                plan = state.get("execution_plan") or []
                entry = next((p for p in plan if p.get("id") == payload["action_id"]), None)
                if not entry or entry.get("status") != "PENDING":
                    raise ValueError("LAB_PLAN_RECONCILE_ACTION_NOT_PENDING")
                evidence = payload["evidence"]
                expected = entry.get("required_evidence") or {}
                if set(evidence) != set(expected) or any(evidence[k] != v for k, v in expected.items()):
                    raise ValueError("LAB_PLAN_RECONCILE_EVIDENCE_MISMATCH")
                live = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/branches/main")
                live_sha = (live.get("commit") or {}).get("sha")
                if live_sha != state["plan_reconciliation_history"][-1]["main_head_verified"]:
                    raise ValueError("LAB_PLAN_RECONCILE_HEAD_MOVED_REPLAN_REQUIRED")
                if payload["action_id"] != "PREP-001":
                    branch = api(
                        "GET",
                        f"/repos/{CONTROL_PLANE_REPOSITORY}/branches/lab%2Fcodeagent-gscc-f1-q12-renewal-284",
                    )
                    pr = api("GET", f"/repos/{CONTROL_PLANE_REPOSITORY}/pulls/316")
                    previous = state["plan_reconciliation_history"][-1]
                    if ((branch.get("commit") or {}).get("sha") != previous["historical_branch_head"]
                            or pr.get("number") != 316 or not pr.get("merged_at")
                            or pr.get("merge_commit_sha") != previous["merged_pr_commit"]
                            or (pr.get("base") or {}).get("ref") != "main"
                            or (pr.get("head") or {}).get("ref") != previous["historical_branch"]):
                        raise ValueError("LAB_PLAN_RECONCILE_PROVENANCE_DRIFT")
            state = apply_evidence(state, payload["action_id"], payload["result"], payload["evidence"])
        elif kind == "execute":
            pass
        elif kind == "upgrade_local_entry":
            if set(payload) != {"target_repository", "expected_head"}:
                raise ValueError("upgrade payload must contain target_repository and expected_head")
        elif kind == "local_command":
            expected = {"target_repository", "issue_number", "expected_head", "command"}
            if set(payload) != expected:
                raise ValueError("local command payload must contain target_repository, issue_number, expected_head and command")
        elif kind == "local_start":
            expected = {"target_repository", "expected_head", "objective"}
            if set(payload) != expected:
                raise ValueError("local start payload must contain target_repository, expected_head and objective")
        else:
            raise ValueError("unsupported governed command")
    except Exception as exc:
        api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{issue['number']}/comments", {
            "body": f"### Governed Control Plane — réponse refusée\n\n`{type(exc).__name__}: {exc}`\n\nAucun état gouverné n'a été avancé."
        })
        return

    if kind not in {"execute", "upgrade_local_entry", "local_command", "local_start"}:
        persist_state(issue["number"], issue.get("body"), state)
        api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{issue['number']}/comments", {"body": render_response(state)})
    if kind == "upgrade_local_entry":
        api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{issue['number']}/comments", {"body": "### Governed local-entry upgrade requested\n\nThe control plane will apply the current governed local-entry version under the supplied exact-HEAD guard."})
    if kind == "local_command":
        api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{issue['number']}/comments", {"body": "### Governed machine local command requested\n\nThe control plane will dispatch the command to the target repository under the supplied exact-HEAD guard."})
    if kind == "local_start":
        api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{issue['number']}/comments", {"body": "### Governed machine local entry start requested\n\nThe control plane will start a new repository-local governed entry under the supplied exact-HEAD guard."})
    emit_executor_outputs(
        state,
        issue["number"],
        payload if kind == "upgrade_local_entry" else None,
        payload if kind == "local_command" else None,
        payload if kind == "local_start" else None,
    )


def handle_repository_dispatch(event: dict) -> None:
    payload = event.get("client_payload") or {}
    objective = payload.get("objective")
    if not isinstance(objective, str) or not objective.strip():
        raise SystemExit("CONTROL_PLANE_DISPATCH_FAILED: client_payload.objective is required")
    agent = payload.get("agent")
    provider = payload.get("provider")
    requested_title = payload.get("title")
    suffix = requested_title.strip() if isinstance(requested_title, str) and requested_title.strip() else objective.strip().splitlines()[0][:80]
    body_lines = [
        "### Initial objective",
        "",
        objective.strip(),
    ]
    if agent:
        body_lines.extend(["", "### Agent identity", "", str(agent)])
    if provider:
        body_lines.extend(["", "### Provider", "", str(provider)])
    created = api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues", {
        "title": f"[Governed Request] {suffix}",
        "body": "\n".join(body_lines) + "\n",
    })
    print(json.dumps({
        "status": "GOVERNED_REQUEST_ISSUE_CREATED",
        "issue_number": created.get("number"),
        "issue_url": created.get("html_url"),
    }, ensure_ascii=False))


def main() -> None:
    if os.environ.get("GITHUB_REPOSITORY") != CONTROL_PLANE_REPOSITORY:
        print("CONTROL_PLANE_SKIPPED: source repository only")
        return
    event_path = Path(os.environ["GITHUB_EVENT_PATH"])
    event = json.loads(event_path.read_text(encoding="utf-8"))
    event_name = os.environ.get("GITHUB_EVENT_NAME")

    if event_name == "repository_dispatch" and event.get("action") == "governed_request_start":
        handle_repository_dispatch(event)
        return
    if event_name == "issues" and event.get("action") == "opened":
        handle_opened(event)
        return
    if event_name == "issue_comment" and event.get("action") == "created":
        sender = (event.get("sender") or {}).get("login")
        if sender == "github-actions[bot]":
            return
        handle_comment(event)
        return
    print(f"CONTROL_PLANE_SKIPPED: unsupported event {event_name}/{event.get('action')}")


if __name__ == "__main__":
    main()
