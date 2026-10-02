#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gscc_function_exposure_gate import (
    build_arrival_route,
    build_package_route_receipt,
    evaluate_function_exposure,
    exposed_function_catalogue,
)
from gscc import InMemoryTransport, SessionEndpoint, instrument_tool

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "gscc-function-exposure-gate.yml"
EXECUTION_WORKFLOW = ROOT / ".github" / "workflows" / "governed-execution.yml"
SNAPSHOT_PATH = ROOT / ".governance" / "control-plane-state" / "mcp-capability-snapshot.json"
UPGRADER = ROOT / "scripts" / "control_plane_upgrade_local_entry.py"


class ExposureGateTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 2, 7, 0, tzinfo=timezone.utc)
        self.connection_ref = "gscc-observable:repo:actor:ref:main"
        self.repository = "owner/repo"
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
                    "repository": self.repository,
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

    def access_grant(self, **overrides):
        value = {
            "schema": "gscc-access-grant/v1",
            "grant_id": "GSCC-GRANT-" + ("f" * 64),
            "admission_id": "GSCC-ADM-" + ("e" * 64),
            "session_id": "session-live",
            "connection_ref": self.connection_ref,
            "repository": self.repository,
            "status": "AUTHORIZED",
            "access_class": "GOVERNED_FUNCTION_EXPOSURE_ELIGIBLE",
            "bound_head": self.head,
            "allowed_authority_classes": [
                "READ_ONLY_DISCOVERY_AUTHORITY",
                "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
            ],
            "constraints": {"direct_main_write": False, "merge": False},
            "issued_at": self.now.isoformat(),
            "expires_at": (self.now + timedelta(minutes=15)).isoformat(),
            "invocation_authority_granted": False,
            "mutation_authority_granted": False,
        }
        value.update(overrides)
        return value


    def test_arrival_route_is_locked_until_function_validation(self):
        route = build_arrival_route(
            repository="owner/repo",
            connection_ref=self.connection_ref,
            surface_class="GITHUB_EVENT_VISIBLE",
            observed_head=self.head,
        )
        self.assertEqual(route["status"], "LOCKED_PENDING_FUNCTION_REQUEST")
        self.assertEqual(route["first_stage"], "ADMISSION_RECEIPT_VALIDATION")
        self.assertIn("ACCESS_GRANT_VALIDATION", route["required_stages"])
        self.assertIn("GSCC_SESSION_BIND", route["required_stages"])
        self.assertIn("FUNCTION_CONTRACT_MATCH", route["required_stages"])
        self.assertIn("AUTHORITY_VALIDATION", route["required_stages"])
        self.assertIn("EXPOSURE_RECEIPT", route["required_stages"])


    def test_access_grant_is_required_before_any_function_exposure(self):
        denied = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(),
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(denied["status"], "WITHHELD")
        self.assertEqual(denied["reason_code"], "ACCESS_GRANT_REQUIRED")
        self.assertFalse(denied["exposable"])

    def test_read_function_requires_explicit_authority_evidence(self):
        denied = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(),
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
            access_grant=self.access_grant(),
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
            access_grant=self.access_grant(),
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
            access_grant=self.access_grant(),
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
            access_grant=self.access_grant(),
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(wrong["status"], "DENIED")
        self.assertEqual(wrong["reason_code"], "ACCESS_GRANT_HEAD_MISMATCH")

        unknown = evaluate_function_exposure(
            tool_name="missing_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(),
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(unknown["status"], "DENIED")
        self.assertEqual(unknown["reason_code"], "FUNCTION_NOT_IN_CANONICAL_CATALOGUE")


    def test_expired_access_grant_fails_closed(self):
        expired = self.access_grant(expires_at=(self.now - timedelta(seconds=1)).isoformat())
        result = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=expired,
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(result["status"], "DENIED")
        self.assertEqual(result["reason_code"], "ACCESS_GRANT_EXPIRED")

    def test_non_gscc_or_expired_session_fails_closed(self):
        bad = json.loads(json.dumps(self.sessions))
        bad["sessions"][0]["connection_method"] = "direct-provider-connector"
        denied = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(),
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
            access_grant=self.access_grant(),
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

    def test_package_route_covers_every_mcp_invocation_without_granting_authority(self):
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        package = {
            "operation_id": "OP-GSCC-PACKAGE-1",
            "intent": "DEPLOY_APPLICATION",
            "bindings": {
                "steps": {
                    "preflight": [
                        {"backend": "MCP_DIRECT", "capability": "SERVER_RUNTIME_OBSERVATION", "tool": "docker_status_s2", "arguments": {}},
                    ],
                    "execute": [
                        {"backend": "MCP_DIRECT", "capability": "DEPLOYMENT_RUNTIME_CHANGE", "tool": "deploy_project_s2", "arguments": {"project": "brvmchainsolution"}},
                    ],
                    "verify": [
                        {"backend": "MCP_DIRECT", "capability": "SERVER_RUNTIME_OBSERVATION", "tool": "docker_status_s2", "arguments": {}},
                    ],
                    "rollback": [],
                }
            },
        }
        receipt = build_package_route_receipt(
            snapshot=snapshot,
            package=package,
            repository="chainsolutions-wealthtech/Governed-Repository-Template",
            source_head="f" * 40,
        )
        self.assertEqual(receipt["status"], "GSCC_PACKAGE_ROUTE_VALIDATED")
        self.assertTrue(receipt["route_validation_only"])
        self.assertFalse(receipt["mutation_authority_granted"])
        self.assertFalse(receipt["invocation_authority_granted"])
        self.assertEqual(receipt["invocation_count"], 3)
        self.assertEqual([x["tool_name"] for x in receipt["invocations"]], ["docker_status_s2", "deploy_project_s2", "docker_status_s2"])
        self.assertEqual(receipt["invocations"][1]["argument_keys"], ["project"])
        self.assertNotIn("arguments", receipt["invocations"][1])
        self.assertEqual(receipt["invocations"][1]["route"], list(receipt["required_stages"]))
        self.assertTrue(receipt["validation_digest"])

    def test_live_catalogue_marks_every_function_as_gscc_required(self):
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        tools = snapshot["catalogue"]["tools"]
        self.assertGreater(len(tools), 100)
        self.assertTrue(all(x.get("governed_exposure_gate") == "GSCC_REQUIRED" for x in tools))
        self.assertTrue(all(x.get("governed_exposure_status") == "REQUIRES_RUNTIME_VALIDATION" for x in tools))
        contract = snapshot["operation_planning_contract"]
        self.assertTrue(contract["gscc_function_gate_required_before_governed_exposure"])
        self.assertTrue(contract["gscc_function_gate_required_before_every_governed_invocation"])
        self.assertTrue(contract["catalogue_presence_is_not_governed_exposure_authority"])

    def test_governed_execution_must_call_same_exposure_workflow(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_call:", workflow)
        self.assertIn("package-evaluate:", workflow)
        self.assertIn("build-package-route", workflow)
        self.assertIn("route_validated", workflow)
        execution = EXECUTION_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("function-exposure-gate:", execution)
        self.assertIn("uses: ./.github/workflows/gscc-function-exposure-gate.yml", execution)
        self.assertIn("needs: function-exposure-gate", execution)
        self.assertIn("GSCC_FUNCTION_ROUTE_VALIDATED", execution)
        self.assertIn("GSCC_FUNCTION_ROUTE_VALIDATION_DIGEST", execution)

    def test_client_upgrader_distributes_canonical_arrival_gateway(self):
        text = UPGRADER.read_text(encoding="utf-8")
        self.assertIn('"scripts/gscc/protocol.py"', text)
        self.assertIn('"scripts/gscc_observable_arrival.py"', text)
        self.assertIn('".github/workflows/gscc-observable-arrival.yml"', text)

    def test_workflow_is_mandatory_and_fail_closed(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("gscc_function_exposure_request", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("python3 scripts/gscc_function_exposure_gate.py evaluate", text)
        self.assertIn("access_grant_json", text)
        self.assertIn("ACCESS_GRANT_JSON", text)
        self.assertIn("python3 scripts/gscc_function_exposure_gate.py arrival-plan", text)
        self.assertIn("actions/upload-artifact@v4", text)
        self.assertNotIn("continue-on-error: true", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)