#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import gscc_function_exposure_gate as exposure_gate
from gscc.capability_projection import build_portable_capability_projection
from gscc_function_exposure_gate import (
    build_arrival_route,
    build_package_route_receipt,
    evaluate_function_exposure,
    evaluate_issue_comment_exposure,
    exposed_function_catalogue,
)
from gscc import InMemoryTransport, SessionEndpoint, instrument_tool
from gscc_observable_arrival import should_skip_github_arrival

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "gscc-function-exposure-gate.yml"
EXECUTION_WORKFLOW = ROOT / ".github" / "workflows" / "governed-execution.yml"
SNAPSHOT_PATH = exposure_gate._default_snapshot_path()
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

    def evidence(self, authority_class, *, preflight=None, route_gate=None):
        value = {
            "authority_class": authority_class,
            "granted": True,
            "evidence_ref": "owner-authority:fixture"
        }
        if preflight is not None:
            value["live_preflight"] = preflight
        if route_gate is not None:
            value["route_gate_evidence"] = route_gate
        return value

    def route_gate(self, entry_action, satisfied_gates, *, branch=None):
        value = {
            "schema": "gscc-entry-action-gate-evidence/v1",
            "status": "PASSED",
            "entry_action": entry_action,
            "session_id": "session-live",
            "observed_head": self.head,
            "satisfied_gates": list(satisfied_gates),
            "evidence_ref": "entry-route:fixture",
        }
        if branch is not None:
            value["branch"] = branch
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
            "entry_action": "REPOSITORY_ACCESS",
            "connection_intent": "READ_ONLY_DISCOVERY",
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



    def function_issue_payload(self, *, tool_name="read_tool", authority_class="READ_ONLY_DISCOVERY_AUTHORITY"):
        return {
            "schema": "gscc-function-exposure-request/v1",
            "connection_ref": self.connection_ref,
            "tool_name": tool_name,
            "observed_head": self.head,
            "access_grant": self.access_grant(
                allowed_authority_classes=["READ_ONLY_DISCOVERY_AUTHORITY"]
            ),
            "authority": {
                "authority_class": authority_class,
                "evidence_ref": "gscc-access-policy:fixture",
                "granted": True,
            },
        }

    def function_issue_event(self, payload, *, issue_number=161, association="OWNER"):
        return {
            "action": "created",
            "issue": {"number": issue_number},
            "comment": {
                "body": "/gscc-function-exposure " + json.dumps(payload, separators=(",", ":")),
                "author_association": association,
            },
            "sender": {"login": "owner"},
        }

    def test_issue_comment_read_exposure_reuses_canonical_gate(self):
        result = evaluate_issue_comment_exposure(
            self.function_issue_event(self.function_issue_payload()),
            expected_issue_number=161,
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(result["status"], "VALIDATED")
        self.assertTrue(result["exposable"])
        self.assertEqual(result["tool_name"], "read_tool")
        self.assertEqual(result["authority_required"], "READ_ONLY_DISCOVERY_AUTHORITY")
        self.assertTrue(result["exposure_receipt"].startswith("GSCC-EXPOSURE-"))

    def test_issue_comment_staged_adoption_mutation_carries_route_gate_evidence(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0].update({
            "connection_method": "controlled-client-adapter",
            "surface_class": "CONTROLLED_INSTRUMENTABLE",
            "entry_action": "ADOPT_EXISTING_REPOSITORY",
            "connection_intent": "CODE_CHANGE",
            "branch": "governance/adoption",
        })
        payload = self.function_issue_payload(
            tool_name="write_tool",
            authority_class="EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
        )
        payload["access_grant"] = self.access_grant(
            allowed_authority_classes=["EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"]
        )
        payload["authority"] = self.evidence(
            "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
            preflight={
                "status": "PASSED",
                "observed_head": self.head,
                "evidence_ref": "preflight:fixture",
            },
            route_gate=self.route_gate(
                "ADOPT_EXISTING_REPOSITORY",
                [
                    "EXACT_HEAD_OBSERVED",
                    "CLEAN_OR_EXPLICITLY_RECONCILED",
                    "ADOPTION_PLAN_ACCEPTED",
                ],
                branch="governance/adoption",
            ),
        )
        result = evaluate_issue_comment_exposure(
            self.function_issue_event(payload),
            expected_issue_number=161,
            snapshot=self.snapshot,
            sessions=sessions,
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual(result["status"], "VALIDATED")
        self.assertEqual(result["route_gate_evidence_ref"], "entry-route:fixture")

    def test_issue_comment_exposure_is_bounded_and_fail_closed(self):
        wrong_issue = self.function_issue_event(self.function_issue_payload(), issue_number=162)
        with self.assertRaises(ValueError):
            evaluate_issue_comment_exposure(
                wrong_issue,
                expected_issue_number=161,
                snapshot=self.snapshot,
                sessions=self.sessions,
                now=self.now,
            )

        unauthorized = self.function_issue_event(
            self.function_issue_payload(),
            association="NONE",
        )
        with self.assertRaises(ValueError):
            evaluate_issue_comment_exposure(
                unauthorized,
                expected_issue_number=161,
                snapshot=self.snapshot,
                sessions=self.sessions,
                now=self.now,
            )

        write_result = evaluate_issue_comment_exposure(
            self.function_issue_event(
                self.function_issue_payload(
                    tool_name="write_tool",
                    authority_class="EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
                )
            ),
            expected_issue_number=161,
            snapshot=self.snapshot,
            sessions=self.sessions,
            now=self.now,
        )
        self.assertEqual(write_result["status"], "DENIED")
        self.assertEqual(write_result["reason_code"], "ACCESS_GRANT_AUTHORITY_CLASS_MISMATCH")

    def test_function_exposure_issue_comment_does_not_create_arrival_session(self):
        event = self.function_issue_event(self.function_issue_payload())
        reason = should_skip_github_arrival(
            event,
            {"GITHUB_EVENT_NAME": "issue_comment", "GITHUB_ACTOR": "owner"},
        )
        self.assertEqual(reason, "INTERNAL_GSCC_FUNCTION_EXPOSURE_INGRESS")


    def test_controlled_repository_surface_is_valid_for_gscc_function_exposure(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0]["connection_method"] = "controlled-repository-surface"
        sessions["sessions"][0]["surface_class"] = "CONTROLLED_INSTRUMENTABLE"
        sessions["sessions"][0]["entry_action"] = "CONTINUE_GOVERNED_WORK"
        sessions["sessions"][0]["connection_intent"] = "OBSERVE"

        result = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(allowed_authority_classes=["READ_ONLY_DISCOVERY_AUTHORITY"]),
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=sessions,
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual(result["status"], "VALIDATED")
        self.assertTrue(result["exposable"])

    def test_controlled_client_adapter_is_valid_for_gscc_function_exposure(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0]["connection_method"] = "controlled-client-adapter"
        sessions["sessions"][0]["surface_class"] = "CONTROLLED_INSTRUMENTABLE"
        sessions["sessions"][0]["entry_action"] = "CONTINUE_GOVERNED_WORK"
        sessions["sessions"][0]["connection_intent"] = "OBSERVE"

        result = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(
                allowed_authority_classes=["READ_ONLY_DISCOVERY_AUTHORITY"]
            ),
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=sessions,
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual(result["status"], "VALIDATED")
        self.assertTrue(result["exposable"])

    def test_controlled_client_requires_current_head_and_canonical_session_route(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0]["connection_method"] = "controlled-client-adapter"
        sessions["sessions"][0]["surface_class"] = "CONTROLLED_INSTRUMENTABLE"
        sessions["sessions"][0]["entry_action"] = "CONTINUE_GOVERNED_WORK"
        sessions["sessions"][0]["connection_intent"] = "OBSERVE"

        missing_head = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(allowed_authority_classes=["READ_ONLY_DISCOVERY_AUTHORITY"]),
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=sessions,
            now=self.now,
        )
        self.assertEqual(missing_head["status"], "DENIED")
        self.assertEqual(missing_head["reason_code"], "CURRENT_HEAD_REOBSERVATION_REQUIRED")

        forged_grant = self.access_grant(
            entry_action="ARBITRARY_CALLER_VALUE",
            connection_intent="ARBITRARY_CALLER_VALUE",
            allowed_authority_classes=["READ_ONLY_DISCOVERY_AUTHORITY"],
        )

        unresolved_entry = json.loads(json.dumps(sessions))
        unresolved_entry["sessions"][0]["entry_action"] = "UNKNOWN"
        result = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=forged_grant,
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=unresolved_entry,
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual(result["status"], "DENIED")
        self.assertEqual(result["reason_code"], "ENTRY_ACTION_RESOLUTION_REQUIRED")

        unresolved_intent = json.loads(json.dumps(sessions))
        unresolved_intent["sessions"][0]["connection_intent"] = "UNKNOWN"
        result = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=forged_grant,
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=unresolved_intent,
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual(result["status"], "DENIED")
        self.assertEqual(result["reason_code"], "CONNECTION_INTENT_RESOLUTION_REQUIRED")

    def test_current_head_reobservation_can_reconcile_persisted_session_lag(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0]["connection_method"] = "controlled-client-adapter"
        sessions["sessions"][0]["surface_class"] = "CONTROLLED_INSTRUMENTABLE"
        sessions["sessions"][0]["entry_action"] = "CONTINUE_GOVERNED_WORK"
        sessions["sessions"][0]["connection_intent"] = "OBSERVE"
        sessions["sessions"][0]["last_observed_head_sha"] = "b" * 40
        before = json.loads(json.dumps(sessions))

        result = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(
                allowed_authority_classes=["READ_ONLY_DISCOVERY_AUTHORITY"]
            ),
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=sessions,
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual(result["status"], "VALIDATED")
        self.assertEqual(
            result["head_reconciliation"]["status"],
            "REOBSERVED_CURRENT_HEAD",
        )
        self.assertEqual(
            result["head_reconciliation"]["previous_observed_head"],
            "b" * 40,
        )
        self.assertEqual(
            result["head_reconciliation"]["current_observed_head"],
            self.head,
        )
        self.assertFalse(
            result["head_reconciliation"]["canonical_session_store_mutated"]
        )
        self.assertEqual(sessions, before)

    def test_current_head_reobservation_fails_closed_on_real_head_mismatch(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0]["connection_method"] = "controlled-client-adapter"
        sessions["sessions"][0]["surface_class"] = "CONTROLLED_INSTRUMENTABLE"
        sessions["sessions"][0]["entry_action"] = "CONTINUE_GOVERNED_WORK"
        sessions["sessions"][0]["connection_intent"] = "OBSERVE"
        sessions["sessions"][0]["last_observed_head_sha"] = "b" * 40

        result = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(
                allowed_authority_classes=["READ_ONLY_DISCOVERY_AUTHORITY"]
            ),
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=sessions,
            current_repository_head="c" * 40,
            now=self.now,
        )
        self.assertEqual(result["status"], "DENIED")
        self.assertEqual(result["reason_code"], "EXACT_HEAD_MISMATCH")

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
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0]["branch"] = "feature/test"
        no_preflight = evaluate_function_exposure(
            tool_name="write_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(),
            authority_evidence=self.evidence("EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"),
            snapshot=self.snapshot,
            sessions=sessions,
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
            sessions=sessions,
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
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual([x["name"] for x in result["functions"]], ["read_tool"])
        self.assertEqual(result["withheld"][0]["name"], "write_tool")

    def test_controlled_client_catalogue_fails_closed_without_current_head(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0]["connection_method"] = "controlled-client-adapter"
        sessions["sessions"][0]["surface_class"] = "CONTROLLED_INSTRUMENTABLE"
        sessions["sessions"][0]["entry_action"] = "CONTINUE_GOVERNED_WORK"
        sessions["sessions"][0]["connection_intent"] = "OBSERVE"
        evidence = {"read_tool": self.evidence("READ_ONLY_DISCOVERY_AUTHORITY")}
        result = exposed_function_catalogue(
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(allowed_authority_classes=["READ_ONLY_DISCOVERY_AUTHORITY"]),
            authority_evidence_by_tool=evidence,
            snapshot=self.snapshot,
            sessions=sessions,
            now=self.now,
        )
        self.assertEqual(result["functions"], [])
        read_withheld = next(x for x in result["withheld"] if x["name"] == "read_tool")
        self.assertEqual(read_withheld["reason_code"], "CURRENT_HEAD_REOBSERVATION_REQUIRED")

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
        if (ROOT / ".template-source").exists():
            contract = snapshot["operation_planning_contract"]
            self.assertTrue(contract["gscc_function_gate_required_before_governed_exposure"])
            self.assertTrue(contract["gscc_function_gate_required_before_every_governed_invocation"])
            self.assertTrue(contract["catalogue_presence_is_not_governed_exposure_authority"])
        else:
            self.assertEqual(snapshot.get("scope"), "PORTABLE_CLIENT_PROJECTION")
            self.assertNotIn("servers", snapshot)
            self.assertNotIn("endpoint", snapshot)

    def test_governed_execution_must_call_same_exposure_workflow(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_call:", workflow)
        self.assertIn("package-evaluate:", workflow)
        self.assertIn("build-package-route", workflow)
        self.assertIn("route_validated", workflow)
        if not (ROOT / ".template-source").exists():
            self.skipTest("central governed-execution workflow is source-only")
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
        self.assertIn('"scripts/gscc/capability_projection.py"', text)
        self.assertIn('"scripts/gscc_function_exposure_gate.py"', text)
        self.assertIn('".governance/gscc/mcp-capability-snapshot.json"', text)
        self.assertIn('"scripts/test_gscc_function_exposure_gate.py"', text)
        self.assertIn('".github/workflows/gscc-function-exposure-gate.yml"', text)

    def test_controlled_host_gateway_requires_canonical_session_route(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0]["connection_method"] = "gscc-controlled-host-gateway"
        sessions["sessions"][0]["surface_class"] = "CONTROLLED_INSTRUMENTABLE"
        sessions["sessions"][0]["entry_action"] = "UNKNOWN"
        sessions["sessions"][0]["connection_intent"] = "UNKNOWN"

        denied = evaluate_function_exposure(
            tool_name="read_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(
                allowed_authority_classes=["READ_ONLY_DISCOVERY_AUTHORITY"]
            ),
            authority_evidence=self.evidence("READ_ONLY_DISCOVERY_AUTHORITY"),
            snapshot=self.snapshot,
            sessions=sessions,
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual(denied["status"], "DENIED")
        self.assertEqual(denied["reason_code"], "ENTRY_ACTION_RESOLUTION_REQUIRED")

    def test_adoption_mutation_requires_completed_entry_gates_not_initial_mutable(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0].update({
            "connection_method": "controlled-client-adapter",
            "surface_class": "CONTROLLED_INSTRUMENTABLE",
            "entry_action": "ADOPT_EXISTING_REPOSITORY",
            "connection_intent": "CODE_CHANGE",
            "branch": "governance/adoption",
        })
        preflight = {
            "status": "PASSED",
            "observed_head": self.head,
            "evidence_ref": "preflight:fixture",
        }

        incomplete = self.route_gate(
            "ADOPT_EXISTING_REPOSITORY",
            ["EXACT_HEAD_OBSERVED", "CLEAN_OR_EXPLICITLY_RECONCILED"],
            branch="governance/adoption",
        )
        denied = evaluate_function_exposure(
            tool_name="write_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(
                allowed_authority_classes=["EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"]
            ),
            authority_evidence=self.evidence(
                "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
                preflight=preflight,
                route_gate=incomplete,
            ),
            snapshot=self.snapshot,
            sessions=sessions,
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual(denied["status"], "DENIED")
        self.assertEqual(denied["reason_code"], "ENTRY_ACTION_REQUIRED_GATES_INCOMPLETE")

        complete = self.route_gate(
            "ADOPT_EXISTING_REPOSITORY",
            [
                "EXACT_HEAD_OBSERVED",
                "CLEAN_OR_EXPLICITLY_RECONCILED",
                "ADOPTION_PLAN_ACCEPTED",
            ],
            branch="governance/adoption",
        )
        allowed = evaluate_function_exposure(
            tool_name="write_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(
                allowed_authority_classes=["EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"]
            ),
            authority_evidence=self.evidence(
                "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
                preflight=preflight,
                route_gate=complete,
            ),
            snapshot=self.snapshot,
            sessions=sessions,
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual(allowed["status"], "VALIDATED")
        self.assertTrue(allowed["exposable"])
        self.assertEqual(allowed["route_gate_evidence_ref"], "entry-route:fixture")
        self.assertEqual(allowed["route_gate_entry_action"], "ADOPT_EXISTING_REPOSITORY")
        self.assertEqual(allowed["route_gate_branch"], "governance/adoption")
        self.assertRegex(allowed["route_gate_evidence_digest"], r"^[0-9a-f]{64}$")

    def test_staged_route_evidence_binding_mismatches_fail_closed(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0].update({
            "connection_method": "controlled-client-adapter",
            "surface_class": "CONTROLLED_INSTRUMENTABLE",
            "entry_action": "ADOPT_EXISTING_REPOSITORY",
            "connection_intent": "CODE_CHANGE",
            "branch": "governance/adoption",
        })
        preflight = {
            "status": "PASSED",
            "observed_head": self.head,
            "evidence_ref": "preflight:fixture",
        }
        base = self.route_gate(
            "ADOPT_EXISTING_REPOSITORY",
            [
                "EXACT_HEAD_OBSERVED",
                "CLEAN_OR_EXPLICITLY_RECONCILED",
                "ADOPTION_PLAN_ACCEPTED",
            ],
            branch="governance/adoption",
        )
        cases = [
            ("session_id", "other-session", "ENTRY_ACTION_GATE_EVIDENCE_MISMATCH"),
            ("observed_head", "b" * 40, "ENTRY_ACTION_GATE_EVIDENCE_HEAD_MISMATCH"),
            ("entry_action", "LAB_EVOLUTION", "ENTRY_ACTION_GATE_EVIDENCE_MISMATCH"),
            ("branch", "other/adoption", "ENTRY_ACTION_GATE_EVIDENCE_BRANCH_MISMATCH"),
        ]
        for key, bad_value, expected_reason in cases:
            with self.subTest(key=key):
                route_gate = json.loads(json.dumps(base))
                route_gate[key] = bad_value
                denied = evaluate_function_exposure(
                    tool_name="write_tool",
                    connection_ref=self.connection_ref,
                    requested_head=self.head,
                    access_grant=self.access_grant(
                        allowed_authority_classes=["EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"]
                    ),
                    authority_evidence=self.evidence(
                        "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
                        preflight=preflight,
                        route_gate=route_gate,
                    ),
                    snapshot=self.snapshot,
                    sessions=sessions,
                    current_repository_head=self.head,
                    now=self.now,
                )
                self.assertEqual(denied["status"], "DENIED")
                self.assertEqual(denied["reason_code"], expected_reason)

    def test_staged_routes_remain_closed_for_nonmutable_intents(self):
        for entry_action, intent, branch, gates in [
            (
                "ADOPT_EXISTING_REPOSITORY",
                "OBSERVE",
                "governance/adoption",
                ["EXACT_HEAD_OBSERVED", "CLEAN_OR_EXPLICITLY_RECONCILED", "ADOPTION_PLAN_ACCEPTED"],
            ),
            (
                "LAB_EVOLUTION",
                "REVIEW",
                "lab/authorized-change",
                ["EXACT_HEAD_OBSERVED", "LAB_BASELINE_CAPTURED", "EXPLICIT_BRANCH_OR_PR_AUTHORITY"],
            ),
        ]:
            with self.subTest(entry_action=entry_action, intent=intent):
                sessions = json.loads(json.dumps(self.sessions))
                sessions["sessions"][0].update({
                    "connection_method": "controlled-client-adapter",
                    "surface_class": "CONTROLLED_INSTRUMENTABLE",
                    "entry_action": entry_action,
                    "connection_intent": intent,
                    "branch": branch,
                })
                denied = evaluate_function_exposure(
                    tool_name="write_tool",
                    connection_ref=self.connection_ref,
                    requested_head=self.head,
                    access_grant=self.access_grant(
                        allowed_authority_classes=["EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"]
                    ),
                    authority_evidence=self.evidence(
                        "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
                        preflight={
                            "status": "PASSED",
                            "observed_head": self.head,
                            "evidence_ref": "preflight:fixture",
                        },
                        route_gate=self.route_gate(entry_action, gates, branch=branch),
                    ),
                    snapshot=self.snapshot,
                    sessions=sessions,
                    current_repository_head=self.head,
                    now=self.now,
                )
                self.assertEqual(denied["status"], "DENIED")
                self.assertEqual(denied["reason_code"], "CONNECTION_INTENT_POLICY_FORBIDS_MUTATION")

    def test_direct_main_write_constraint_is_enforced(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0].update({
            "connection_method": "controlled-client-adapter",
            "surface_class": "CONTROLLED_INSTRUMENTABLE",
            "entry_action": "ADOPT_EXISTING_REPOSITORY",
            "connection_intent": "CODE_CHANGE",
            "branch": "main",
        })
        route_gate = self.route_gate(
            "ADOPT_EXISTING_REPOSITORY",
            ["EXACT_HEAD_OBSERVED", "CLEAN_OR_EXPLICITLY_RECONCILED", "ADOPTION_PLAN_ACCEPTED"],
            branch="main",
        )
        denied = evaluate_function_exposure(
            tool_name="write_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(
                allowed_authority_classes=["EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"],
                constraints={"direct_main_write": False, "merge": False},
            ),
            authority_evidence=self.evidence(
                "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
                preflight={
                    "status": "PASSED",
                    "observed_head": self.head,
                    "evidence_ref": "preflight:fixture",
                },
                route_gate=route_gate,
            ),
            snapshot=self.snapshot,
            sessions=sessions,
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual(denied["status"], "DENIED")
        self.assertEqual(denied["reason_code"], "ACCESS_GRANT_DIRECT_MAIN_WRITE_FORBIDDEN")

    def test_lab_mutation_requires_completed_gates_and_noncanonical_branch(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0].update({
            "connection_method": "controlled-client-adapter",
            "surface_class": "CONTROLLED_INSTRUMENTABLE",
            "entry_action": "LAB_EVOLUTION",
            "connection_intent": "CODE_CHANGE",
            "branch": "trunk",
        })
        preflight = {
            "status": "PASSED",
            "observed_head": self.head,
            "evidence_ref": "preflight:fixture",
        }
        route_gate = self.route_gate(
            "LAB_EVOLUTION",
            [
                "EXACT_HEAD_OBSERVED",
                "LAB_BASELINE_CAPTURED",
                "EXPLICIT_BRANCH_OR_PR_AUTHORITY",
            ],
            branch="trunk",
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            governance = root / ".governance"
            governance.mkdir(parents=True)
            (governance / "profile.json").write_text(
                json.dumps({
                    "template_source": False,
                    "initialized": True,
                    "canonical_branch": "trunk",
                }),
                encoding="utf-8",
            )
            with patch.object(exposure_gate, "ROOT", root):
                denied = evaluate_function_exposure(
                    tool_name="write_tool",
                    connection_ref=self.connection_ref,
                    requested_head=self.head,
                    access_grant=self.access_grant(
                        allowed_authority_classes=["EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"],
                        constraints={"direct_main_write": True, "merge": False},
                    ),
                    authority_evidence=self.evidence(
                        "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
                        preflight=preflight,
                        route_gate=route_gate,
                    ),
                    snapshot=self.snapshot,
                    sessions=sessions,
                    current_repository_head=self.head,
                    now=self.now,
                )
                self.assertEqual(denied["status"], "DENIED")
                self.assertEqual(denied["reason_code"], "LAB_EVOLUTION_CANONICAL_BRANCH_FORBIDDEN")

                sessions["sessions"][0]["branch"] = "lab/authorized-change"
                route_gate["branch"] = "lab/authorized-change"
                allowed = evaluate_function_exposure(
                    tool_name="write_tool",
                    connection_ref=self.connection_ref,
                    requested_head=self.head,
                    access_grant=self.access_grant(
                        allowed_authority_classes=["EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"],
                        constraints={"direct_main_write": True, "merge": False},
                    ),
                    authority_evidence=self.evidence(
                        "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
                        preflight=preflight,
                        route_gate=route_gate,
                    ),
                    snapshot=self.snapshot,
                    sessions=sessions,
                    current_repository_head=self.head,
                    now=self.now,
                )
                self.assertEqual(allowed["status"], "VALIDATED")
                self.assertEqual(allowed["route_gate_branch"], "lab/authorized-change")

    def test_observe_intent_cannot_expose_mutation_function(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0]["connection_method"] = "gscc-controlled-host-gateway"
        sessions["sessions"][0]["surface_class"] = "CONTROLLED_INSTRUMENTABLE"
        sessions["sessions"][0]["entry_action"] = "CONTINUE_GOVERNED_WORK"
        sessions["sessions"][0]["connection_intent"] = "OBSERVE"

        denied = evaluate_function_exposure(
            tool_name="write_tool",
            connection_ref=self.connection_ref,
            requested_head=self.head,
            access_grant=self.access_grant(
                allowed_authority_classes=["EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED"]
            ),
            authority_evidence=self.evidence(
                "EXPLICIT_SCOPED_MUTATION_AUTHORITY_REQUIRED",
                preflight={
                    "status": "PASSED",
                    "observed_head": self.head,
                    "evidence_ref": "preflight:fixture",
                },
            ),
            snapshot=self.snapshot,
            sessions=sessions,
            current_repository_head=self.head,
            now=self.now,
        )
        self.assertEqual(denied["status"], "DENIED")
        self.assertEqual(denied["reason_code"], "CONNECTION_INTENT_POLICY_FORBIDS_MUTATION")

    def test_portable_capability_projection_is_minimal(self):
        source = {
            "status": "CURRENT",
            "authority_id": "CP-MCP-CAP-001",
            "observed_at": "2026-10-05T00:00:00+00:00",
            "endpoint": "https://secret-ish.example.invalid/mcp",
            "servers": {"s1": {"protected_domains": ["example.invalid"]}},
            "refresh_policy": {"pre_mutation_live_refresh_required": True},
            "catalogue": {
                "status": "CURRENT",
                "catalogue_digest": "d" * 64,
                "tools": [{"name": "read_tool", "surface": "read"}],
            },
        }
        projected = build_portable_capability_projection(source)
        self.assertEqual(projected["scope"], "PORTABLE_CLIENT_PROJECTION")
        self.assertEqual(projected["catalogue"]["tools"][0]["name"], "read_tool")
        self.assertTrue(projected["refresh_policy"]["pre_mutation_live_refresh_required"])
        self.assertNotIn("endpoint", projected)
        self.assertNotIn("servers", projected)

    def test_default_snapshot_follows_source_client_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".governance").mkdir(parents=True)

            with patch.object(exposure_gate, "ROOT", root):
                self.assertEqual(
                    exposure_gate._default_snapshot_path(),
                    root / ".governance" / "gscc" / "mcp-capability-snapshot.json",
                )

            (root / ".template-source").write_text("", encoding="utf-8")
            with patch.object(exposure_gate, "ROOT", root):
                self.assertEqual(
                    exposure_gate._default_snapshot_path(),
                    root / ".governance" / "control-plane-state" / "mcp-capability-snapshot.json",
                )

    def test_default_session_store_follows_source_client_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            governance = root / ".governance"
            governance.mkdir(parents=True)
            with patch.object(exposure_gate, "ROOT", root):
                self.assertEqual(
                    exposure_gate._default_sessions_path(),
                    root / ".governance" / "sessions" / "sessions.json",
                )

            (root / ".template-source").write_text("", encoding="utf-8")
            with patch.object(exposure_gate, "ROOT", root):
                self.assertEqual(
                    exposure_gate._default_sessions_path(),
                    root / ".governance" / "control-plane-state" / "gacr-sessions.json",
                )

    def test_exposure_issue_ingress_is_repository_local_and_fail_closed(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("github.event.issue.number == 161", text)
        self.assertNotIn("--expected-issue-number 161", text)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = root / ".governance" / "agent-relay"
            cfg.mkdir(parents=True)
            (cfg / "config.json").write_text(
                json.dumps({"gscc_function_exposure_gate": {"issue_number": None}}),
                encoding="utf-8",
            )
            with patch.object(exposure_gate, "ROOT", root):
                with self.assertRaisesRegex(RuntimeError, "FUNCTION_EXPOSURE_ISSUE_NOT_CONFIGURED"):
                    exposure_gate._configured_function_exposure_issue_number()

    def test_private_repository_canonical_checkout_does_not_require_persisted_credentials(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        package_job = text.split("  package-evaluate:", 1)[1].split("  evaluate:", 1)[0]
        evaluate_job = text.split("  evaluate:", 1)[1]
        for name, job in [("package-evaluate", package_job), ("evaluate", evaluate_job)]:
            with self.subTest(job=name):
                self.assertNotIn('git fetch origin "refs/heads/$canonical"', job)
                self.assertIn("id: canonical", job)
                self.assertIn('ref: ${{ steps.canonical.outputs.branch }}', job)
                self.assertIn("persist-credentials: false", job)

    def test_exposure_workflow_has_no_canonical_main_hardcoding(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("ref: main", text)
        self.assertNotIn("refs/heads/main", text)
        self.assertNotIn("GSCC_FUNCTION_GATE_REQUIRES_CANONICAL_MAIN", text)
        self.assertIn("CANONICAL_BRANCH", text)
        self.assertIn("canonical-branch", text)

    def test_remote_head_reobservation_uses_bound_session_branch_for_lab(self):
        sessions = json.loads(json.dumps(self.sessions))
        sessions["sessions"][0].update({
            "connection_method": "controlled-client-adapter",
            "surface_class": "CONTROLLED_INSTRUMENTABLE",
            "entry_action": "LAB_EVOLUTION",
            "connection_intent": "CODE_CHANGE",
            "branch": "lab/authorized-change",
        })
        observed_calls = []

        class Proc:
            returncode = 0
            stdout = ("c" * 40) + "\trefs/heads/lab/authorized-change\n"
            stderr = ""

        def fake_run(args, **kwargs):
            observed_calls.append(list(args))
            return Proc()

        with patch.object(exposure_gate.subprocess, "run", fake_run):
            observed = exposure_gate._git_remote_session_head(
                sessions,
                self.connection_ref,
                now=self.now,
            )

        self.assertEqual(observed, "c" * 40)
        self.assertEqual(
            observed_calls,
            [["git", "ls-remote", "--exit-code", "origin", "refs/heads/lab/authorized-change"]],
        )

    def test_remote_head_reobservation_uses_instantiated_canonical_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            governance = root / ".governance"
            governance.mkdir(parents=True)
            (governance / "profile.json").write_text(
                json.dumps({
                    "template_source": False,
                    "initialized": True,
                    "canonical_branch": "trunk",
                }),
                encoding="utf-8",
            )

            observed_calls = []

            class Proc:
                returncode = 0
                stdout = ("b" * 40) + "\trefs/heads/trunk\n"
                stderr = ""

            def fake_run(args, **kwargs):
                observed_calls.append(list(args))
                return Proc()

            with patch.object(exposure_gate, "ROOT", root), patch.object(exposure_gate.subprocess, "run", fake_run):
                self.assertEqual(exposure_gate._canonical_branch(), "trunk")
                self.assertEqual(exposure_gate._git_remote_canonical_head(), "b" * 40)

            self.assertEqual(
                observed_calls,
                [["git", "ls-remote", "--exit-code", "origin", "refs/heads/trunk"]],
            )

    def test_workflow_is_mandatory_and_fail_closed(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("gscc_function_exposure_request", text)
        self.assertIn("/gscc-function-exposure ", text)
        self.assertIn("issue_comment", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("python3 scripts/gscc_function_exposure_gate.py evaluate", text)
        self.assertIn("access_grant_json", text)
        self.assertIn("ACCESS_GRANT_JSON", text)
        self.assertIn("python3 scripts/gscc_function_exposure_gate.py arrival-plan", text)
        self.assertIn("actions/upload-artifact@v4", text)
        self.assertNotIn("continue-on-error: true", text)
        source = (ROOT / "scripts" / "gscc_function_exposure_gate.py").read_text(encoding="utf-8")
        self.assertIn('"ls-remote"', source)
        self.assertIn("def _canonical_branch", source)
        self.assertIn('"refs/heads/{branch}"', source)


if __name__ == "__main__":
    unittest.main(verbosity=2)