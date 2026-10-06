#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from provider_first_touch_ingress import (
    SCHEMA,
    build_capture,
    emit_if_identifiable,
    validate_envelope,
)


def envelope() -> dict:
    return {
        "schema": SCHEMA,
        "provider": "chatgpt",
        "transport": "chatgpt-github-direct",
        "model": "GPT-5.6 Sol",
        "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
        "actor": "Wealthtechinnovations",
        "branch": "main",
        "observed_head": "6891292cf4ae0ffea17835f758e7d8d44136eade",
        "identity": {
            "conversation_ref": "provider-conversation-123",
            "session_ref": "UNAVAILABLE",
        },
        "capabilities": {
            "pull": True,
            "push": True,
            "admin": True,
        },
        "unavailable": {
            "installation_id": "UNAVAILABLE",
            "client_id": "UNAVAILABLE",
        },
        "codex_used": False,
        "github_app_codex_used": False,
        "codex_workspace_created": False,
        "codex_task_created": False,
        "repository_mutated": False,
        "secret_accessed": False,
        "token_exposed": False,
        "oauth_secret_exposed": False,
        "private_key_exposed": False,
        "conversation_id_exposed": False,
        "session_id_exposed": False,
        "installation_id_exposed": False,
        "client_id_exposed": False,
        "ip_exposed": False,
        "tool": {
            "name": "mcp__GitHub__get_repo",
            "operation": "read_repository",
            "category": "READ",
            "success": True,
        },
    }


class ProviderFirstTouchIngressTests(unittest.TestCase):
    def test_capture_preserves_provider_context_losslessly(self):
        value = envelope()
        capture = build_capture(value, observed_at="2026-10-06T05:30:00+00:00")
        self.assertEqual(capture["provider_context"], value)
        self.assertEqual(capture["repository"], value["repository"])
        self.assertEqual(capture["schema"], "first-touch-exhaustive-capture/v1")
        self.assertFalse(capture["mutation_authority_granted"])
        self.assertFalse(capture["interpretation_applied"])
        self.assertTrue(capture["capture_id"].startswith("FTC-"))
        self.assertEqual(capture["field_evidence_contract"]["schema"], "first-touch-field-evidence/v1")
        self.assertEqual(capture["field_evidence_contract"]["expected_field_count"], len(capture["field_evidence"]))
        self.assertFalse(capture["field_evidence_contract"]["silent_absence_allowed"])
        self.assertGreaterEqual(len(capture["field_evidence"]), 600)
        by_id = {row["field_id"]: row for row in capture["field_evidence"]}
        self.assertEqual(by_id["agent.provider"]["value"], "chatgpt")
        self.assertEqual(by_id["agent.provider"]["source"], "provider_envelope")
        self.assertEqual(by_id["agent.provider"]["confidence"], "exact")
        self.assertEqual(by_id["agent.model"]["value"], "GPT-5.6 Sol")
        self.assertEqual(by_id["repository.full_name"]["value"], value["repository"])
        self.assertEqual(by_id["git.head"]["value"], value["observed_head"])
        self.assertEqual(by_id["negative.codex_used"]["value"], False)
        self.assertEqual(by_id["negative.secret_accessed"]["value"], False)
        self.assertEqual(by_id["session.conversation_id"]["value"], "UNAVAILABLE")
        self.assertEqual(by_id["session.conversation_id"]["source"], "not_exposed")

    def test_capture_id_is_deterministic_for_same_material(self):
        value = envelope()
        a = build_capture(value, observed_at="2026-10-06T05:30:00+00:00")
        b = build_capture(value, observed_at="2026-10-06T05:30:00+00:00")
        self.assertEqual(a["capture_id"], b["capture_id"])
        self.assertEqual(a["capture_digest"], b["capture_digest"])

    def test_negative_security_status_fields_are_allowed(self):
        value = envelope()
        validate_envelope(value)
        capture = build_capture(value, observed_at="2026-10-06T05:30:00+00:00")
        by_id = {row["field_id"]: row for row in capture["field_evidence"]}
        self.assertFalse(by_id["negative.token_exposed"]["value"])
        self.assertFalse(by_id["negative.oauth_secret_exposed"]["value"])

    def test_sensitive_keys_are_rejected(self):
        value = envelope()
        value["oauth_token"] = "must-never-enter-capture"
        with self.assertRaisesRegex(ValueError, "sensitive field forbidden"):
            validate_envelope(value)

    def test_unresolved_identity_is_capture_only(self):
        value = envelope()
        value["identity"] = {
            "conversation_ref": "UNAVAILABLE",
            "session_ref": "UNAVAILABLE",
        }
        result = emit_if_identifiable(value)
        self.assertEqual(result["status"], "CAPTURE_ONLY_IDENTITY_UNRESOLVED")
        self.assertEqual(result["identity_strength"], "UNRESOLVED")
        self.assertFalse(result["mutation_authority_granted"])

    def test_stable_identity_routes_through_existing_controlled_arrival(self):
        value = envelope()
        calls = []

        def request_fn(method, url, token, body=None):
            calls.append((method, url, token, body))
            return 204, b""

        result = emit_if_identifiable(value, token="test-token", request_fn=request_fn)
        self.assertEqual(result["status"], "GSCC_ARRIVAL_DISPATCHED")
        self.assertEqual(result["identity_strength"], "EXACT")
        self.assertEqual(result["identity_source"], "conversation_ref")
        self.assertFalse(result["mutation_authority_granted"])
        self.assertTrue(calls)


if __name__ == "__main__":
    unittest.main()
