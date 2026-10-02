#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gscc_function_exposure_gate import (
    build_arrival_route,
    evaluate_function_exposure,
    exposed_function_catalogue,
)
from gscc import InMemoryTransport, SessionEndpoint, instrument_tool

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "gscc-function-exposure-gate.yml"


class ExposureGateTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 2, 7, 0, tzinfo=timezone.utc)
        self.connection_ref = "gscc-observable:repo:actor:ref:main"
        self.head = "a" * 40
        self.snapshot = {
            "status": "CURRENT",
            "catalogue": {
                "status": "CURRENT",
                "tools": [
                    {
                        "name": "read_tool",
                        "surface": "read",
                        "authority_required": "READ_ONLY_DISCOVERY_AUTHORITY",
                        "contract_digest": "d" * 64,
                        "description": "safe read"
                    },
                    {
                        "name": "write_tool",
                        "surface": "scoped-write",
                        "authority_required": "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
                        "contract_digest": "e" * 64,
                        "description": "bounded write"
                    }
                ]
            },
            "refresh_policy": {
                "pre_mutation_live_refresh_required": True
            }
        }
        self.sessions = {
            "sessions": [
                {
                    "session_id": "session-live",
                    "status": "ACTIVE",
                    "connection_ref": self.connection_ref,
                    "connection_method": "gscc-github-event-gateway",
                    "surface_class": "GITHUB_EVENT_VISIBLE",
                    "last_observed_head_sha": self.head,
                    "relay": {
                        "state": "ACTIVE",
                        "lease_expires_at": (self.now + timedelta(minutes=20)).isoformat()
                    }
                }
            ]
        }

    def evidence(self, authority_class, *, preflight=None):
        value = {
            "authority_class": authority_class,
            "granted": True,
            "evidence_ref": "owner-authority:fixture"
        }
        if preflight is not None:
            value["live_preflight"] = preflight
        return value

    def test_arrival_route_is_locked_until_function_validation(self):
        route = build_arrival_route(
            repository="owner/repo",
            connection_ref=self.connection_ref,
            surface_class="GITHUB_EVENT_VISIBLE",
            observed_head=self.head,
        )
        self.assertEqual(route["status"], "LOCKED_PENDING_FUNCTION_REQUEST")
        self.assertEqual(route["first_stage"], "GSCC_SESSION_BIND")
        self.assertIn("FUNCTION_CONTRACT_MATCH", route["required_stages"])
        self.assertIn("AUTHORITY_VALIDATION", route["required_stages"])
        self.assertIn("EXPOSURE_RECEIPT", route["required_stages"])

    def test_read_function_requires_explicit_authority_evidence(self):
        denied = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            authority_evidence=None,
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(denied["status"], "WITHHELD")
        self.assertEqual(denied["reason_code"], "AUTHORITY_EVIDENCE_REQUIRED")

        allowed = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(allowed["status"], "VALIDATED")
        self.assertTrue(allowed["exposable"])
        self.assertTrue(allowed["exposure_receipt"].startswith("GSCC-EXPOSURE-"))

    def test_mutation_function_requires_authority_and_live_preflight(self):
        no_preflight = evaluate_function_exposure(
            tool_name="write_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            authority_evidence=self.evidence("EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"),
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(no_preflight["status"], "WITHHELD")
        self.assertEqual(no_preflight["reason_code"], "LIVE_PREFLIGHT_REQUIRED")

        allowed = evaluate_function_exposure(
            tool_name="write_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            authority_evidence=self.evidence(
                "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
                preflight={"status": "PASSED", "observed_head": self.head, "evidence_ref": "preflight:fixture"},
            ),
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(allowed["status"], "VALIDATED")
        self.assertTrue(allowed["exposable"])

    def test_wrong_head_or_unknown_tool_fails_closed(self):
        wrong = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head="b" * 40,
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(wrong["status"], "DENIED")
        self.assertEqual(wrong["reason_code"], "EXACT_HEAD_MISMATCH")

        unknown = evaluate_function_exposure(
            tool_name="missing_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(unknown["status"], "DENIED")
        self.assertEqual(unknown["reason_code"], "FUNCTION_NOT_IN_CANONICAL_CATALOGUE")

    def test_non_gscc_or_expired_session_fails_closed(self):
        bad = json.loads(json.dumps(self.sessions))
        bad["sessions"][0]["connection_method"] = "direct-provider-connector"
        denied = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=bad,
            now=self.now,
        )
        self.assertEqual(denied["reason_code"], "GSCC_BOUND_ACTIVE_SESSION_REQUIRED")

    def test_catalogue_exposes_only_validated_functions(self):
        evidence = {
            "read_tool": self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            "write_tool": self.evidence("EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"),
        }
        result = exposed_function_catalogue(
            connection_ref=self.connection_ref,
            requested_head=self.head,
            authority_evidence_by_tool=evidence,
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual([x["name"] for x in result["functions"]], ["read_tool"])
        self.assertEqual(result["withheld"][0]["name"], "write_tool")

    def test_instrumented_tool_revalidates_before_real_call(self):
        transport = InMemoryTransport()
        endpoint = SessionEndpoint(
            transport,
            source={"session_id": "session-live", "client_instance_id": "client-a"},
            target={"system": "gacr"},
            scope={"repository": "owner/repo", "observed_head": self.head},
        )
        calls = []
        def guard(tool_name):
            calls.append(("guard", tool_name))
            return {"status": "VALIDATED", "exposable": True, "exposure_receipt": "GSCC-EXPOSURE-ok"}

        wrapped = instrument_tool(endpoint, "read_tool", lambda: calls.append(("call", "read_tool")) or "ok", exposure_guard=guard)
        self.assertEqual(wrapped(), "ok")
        self.assertEqual(calls, [("guard", "read_tool"), ("call", "read_tool")])
        serialized = "\n".join(m.serialize() for m in transport.sent)
        self.assertIn("FUNCTION_EXPOSURE_GATE", serialized)
        self.assertIn("TOOL_STARTED", serialized)
        self.assertIn("TOOL_COMPLETED", serialized)

    def test_instrumented_tool_denial_blocks_real_call(self):
        transport = InMemoryTransport()
        endpoint = SessionEndpoint(transport, source={"session_id": "session-live"}, target={"system": "gacr"})
        called = []
        wrapped = instrument_tool(
            endpoint,
            "write_tool",
            lambda: called.append(True),
            exposure_guard=lambda _: {"status": "WITHHELD", "exposable": False, "reason_code": "AUTHORITY_EVIDENCE_REQUIRED"},
        )
        with self.assertRaises(PermissionError):
            wrapped()
        self.assertEqual(called, [])
        serialized = "\n".join(m.serialize() for m in transport.sent)
        self.assertIn("FUNCTION_EXPOSURE_GATE", serialized)
        self.assertNotIn("TOOL_STARTED", serialized)

    def test_workflow_is_mandatory_and_fail_closed(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("gscc_function_exposure_request", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("python3 scripts/gscc_function_exposure_gate.py evaluate", text)
        self.assertIn("python3 scripts/gscc_function_exposure_gate.py arrival-plan", text)
        self.assertIn("actions/upload-artifact@v4", text)
        self.assertNotIn("continue-on-error: true", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
