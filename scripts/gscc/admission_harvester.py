#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

if __package__:
    from .admission import QUALIFICATION_REQUIREMENTS, resolve_admission_session_binding
    from .protocol import assert_secretless
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from gscc.admission import QUALIFICATION_REQUIREMENTS, resolve_admission_session_binding
    from gscc.protocol import assert_secretless

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSIONS = ROOT / ".governance" / "control-plane-state" / "gacr-sessions.json"
DEFAULT_CLAIMS = ROOT / ".governance" / "control-plane-state" / "gacr-claims.json"
DEFAULT_TASKS = ROOT / ".governance" / "control-plane-state" / "tasks.json"

REQUIRED_GOVERNANCE_DOCUMENTS = (
    "00_START_HERE.md",
    "GOVERNANCE.md",
    "docs/control-plane/GSCC_ADMISSION_ACCESS_GATE.md",
    "docs/control-plane/GACR_PROGRAM.md",
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def normalize_unavailable(reason: str, source: str, observed_at: datetime) -> dict[str, Any]:
    provenance = (
        "PROVIDER_PRIVATE_UNAVAILABLE"
        if reason in {"NOT_EXPOSED_BY_PROVIDER", "PROVIDER_NOT_EXPOSED"}
        else "OBSERVABLE_BY_PLATFORM"
    )
    return {
        "status": "UNAVAILABLE",
        "reason": reason,
        "provenance": provenance,
        "source": source,
        "observed_at": _iso(observed_at),
    }


def github_get_json(url: str, *, token: str | None = None) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "gscc-admission-harvester",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("GitHub observation must return an object")
    return payload


def observe_repository(
    repository: str,
    requested_branch: str | None,
    *,
    request_fn: Callable[[str], dict[str, Any]],
    observed_at: datetime | None = None,
) -> dict[str, Any]:
    observed_at = (observed_at or _now()).astimezone(timezone.utc)
    encoded_repo = urllib.parse.quote(repository, safe="/")
    repo_url = f"https://api.github.com/repos/{encoded_repo}"
    repo = request_fn(repo_url)
    actual = str(repo.get("full_name") or repository)
    if actual != repository:
        return {
            "status": "DENIED",
            "reason_code": "REPOSITORY_IDENTITY_MISMATCH",
            "repository": actual,
            "expected_repository": repository,
        }

    branch = requested_branch or str(repo.get("default_branch") or "")
    if not branch:
        return {
            "status": "UNAVAILABLE",
            "reason_code": "DEFAULT_BRANCH_UNAVAILABLE",
            "repository": repository,
        }
    branch_url = f"{repo_url}/branches/{urllib.parse.quote(branch, safe='')}"
    branch_payload = request_fn(branch_url)
    head = ((branch_payload.get("commit") or {}).get("sha"))

    result = {
        "status": "OBSERVED" if head else "UNAVAILABLE",
        "repository": repository,
        "repository_id": str(repo.get("id")) if repo.get("id") is not None else None,
        "organization": ((repo.get("owner") or {}).get("login")),
        "visibility": repo.get("visibility"),
        "default_branch": repo.get("default_branch"),
        "requested_branch": branch,
        "observed_head": head,
        "permissions": {
            key: bool(value)
            for key, value in (repo.get("permissions") or {}).items()
            if key in {"pull", "triage", "push", "maintain", "admin"}
        },
        "observed_at": _iso(observed_at),
        "provenance": {
            "source_method": "GET",
            "provenance": "OBSERVABLE_BY_PLATFORM",
            "source": "GITHUB_API",
            "repository_url": repo_url,
            "branch_url": branch_url,
        },
        "evidence_ref": (
            f"github-api:repository:{repo.get('id')}:branch:{branch}:head:{head}"
            if head else f"github-api:repository:{repo.get('id')}:branch:{branch}"
        ),
    }
    assert_secretless(result)
    return result


def _connection_field(session: dict[str, Any], name: str) -> Any:
    envelope = session.get("connection_envelope")
    if not isinstance(envelope, dict):
        return None
    fields = envelope.get("fields")
    if not isinstance(fields, dict):
        return None
    entry = fields.get(name)
    if isinstance(entry, dict):
        value = entry.get("value")
        return None if value in (None, "", "UNAVAILABLE") else value
    return None


def resolve_gacr_session(
    sessions: dict[str, Any],
    *,
    admission_receipt: dict[str, Any] | None = None,
    connection_ref: str | None = None,
    repository: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or _now()).astimezone(timezone.utc)
    receipt = copy.deepcopy(admission_receipt) if isinstance(admission_receipt, dict) else {
        "schema": "gscc-admission-receipt/v1",
        "status": "PREAUTHORIZED",
        "admission_id": "GSCC-ADM-HARVEST-LOOKUP",
        "connection_ref": connection_ref,
        "repository": repository,
        "requested_branch": None,
        "evaluated_at": _iso(now),
    }
    repository = str(repository or receipt.get("repository") or "")
    if not repository:
        return normalize_unavailable("ADMISSION_REPOSITORY_REQUIRED", "GACR_CANONICAL_SESSION_STORE", now)

    binding = resolve_admission_session_binding(receipt, sessions, now=now)
    if binding.get("status") != "BOUND":
        reason = str(binding.get("reason_code") or "NO_ACTIVE_CANONICAL_GACR_SESSION")
        if reason == "ADMISSION_SESSION_BIND_AMBIGUOUS":
            return {
                "status": "AMBIGUOUS",
                "reason": reason,
                "candidate_session_ids": binding.get("candidate_session_ids") or [],
                "provenance": "CORRELATED",
                "source": "GACR_CANONICAL_SESSION_BINDING",
                "observed_at": _iso(now),
            }
        return normalize_unavailable(reason, "GACR_CANONICAL_SESSION_BINDING", now)

    session_id = binding.get("session_id")
    session = next(
        (
            item for item in (sessions.get("sessions") or [])
            if isinstance(item, dict) and item.get("session_id") == session_id
        ),
        None,
    )
    if not isinstance(session, dict):
        return normalize_unavailable("BOUND_GACR_SESSION_NOT_FOUND", "GACR_CANONICAL_SESSION_STORE", now)

    relay = session.get("relay") if isinstance(session.get("relay"), dict) else {}
    expiry = _parse_datetime(relay.get("lease_expires_at"))
    if expiry is None or expiry <= now:
        return normalize_unavailable("GACR_SESSION_LEASE_EXPIRED", "GACR_CANONICAL_SESSION_STORE", now)

    result = {
        "status": "BOUND",
        "session_id": session.get("session_id"),
        "connection_ref": binding.get("canonical_connection_ref") or session.get("connection_ref"),
        "admission_connection_ref": binding.get("admission_connection_ref") or receipt.get("connection_ref"),
        "binding_level": binding.get("correlation"),
        "binding_evidence_ref": binding.get("binding_evidence_ref"),
        "repository": session.get("repository"),
        "last_observed_head": session.get("last_observed_head_sha"),
        "lease_expires_at": relay.get("lease_expires_at"),
        "task_id": relay.get("task_id") or _connection_field(session, "task_id"),
        "claim_id": _connection_field(session, "claim_id"),
        "capabilities": copy.deepcopy(session.get("capabilities") or _connection_field(session, "capabilities") or []),
        "connection_envelope": copy.deepcopy(session.get("connection_envelope")),
        "provenance": {
            "source_method": "CORRELATED",
            "provenance": "CORRELATED",
            "source": "GACR_CANONICAL_SESSION_BINDING",
            "store_revision": sessions.get("revision"),
        },
        "observed_at": _iso(now),
    }
    assert_secretless(result)
    return result


def _contains_identifier(value: Any, identifier: str) -> bool:
    if isinstance(value, dict):
        if identifier in {str(v) for v in value.values() if isinstance(v, (str, int))}:
            return True
        return any(_contains_identifier(child, identifier) for child in value.values())
    if isinstance(value, list):
        return any(_contains_identifier(child, identifier) for child in value)
    return False


def _reconcile_reference(kind: str, identifier: str | None, store: dict[str, Any], now: datetime) -> dict[str, Any]:
    if not identifier:
        return {
            "status": "NOT_REQUIRED",
            f"{kind}_id": None,
            "provenance": "CORRELATED",
            "source": f"CANONICAL_{kind.upper()}_STORE",
            "observed_at": _iso(now),
        }
    if _contains_identifier(store, identifier):
        return {
            "status": "RECONCILED",
            f"{kind}_id": identifier,
            "provenance": "CORRELATED",
            "source": f"CANONICAL_{kind.upper()}_STORE",
            "observed_at": _iso(now),
        }
    return {
        "status": "UNAVAILABLE",
        "reason": f"CANONICAL_{kind.upper()}_NOT_FOUND",
        f"{kind}_id": identifier,
        "provenance": "CORRELATED",
        "source": f"CANONICAL_{kind.upper()}_STORE",
        "observed_at": _iso(now),
    }


def observe_governance(
    documents: dict[str, str],
    *,
    repository_head: str | None,
    observed_at: datetime,
) -> dict[str, Any]:
    missing = [path for path in REQUIRED_GOVERNANCE_DOCUMENTS if path not in documents]
    evidence = [
        {
            "path": path,
            "digest": hashlib.sha256(documents[path].encode("utf-8")).hexdigest(),
        }
        for path in REQUIRED_GOVERNANCE_DOCUMENTS
        if path in documents
    ]
    return {
        "status": "COMPLETED" if not missing else "PENDING",
        "documents": evidence,
        "missing_documents": missing,
        "repository_head": repository_head,
        "reader": "GSCC_ADMISSION_HARVESTER",
        "provenance": {
            "source_method": "GET",
            "provenance": "OBSERVABLE_BY_PLATFORM",
            "source": "CHECKED_OUT_CANONICAL_REPOSITORY",
        },
        "observed_at": _iso(observed_at),
    }


def _verified_optional(section: dict[str, Any] | None, *, unavailable_reason: str, source: str, now: datetime) -> dict[str, Any]:
    if isinstance(section, dict) and section.get("status") == "VERIFIED" and section.get("evidence_ref"):
        result = copy.deepcopy(section)
        result.setdefault("provenance", "OBSERVABLE_BY_PLATFORM")
        result.setdefault("source", source)
        result.setdefault("observed_at", _iso(now))
        return result
    return normalize_unavailable(unavailable_reason, source, now)


def harvest_qualification_evidence(
    admission_receipt: dict[str, Any],
    *,
    github_request_fn: Callable[[str], dict[str, Any]],
    sessions: dict[str, Any],
    claims: dict[str, Any],
    tasks: dict[str, Any],
    governance_documents: dict[str, str],
    target_repository: str | None = None,
    requested_branch: str | None = None,
    capability_evidence: dict[str, Any] | None = None,
    control_evidence: dict[str, Any] | None = None,
    gse_state: dict[str, Any] | None = None,
    access_policy: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or _now()).astimezone(timezone.utc)
    if not isinstance(admission_receipt, dict) or admission_receipt.get("status") != "PREAUTHORIZED":
        raise ValueError("PREAUTHORIZED_ADMISSION_REQUIRED")

    repository = target_repository or admission_receipt.get("repository")
    if not isinstance(repository, str) or repository.count("/") != 1:
        raise ValueError("TARGET_REPOSITORY_REQUIRED")

    context = admission_receipt.get("admission_context") or {}
    target = context.get("target") if isinstance(context.get("target"), dict) else {}
    branch = requested_branch or target.get("requested_branch")

    repository_baseline = observe_repository(
        repository,
        branch,
        request_fn=github_request_fn,
        observed_at=now,
    )
    session = resolve_gacr_session(
        sessions,
        admission_receipt=admission_receipt,
        connection_ref=str(admission_receipt.get("connection_ref") or ""),
        repository=repository,
        now=now,
    )

    if session.get("status") == "BOUND":
        session_head = session.get("last_observed_head")
        current_head = repository_baseline.get("observed_head")
        if session_head and current_head and session_head != current_head:
            session = {
                **session,
                "status": "STALE_HEAD",
                "reason": "GACR_SESSION_HEAD_DIFFERS_FROM_GITHUB_OBSERVATION",
                "current_observed_head": current_head,
            }

    governance_read = observe_governance(
        governance_documents,
        repository_head=repository_baseline.get("observed_head"),
        observed_at=now,
    )

    task = _reconcile_reference("task", session.get("task_id") if session.get("status") in {"BOUND", "STALE_HEAD"} else None, tasks, now)
    claim = _reconcile_reference("claim", session.get("claim_id") if session.get("status") in {"BOUND", "STALE_HEAD"} else None, claims, now)

    declared_capabilities = session.get("capabilities") if session.get("status") in {"BOUND", "STALE_HEAD"} else []
    if isinstance(capability_evidence, dict) and capability_evidence.get("status") == "VERIFIED" and capability_evidence.get("evidence_ref"):
        capabilities = copy.deepcopy(capability_evidence)
        capabilities.setdefault("declared", copy.deepcopy(declared_capabilities or []))
        capabilities.setdefault("provenance", "OBSERVABLE_BY_PLATFORM")
        capabilities.setdefault("source", "GSCC_CAPABILITY_CHALLENGE")
        capabilities.setdefault("observed_at", _iso(now))
    else:
        capabilities = {
            "status": "DECLARED_BUT_UNVERIFIED" if declared_capabilities else "UNAVAILABLE",
            "declared": copy.deepcopy(declared_capabilities or []),
            "reason": "GSCC_CAPABILITY_CHALLENGE_REQUIRED",
            "provenance": "CORRELATED",
            "source": "GACR_CONNECTION_ENVELOPE",
            "observed_at": _iso(now),
        }

    control_channel = _verified_optional(
        control_evidence,
        unavailable_reason="CANONICAL_CONTROL_CHALLENGE_EVIDENCE_REQUIRED",
        source="GSCC_CONTROL_CHANNEL",
        now=now,
    )

    if (
        isinstance(gse_state, dict)
        and gse_state.get("schema") == "gscc-gse-admission-state/v1"
        and gse_state.get("presence") == "PRESENT"
        and gse_state.get("liveness") == "VERIFIED"
        and gse_state.get("control_reachability") == "REACHABLE"
        and gse_state.get("evidence_ref")
    ):
        gse_initial_state = copy.deepcopy(gse_state)
        gse_initial_state.setdefault("provenance", "GSE_DERIVED")
        gse_initial_state.setdefault("source", "GSE_SESSION_STATE_ENGINE")
        gse_initial_state.setdefault("observed_at", _iso(now))
    else:
        gse_initial_state = normalize_unavailable(
            "CANONICAL_GSE_ADMISSION_STATE_REQUIRED",
            "GSE_SESSION_STATE_ENGINE",
            now,
        )

    if isinstance(access_policy, dict) and access_policy.get("status") == "ALLOW" and access_policy.get("evidence_ref"):
        access_policy_result = copy.deepcopy(access_policy)
        access_policy_result.setdefault("provenance", "OBSERVABLE_BY_PLATFORM")
        access_policy_result.setdefault("source", "GOVERNANCE_ACCESS_POLICY")
        access_policy_result.setdefault("observed_at", _iso(now))
    else:
        access_policy_result = {
            "status": "PENDING",
            "reason": "CANONICAL_ACCESS_POLICY_EVIDENCE_REQUIRED",
            "allowed_authority_classes": [],
            "constraints": {},
            "provenance": "OBSERVABLE_BY_PLATFORM",
            "source": "GOVERNANCE_ACCESS_POLICY",
            "observed_at": _iso(now),
        }

    evidence = {
        "schema": "gscc-qualification-evidence/v1",
        "harvested_by": "GSCC_ADMISSION_HARVESTER",
        "admission_id": admission_receipt.get("admission_id"),
        "connection_ref": admission_receipt.get("connection_ref"),
        "repository": repository,
        "session": session,
        "governance_read": governance_read,
        "repository_baseline": repository_baseline,
        "task": task,
        "claim": claim,
        "capabilities": capabilities,
        "control_channel": control_channel,
        "gse_initial_state": gse_initial_state,
        "access_policy": access_policy_result,
        "observed_at": _iso(now),
        "provenance_matrix": {
            "repository_baseline": "GITHUB_API_GET",
            "session": "GACR_CANONICAL_SESSION_STORE",
            "governance_read": "CHECKED_OUT_CANONICAL_REPOSITORY",
            "task": "CANONICAL_TASK_STORE",
            "claim": "CANONICAL_CLAIM_STORE",
            "capabilities": "GACR_PLUS_GSCC_CHALLENGE_REQUIRED",
            "control_channel": "GSCC_CONTROL_CHALLENGE_REQUIRED",
            "gse_initial_state": "GSE_CANONICAL_STATE_REQUIRED",
            "access_policy": "GOVERNANCE_POLICY_REQUIRED",
        },
    }

    missing = [
        name
        for name, validator in QUALIFICATION_REQUIREMENTS.items()
        if not validator(evidence.get(name))
    ]
    evidence["missing_canonical_evidence"] = missing
    evidence["status"] = "QUALIFICATION_EVIDENCE_COMPLETE" if not missing else "QUALIFICATION_EVIDENCE_PARTIAL"
    material = copy.deepcopy(evidence)
    evidence["harvest_digest"] = _digest(material)
    assert_secretless(evidence)
    return evidence


def _load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _load_governance_documents(root: Path = ROOT) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in REQUIRED_GOVERNANCE_DOCUMENTS:
        target = root / path
        if target.exists():
            result[path] = target.read_text(encoding="utf-8")
    return result


def _write_output(value: dict[str, Any], output: str | None) -> None:
    rendered = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")


def _github_output(name: str, value: Any) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="GSCC canonical admission qualification evidence harvester")
    sub = parser.add_subparsers(dest="command", required=True)
    harvest = sub.add_parser("harvest")
    harvest.add_argument("--admission-receipt-json", required=True)
    harvest.add_argument("--repository")
    harvest.add_argument("--requested-branch")
    harvest.add_argument("--sessions", default=str(DEFAULT_SESSIONS))
    harvest.add_argument("--claims", default=str(DEFAULT_CLAIMS))
    harvest.add_argument("--tasks", default=str(DEFAULT_TASKS))
    harvest.add_argument("--output")
    args = parser.parse_args()

    if args.command != "harvest":
        raise SystemExit("UNSUPPORTED_COMMAND")

    receipt = json.loads(args.admission_receipt_json)
    if not isinstance(receipt, dict):
        raise SystemExit("ADMISSION_RECEIPT_OBJECT_REQUIRED")

    token = os.environ.get("GITHUB_TOKEN")
    result = harvest_qualification_evidence(
        receipt,
        target_repository=args.repository,
        requested_branch=args.requested_branch,
        github_request_fn=lambda url: github_get_json(url, token=token),
        sessions=_load_json(args.sessions),
        claims=_load_json(args.claims),
        tasks=_load_json(args.tasks),
        governance_documents=_load_governance_documents(),
    )
    _write_output(result, args.output)
    _github_output("status", result.get("status"))
    _github_output("harvest_digest", result.get("harvest_digest"))
    _github_output("missing_canonical_evidence", ",".join(result.get("missing_canonical_evidence") or []))


if __name__ == "__main__":
    main()
