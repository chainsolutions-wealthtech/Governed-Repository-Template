#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

SCHEMA = "first-touch-exhaustive-capture/v1"

SENSITIVE_KEY_RE = re.compile(
    r"(?:^|_)(?:token|secret|password|passwd|cookie|authorization|auth_header|private_key|"
    r"client_secret|access_key|session_cookie)(?:$|_)",
    re.IGNORECASE,
)

SAFE_ENV_KEYS = {
    "CI",
    "GITHUB_REPOSITORY",
    "GITHUB_REPOSITORY_ID",
    "GITHUB_REPOSITORY_OWNER",
    "GITHUB_REPOSITORY_OWNER_ID",
    "GITHUB_ACTOR",
    "GITHUB_ACTOR_ID",
    "GITHUB_TRIGGERING_ACTOR",
    "GITHUB_EVENT_NAME",
    "GITHUB_REF",
    "GITHUB_REF_NAME",
    "GITHUB_REF_TYPE",
    "GITHUB_SHA",
    "GITHUB_HEAD_REF",
    "GITHUB_BASE_REF",
    "GITHUB_WORKFLOW",
    "GITHUB_WORKFLOW_REF",
    "GITHUB_WORKFLOW_SHA",
    "GITHUB_RUN_ID",
    "GITHUB_RUN_NUMBER",
    "GITHUB_RUN_ATTEMPT",
    "GITHUB_JOB",
    "GITHUB_ACTION",
    "GITHUB_ACTION_REPOSITORY",
    "GITHUB_ACTION_REF",
    "GITHUB_SERVER_URL",
    "GITHUB_API_URL",
    "GITHUB_GRAPHQL_URL",
    "GITHUB_WORKSPACE",
    "GITHUB_EVENT_PATH",
    "RUNNER_OS",
    "RUNNER_ARCH",
    "RUNNER_NAME",
    "RUNNER_ENVIRONMENT",
    "RUNNER_TEMP",
    "RUNNER_TOOL_CACHE",
}

FREEFORM_CONTENT_KEYS = {
    "body",
    "text",
    "content",
    "message",
    "description",
    "raw_prompt",
    "prompt",
    "response",
    "transcript",
    "tool_output",
    "tool_result",
}



FIRST_TOUCH_PREFIX = "/gscc-first-touch "
FIRST_TOUCH_SAFE_MAX = 512
OPAQUE_REF_RE = re.compile(r"^[A-Za-z0-9._:-]{8,256}$")
UNAVAILABLE_MARKERS = {"UNAVAILABLE","UNKNOWN","NOT_EXPOSED"}

