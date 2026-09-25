#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

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
    if stripped.startswith("/governed-answer"):
        raw = stripped[len("/governed-answer"):].strip()
        return "answer", json.loads(raw)
    if stripped.startswith("/governed-evidence"):
        raw = stripped[len("/governed-evidence"):].strip()
        return "evidence", json.loads(raw)
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


def emit_executor_outputs(state: dict, issue_number: int) -> None:
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
        f"issue_number={issue_number}",
    ]
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

    state = extract_state(issue.get("body"))
    kind, payload = command
    try:
        if kind == "answer":
            if set(payload) != {"field", "value"}:
                raise ValueError("answer payload must contain exactly field and value")
            state = apply_answer(state, payload["field"], payload["value"])
        elif kind == "evidence":
            if set(payload) != {"action_id", "result", "evidence"}:
                raise ValueError("evidence payload must contain exactly action_id, result and evidence")
            if not isinstance(payload["evidence"], dict):
                raise ValueError("evidence must be an object")
            state = apply_evidence(state, payload["action_id"], payload["result"], payload["evidence"])
        elif kind == "execute":
            pass
        else:
            raise ValueError("unsupported governed command")
    except Exception as exc:
        api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{issue['number']}/comments", {
            "body": f"### Governed Control Plane — réponse refusée\n\n`{type(exc).__name__}: {exc}`\n\nAucun état gouverné n'a été avancé."
        })
        return

    if kind != "execute":
        persist_state(issue["number"], issue.get("body"), state)
        api("POST", f"/repos/{CONTROL_PLANE_REPOSITORY}/issues/{issue['number']}/comments", {"body": render_response(state)})
    emit_executor_outputs(state, issue["number"])


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
