#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import first_touch_field_block_gate as fb
import first_touch_connection_completeness as cp
import first_touch_entry_contract as ec

from provider_first_touch_ingress import (
    SCHEMA,
    build_capture,
    classify_identity,
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
        result = classify_identity(value)
        self.assertEqual(result["status"], "CAPTURE_ONLY_IDENTITY_UNRESOLVED")
        self.assertEqual(result["identity_strength"], "UNRESOLVED")
        self.assertFalse(result["mutation_authority_granted"])

    def test_provider_capture_is_ready_for_canonical_q1_entry(self):
        value = envelope()
        capture = build_capture(value, observed_at="2026-10-06T05:30:00+00:00")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            cap=root/"capture.json"
            db=root/"capture.sqlite"
            comp=root/"completeness.json"
            cap.write_text(json.dumps(capture),encoding="utf-8")
            fb.build_capture_database(cap,db,source_ref="provider-unit-test")
            cp.build_packet(None,comp,capture_path=cap)
            strength, anchor = ec.discover_identity(cap)
            self.assertEqual(strength,"EXACT")
            self.assertEqual(anchor,"provider_conversation_ref:provider-conversation-123")
            result=ec.evaluate(comp,db,identity_strength=strength,identity_anchor=anchor,first_touch_seen=False)
            self.assertEqual(result["status"],"ENTRY_READY_FOR_Q1",result)
            self.assertEqual(result["classification"],"FIRST_TOUCH")
            self.assertFalse(result["authority_granted"])

    def test_q10_gacr_dispatch_respects_github_payload_width(self):
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/gscc-provider-first-touch-ingress.yml").read_text(encoding="utf-8")
        self.assertIn('payload["arrival_context"]=arrival_context', workflow)
        self.assertIn('"same_logical_agent_session_id","continuity_id","continuity_evidence_ref"', workflow.replace("\n","").replace(" ",""))
        self.assertIn('payload.pop("logical_agent_alias",None)', workflow)
        self.assertIn('if len(payload)>10:', workflow)
        self.assertIn('GACR_DISPATCH_CLIENT_PAYLOAD_TOO_WIDE', workflow)
        self.assertNotIn('payload["repository"]=os.environ["GITHUB_REPOSITORY"]', workflow)

    def test_stable_identity_routes_to_canonical_gscc_q1_pipeline(self):
        value = envelope()
        capture = build_capture(value, observed_at="2026-10-06T05:30:00+00:00")
        result = classify_identity(value)
        self.assertEqual(result["status"], "READY_FOR_GSCC_Q1_PIPELINE")
        self.assertEqual(result["identity_strength"], "EXACT")
        self.assertEqual(result["identity_source"], "conversation_ref")
        self.assertFalse(result["mutation_authority_granted"])
        self.assertEqual(capture["safe_ingress"]["status"], "VALID")
        self.assertEqual(capture["safe_ingress"]["ingress_type"], "FIRST_TOUCH")
        self.assertTrue(capture["safe_ingress"]["connection_ref"].startswith("provider-first-touch:chatgpt:conversation_ref:"))
        self.assertEqual(capture["safe_ingress"]["provider_conversation_ref"], "provider-conversation-123")


if __name__ == "__main__":
    unittest.main()