def _safe_first_touch_ingress(event: dict[str, Any], observed_at: str) -> dict[str, Any] | None:
    if not isinstance(event, dict):
        return None
    comment = event.get("comment") if isinstance(event.get("comment"), dict) else {}
    body = comment.get("body")
    if not isinstance(body, str) or not body.startswith(FIRST_TOUCH_PREFIX):
        return None
    raw = body[len(FIRST_TOUCH_PREFIX):].strip()
    if not raw or len(raw) > FIRST_TOUCH_SAFE_MAX:
        return {
            "schema":"gscc-first-touch-safe-ingress/v1",
            "status":"INVALID",
            "reason":"PAYLOAD_SIZE_OR_EMPTY",
            "comment_id":comment.get("id"),
            "observed_at":observed_at,
        }
    try:
        payload=json.loads(raw)
    except Exception:
        return {
            "schema":"gscc-first-touch-safe-ingress/v1",
            "status":"INVALID",
            "reason":"JSON_INVALID",
            "comment_id":comment.get("id"),
            "observed_at":observed_at,
        }
    if not isinstance(payload, dict):
        return {
            "schema":"gscc-first-touch-safe-ingress/v1",
            "status":"INVALID",
            "reason":"JSON_OBJECT_REQUIRED",
            "comment_id":comment.get("id"),
            "observed_at":observed_at,
        }

    connection = payload.get("connection") if isinstance(payload.get("connection"), dict) else {}
    client = payload.get("client") if isinstance(payload.get("client"), dict) else {}
    session = payload.get("session") if isinstance(payload.get("session"), dict) else {}

    connection_ref = connection.get("connection_ref")
    client_instance_id = client.get("client_instance_id")
    conversation_ref = session.get("conversation_ref")
    provider_conversation_ref = session.get("provider_conversation_ref")

    def safe_ref(value: Any) -> str | None:
        if not isinstance(value, str) or value.upper() in UNAVAILABLE_MARKERS:
            return None
        return value if OPAQUE_REF_RE.fullmatch(value) else None

    result = {
        "schema":"gscc-first-touch-safe-ingress/v1",
        "status":"VALID",
        "ingress_type":"FIRST_TOUCH",
        "comment_id":comment.get("id"),
        "connection_ref":safe_ref(connection_ref),
        "client_instance_id":safe_ref(client_instance_id),
        "conversation_ref":safe_ref(conversation_ref),
        "provider_conversation_ref":safe_ref(provider_conversation_ref),
        "conversation_ref_status":(
            "UNAVAILABLE" if isinstance(conversation_ref,str) and conversation_ref.upper() in UNAVAILABLE_MARKERS
            else "PRESENT" if safe_ref(conversation_ref) else "UNKNOWN"
        ),
        "provider_conversation_ref_status":(
            "UNAVAILABLE" if isinstance(provider_conversation_ref,str) and provider_conversation_ref.upper() in UNAVAILABLE_MARKERS
            else "PRESENT" if safe_ref(provider_conversation_ref) else "UNKNOWN"
        ),
        "source":"GITHUB_ISSUE_COMMENT_STRUCTURED_PREFIX",
        "source_method":"ISSUE_COMMENT",
        "observed_at":observed_at,
        "freeform_body_persisted":False,
    }
    if not result["connection_ref"] and not result["client_instance_id"] and not result["conversation_ref"] and not result["provider_conversation_ref"]:
        result["status"]="INVALID"
        result["reason"]="NO_SAFE_IDENTITY_ANCHOR"
    return result

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _is_sensitive_key(key: str) -> bool:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", key).strip("_")
    return bool(SENSITIVE_KEY_RE.search(normalized))


def _redacted_metadata(value: Any, reason: str) -> dict[str, Any]:
    rendered = "" if value is None else (
        value if isinstance(value, str)
        else json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    )
    return {
        "_capture_status": "REDACTED_VALUE",
        "_reason": reason,
        "_field_present": value not in (None, ""),
        "_value_length": len(rendered),
        "_value_sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest() if rendered else None,
    }


