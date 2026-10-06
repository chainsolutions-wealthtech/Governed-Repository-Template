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

    def test_capture_id_is_deterministic_for_same_material(self):
        value = envelope()
        a = build_capture(value, observed_at="2026-10-06T05:30:00+00:00")
        b = build_capture(value, observed_at="2026-10-06T05:30:00+00:00")
        self.assertEqual(a["capture_id"], b["capture_id"])
        self.assertEqual(a["capture_digest"], b["capture_digest"])

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

        def request_fn(url, *, method, token, payload=None):
            calls.append((url, method, token, payload))
            return 204, b""

        result = emit_if_identifiable(value, token="test-token", request_fn=request_fn)
        self.assertEqual(result["status"], "GSCC_ARRIVAL_DISPATCHED")
        self.assertEqual(result["identity_strength"], "EXACT")
        self.assertEqual(result["identity_source"], "conversation_ref")
        self.assertFalse(result["mutation_authority_granted"])
        self.assertTrue(calls)


if __name__ == "__main__":
    unittest.main()
