#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from gscc_observable_arrival import emit_controlled_arrival
from provider_first_touch_evidence import build_field_evidence

SCHEMA = "gscc-provider-first-touch-envelope/v1"
CAPTURE_SCHEMA = "first-touch-exhaustive-capture/v1"

SENSITIVE_KEY_RE = re.compile(
    r"(?:^|_)(?:token|secret|password|passwd|cookie|authorization|auth_header|private_key|"
    r"client_secret|access_key|session_cookie)(?:$|_)",
    re.IGNORECASE,
)

UNAVAILABLE_MARKERS = {None, "", "UNAVAILABLE", "UNKNOWN", "NOT_EXPOSED", "NOT_ACCESSIBLE"}

SAFE_SECURITY_STATUS_KEYS = {
    "secret_accessed",
    "token_exposed",
    "oauth_secret_exposed",
    "private_key_exposed",
    "conversation_id_exposed",
    "session_id_exposed",
    "installation_id_exposed",
    "client_id_exposed",
    "ip_exposed",
    "sensitive_value_present",
    "redacted",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _is_sensitive_key(key: str) -> bool:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", key).strip("_").lower()
    if normalized in SAFE_SECURITY_STATUS_KEYS:
        return False
    return bool(SENSITIVE_KEY_RE.search(normalized))


def _assert_no_sensitive_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if _is_sensitive_key(str(key)):
                raise ValueError(f"sensitive field forbidden at {path}.{key}")
            _assert_no_sensitive_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_sensitive_keys(child, f"{path}[{index}]")


def _require_text(envelope: dict[str, Any], key: str) -> str:
    value = envelope.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} required")
    return value.strip()


def _stable_ref(envelope: dict[str, Any]) -> tuple[str | None, str | None]:
    identity = envelope.get("identity") if isinstance(envelope.get("identity"), dict) else {}
    for key in ("conversation_ref", "session_ref", "connection_ref"):
        value = identity.get(key)
        if isinstance(value, str) and value.strip() and value.strip().upper() not in UNAVAILABLE_MARKERS:
            return key, value.strip()
    return None, None


def validate_envelope(envelope: dict[str, Any]) -> None:
    if envelope.get("schema") != SCHEMA:
        raise ValueError(f"unsupported schema: {envelope.get('schema')!r}")
    _require_text(envelope, "provider")
    repository = _require_text(envelope, "repository")
    if repository.count("/") != 1:
        raise ValueError("repository must use owner/name")
    _require_text(envelope, "transport")
    _assert_no_sensitive_keys(envelope)


def build_capture(envelope: dict[str, Any], *, observed_at: str | None = None) -> dict[str, Any]:
    validate_envelope(envelope)
    observed_at = observed_at or str(envelope.get("observed_at") or utc_now())
    field_evidence = build_field_evidence(envelope, observed_at)
    material = {
        "schema": CAPTURE_SCHEMA,
        "observed_at": observed_at,
        "repository": envelope["repository"],
        "actor": envelope.get("actor"),
        "subject": {
            "event_name": "provider_first_touch",
            "event_ref": envelope.get("branch"),
        },
        "github_event": {},
        "environment": {},
        "api_attempts": [],
        "provider_context": envelope,
        "field_evidence": field_evidence,
        "field_evidence_contract": {
            "schema": "first-touch-field-evidence/v1",
            "expected_field_count": len(field_evidence),
            "silent_absence_allowed": False,
            "unavailable_value": "UNAVAILABLE",
            "required_provenance_keys": ["source", "confidence", "observed_at", "reason", "evidence_ref"],
        },
        "mutation_authority_granted": False,
        "interpretation_applied": False,
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return {
        **material,
        "capture_id": "FTC-" + digest[:24],
        "capture_digest": digest,
    }


def emit_if_identifiable(
    envelope: dict[str, Any],
    *,
    token: str | None = None,
    request_fn: Callable[..., tuple[int, bytes]] | None = None,
) -> dict[str, Any]:
    validate_envelope(envelope)
    ref_kind, stable_ref = _stable_ref(envelope)
    if not stable_ref:
        return {
            "status": "CAPTURE_ONLY_IDENTITY_UNRESOLVED",
            "identity_strength": "UNRESOLVED",
            "mutation_authority_granted": False,
        }

    provider = str(envelope["provider"])
    repository = str(envelope["repository"])
    actor = envelope.get("actor")
    model = envelope.get("model")
    connection_ref = f"provider-first-touch:{provider}:{ref_kind}:{stable_ref}"
    client_instance_id = f"{provider}:{ref_kind}:{stable_ref}"
    provider_ref_parts = [str(envelope.get("transport") or "UNAVAILABLE")]
    if model:
        provider_ref_parts.append(str(model))

    result = emit_controlled_arrival(
        repository=repository,
        connection_ref=connection_ref,
        client_instance_id=client_instance_id,
        provider=provider,
        provider_ref="|".join(provider_ref_parts),
        agent=str(actor) if actor else provider,
        branch=str(envelope.get("branch")) if envelope.get("branch") else None,
        observed_head=str(envelope.get("observed_head")) if envelope.get("observed_head") else None,
        token=token,
        request_fn=request_fn,
    )
    return {
        **result,
        "identity_strength": "EXACT",
        "identity_source": ref_kind,
        "mutation_authority_granted": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Provider-side first-touch ingress adapter")
    parser.add_argument("--envelope", required=True, help="Path to provider first-touch envelope JSON")
    parser.add_argument("--capture-output", required=True)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()

    envelope = json.loads(Path(args.envelope).read_text(encoding="utf-8"))
    if not isinstance(envelope, dict):
        raise ValueError("provider envelope must be a JSON object")

    capture = build_capture(envelope)
    output = Path(args.capture_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(capture, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    result: dict[str, Any] = {
        "status": "PROVIDER_FIRST_TOUCH_CAPTURED",
        "capture_id": capture["capture_id"],
        "capture_output": str(output),
        "mutation_authority_granted": False,
    }
    if args.emit:
        import os
        result["gscc"] = emit_if_identifiable(envelope, token=os.environ.get("GITHUB_TOKEN"))

    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
