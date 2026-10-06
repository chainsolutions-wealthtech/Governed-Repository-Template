#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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



def _safe_ingress(envelope: dict[str, Any], observed_at: str) -> dict[str, Any]:
    ref_kind, stable_ref = _stable_ref(envelope)
    provider = str(envelope.get("provider") or "provider")
    if not stable_ref:
        return {
            "schema":"gscc-first-touch-safe-ingress/v1",
            "status":"INVALID",
            "reason":"NO_SAFE_IDENTITY_ANCHOR",
            "ingress_type":"FIRST_TOUCH",
            "source":"PROVIDER_FIRST_TOUCH_ENVELOPE",
            "source_method":"REPOSITORY_DISPATCH",
            "observed_at":observed_at,
            "freeform_body_persisted":False,
        }
    connection_ref=f"provider-first-touch:{provider}:{ref_kind}:{stable_ref}"
    client_instance_id=f"{provider}:{ref_kind}:{stable_ref}"
    identity=envelope.get("identity") if isinstance(envelope.get("identity"),dict) else {}
    conversation_ref=identity.get("conversation_ref")
    provider_conversation_ref=conversation_ref if ref_kind=="conversation_ref" else None
    return {
        "schema":"gscc-first-touch-safe-ingress/v1",
        "status":"VALID",
        "ingress_type":"FIRST_TOUCH",
        "connection_ref":connection_ref,
        "client_instance_id":client_instance_id,
        "conversation_ref":conversation_ref if isinstance(conversation_ref,str) and conversation_ref.upper() not in UNAVAILABLE_MARKERS else None,
        "provider_conversation_ref":provider_conversation_ref if isinstance(provider_conversation_ref,str) and provider_conversation_ref.upper() not in UNAVAILABLE_MARKERS else None,
        "conversation_ref_status":"PRESENT" if ref_kind=="conversation_ref" else "UNAVAILABLE",
        "provider_conversation_ref_status":"PRESENT" if ref_kind=="conversation_ref" else "UNAVAILABLE",
        "identity_source":ref_kind,
        "source":"PROVIDER_FIRST_TOUCH_ENVELOPE",
        "source_method":"REPOSITORY_DISPATCH",
        "observed_at":observed_at,
        "freeform_body_persisted":False,
    }

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
        "safe_ingress": _safe_ingress(envelope, observed_at),
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


def classify_identity(envelope: dict[str, Any]) -> dict[str, Any]:
    validate_envelope(envelope)
    ref_kind, stable_ref = _stable_ref(envelope)
    if not stable_ref:
        return {
            "status":"CAPTURE_ONLY_IDENTITY_UNRESOLVED",
            "identity_strength":"UNRESOLVED",
            "identity_source":None,
            "mutation_authority_granted":False,
        }
    return {
        "status":"READY_FOR_GSCC_Q1_PIPELINE",
        "identity_strength":"EXACT" if ref_kind in {"conversation_ref","session_ref"} else "STRONG",
        "identity_source":ref_kind,
        "mutation_authority_granted":False,
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="Provider-side first-touch ingress adapter")
    parser.add_argument("--envelope", required=True, help="Path to provider first-touch envelope JSON")
    parser.add_argument("--capture-output", required=True)
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
    result["identity"] = classify_identity(envelope)

    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