def sanitize(value: Any, *, key: str | None = None) -> Any:
    if key is not None and _is_sensitive_key(key):
        return _redacted_metadata(value, "SENSITIVE_KEY")
    if key is not None and key.lower() in FREEFORM_CONTENT_KEYS:
        return _redacted_metadata(value, "FREEFORM_CONTENT")
    if isinstance(value, dict):
        return {str(k): sanitize(v, key=str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    if isinstance(value, tuple):
        return [sanitize(v) for v in value]
    return value


def _read_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    target = Path(path)
    if not target.exists():
        return {}
    value = json.loads(target.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {"_raw_event": value}


def _event_subject(event: dict[str, Any], env: dict[str, str]) -> dict[str, Any]:
    issue = event.get("issue") or {}
    pr = event.get("pull_request") or {}
    ref = event.get("ref") or env.get("GITHUB_HEAD_REF") or env.get("GITHUB_REF_NAME")
    result = {
        "event_name": env.get("GITHUB_EVENT_NAME"),
        "issue_number": issue.get("number") or (
            event.get("number") if env.get("GITHUB_EVENT_NAME") in {"issues", "issue_comment"} else None
        ),
        "pull_request_number": pr.get("number") or (
            event.get("number") if env.get("GITHUB_EVENT_NAME", "").startswith("pull_request") else None
        ),
        "event_ref": ref,
        "event_after": event.get("after"),
        "event_before": event.get("before"),
    }
    return {k: v for k, v in result.items() if v not in (None, "", [], {})}


def _environment_snapshot(env: dict[str, str]) -> dict[str, Any]:
    return {
        key: sanitize(env[key], key=key)
        for key in sorted(SAFE_ENV_KEYS)
        if key in env
    }


def _http_json(url: str, token: str | None, timeout: int = 15) -> tuple[int, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "governed-first-touch-exhaustive-collector/1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            return int(response.status), json.loads(body.decode("utf-8")) if body else None
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            parsed = json.loads(body.decode("utf-8")) if body else None
        except Exception:
            parsed = {"message": body.decode("utf-8", errors="replace")[:1000]}
        return int(exc.code), parsed
    except Exception as exc:
        return 0, {"error_type": type(exc).__name__, "message": str(exc)[:1000]}


def _api_attempt(name: str, url: str, *, token: str | None, request_fn=None) -> dict[str, Any]:
    requester = request_fn or _http_json
    status, payload = requester(url, token)
    return {
        "name": name,
        "url": url,
        "http_status": status,
        "response": sanitize(payload),
    }


def build_capture(
    event: dict[str, Any],
    env: dict[str, str],
    *,
    token: str | None = None,
    request_fn: Callable[[str, str | None], tuple[int, Any]] | None = None,
    observed_at: str | None = None,
) -> dict[str, Any]:
    observed_at = observed_at or utc_now()
    repo = str(((event.get("repository") or {}).get("full_name")) or env.get("GITHUB_REPOSITORY") or "")
    actor = str(((event.get("sender") or {}).get("login")) or env.get("GITHUB_ACTOR") or "")
    api_url = env.get("GITHUB_API_URL") or "https://api.github.com"
    subject = _event_subject(event, env)

    attempts: list[dict[str, Any]] = []
    if repo.count("/") == 1:
        owner, name = repo.split("/", 1)
        repo_path = f"/repos/{quote(owner, safe='')}/{quote(name, safe='')}"
        attempts.append(_api_attempt("repository", api_url + repo_path, token=token, request_fn=request_fn))
        if actor:
            attempts.append(_api_attempt(
                "actor_repository_permission",
                api_url + repo_path + f"/collaborators/{quote(actor, safe='')}/permission",
                token=token,
                request_fn=request_fn,
            ))
        if subject.get("issue_number") is not None:
            attempts.append(_api_attempt(
                "issue",
                api_url + repo_path + f"/issues/{int(subject['issue_number'])}",
                token=token,
                request_fn=request_fn,
            ))
        if subject.get("pull_request_number") is not None:
            attempts.append(_api_attempt(
                "pull_request",
                api_url + repo_path + f"/pulls/{int(subject['pull_request_number'])}",
                token=token,
                request_fn=request_fn,
            ))
        run_id = env.get("GITHUB_RUN_ID")
        if run_id:
            attempts.append(_api_attempt(
                "workflow_run",
                api_url + repo_path + f"/actions/runs/{quote(str(run_id), safe='')}",
                token=token,
                request_fn=request_fn,
            ))
            attempts.append(_api_attempt(
                "workflow_run_jobs",
                api_url + repo_path + f"/actions/runs/{quote(str(run_id), safe='')}/jobs",
                token=token,
                request_fn=request_fn,
            ))
        attempts.append(_api_attempt(
            "repository_installation",
            api_url + repo_path + "/installation",
            token=token,
            request_fn=request_fn,
        ))
        attempts.append(_api_attempt(
            "repository_actions_permissions",
            api_url + repo_path + "/actions/permissions",
            token=token,
            request_fn=request_fn,
        ))

    safe_ingress = _safe_first_touch_ingress(event, observed_at)

    material = {
        "schema": SCHEMA,
        "observed_at": observed_at,
        "repository": repo or None,
        "actor": actor or None,
        "subject": sanitize(subject),
        "safe_ingress": safe_ingress,
        "github_event": sanitize(event),
        "environment": _environment_snapshot(env),
        "api_attempts": attempts,
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return {
        **material,
        "capture_id": "FTC-" + digest[:24],
        "capture_digest": digest,
        "mutation_authority_granted": False,
        "interpretation_applied": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Exhaustive first-touch repository-side capture")
    sub = parser.add_subparsers(dest="command", required=True)
    github = sub.add_parser("github-event")
    github.add_argument("--output", required=True)
    args = parser.parse_args()

    event = _read_json(os.environ.get("GITHUB_EVENT_PATH"))
    capture = build_capture(event, dict(os.environ), token=os.environ.get("GITHUB_TOKEN"))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(capture, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "FIRST_TOUCH_CAPTURE_COMPLETE",
        "capture_id": capture["capture_id"],
        "output": str(output),
        "api_attempts": len(capture["api_attempts"]),
    }, indent=2))


if __name__ == "__main__":
    main()
