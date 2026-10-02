#!/usr/bin/env python3
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from gscc.entry_gate import (
    ENTRY_REQUIRED_GET_FIELDS,
    ENTRY_REQUIRED_POST_FIELDS,
    complete_entry_context,
)


class EntryContextGateTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 2, 8, 0, tzinfo=timezone.utc)
        self.post_data = {
            "provider": "chatgpt",
            "agent_identity": "conversation-agent",
            "client_instance_id": "client-a",
            "connection_ref": "gscc-controlled:owner/repo:client-a",
            "connection_method": "gscc-controlled-host-gateway",
            "surface_class": "CONTROLLED_INSTRUMENTABLE",
            "function_surface": ["github"],
            "capabilities": {
                "functions": ["github.fetch_file"],
                "control": ["COMMAND_RECEIVE", "COMMAND_ACK"],
            },
        }
        self.get_data = {
            "repository": "owner/repo",
            "repository_owner": "owner",
            "repository_name": "repo",
            "default_branch": "main",
            "requested_ref": "main",
            "observed_head_sha": "a" * 40,
        }

    def test_contract_has_required_post_and_get_surfaces(self):
        self.assertIn("provider", ENTRY_REQUIRED_POST_FIELDS)
        self.assertIn("connection_ref", ENTRY_REQUIRED_POST_FIELDS)
        self.assertIn("capabilities", ENTRY_REQUIRED_POST_FIELDS)
        self.assertIn("repository", ENTRY_REQUIRED_GET_FIELDS)
        self.assertIn("observed_head_sha", ENTRY_REQUIRED_GET_FIELDS)

    def test_post_plus_get_opens_entry_only_when_complete(self):
        receipt = complete_entry_context(
            post_data=self.post_data,
            get_data=self.get_data,
            observed_at=self.now,
        )
        self.assertEqual(receipt["status"], "ENTRY_CONTEXT_OPEN")
        self.assertTrue(receipt["entry_open"])
        self.assertEqual(receipt["missing_required"], [])
        self.assertTrue(receipt["entry_receipt"].startswith("GSCC-ENTRY-"))
        self.assertEqual(receipt["fields"]["provider"]["source_method"], "POST")
        self.assertEqual(receipt["fields"]["repository"]["source_method"], "GET")
        self.assertEqual(receipt["fields"]["observed_head_sha"]["value"], "a" * 40)

    def test_missing_required_get_fact_keeps_repository_entry_closed(self):
        get_data = dict(self.get_data)
        get_data.pop("observed_head_sha")
        receipt = complete_entry_context(
            post_data=self.post_data,
            get_data=get_data,
            observed_at=self.now,
        )
        self.assertEqual(receipt["status"], "ENTRY_CONTEXT_CLOSED")
        self.assertFalse(receipt["entry_open"])
        self.assertIn("observed_head_sha", receipt["missing_required"])
        self.assertIsNone(receipt["entry_receipt"])

    def test_missing_required_post_fact_keeps_repository_entry_closed(self):
        post_data = dict(self.post_data)
        post_data.pop("client_instance_id")
        receipt = complete_entry_context(
            post_data=post_data,
            get_data=self.get_data,
            observed_at=self.now,
        )
        self.assertFalse(receipt["entry_open"])
        self.assertIn("client_instance_id", receipt["missing_required"])

    def test_optional_provider_private_fact_may_be_explicitly_unavailable(self):
        post_data = dict(self.post_data)
        post_data["unavailable"] = {
            "conversation_ref": "NOT_EXPOSED_BY_PROVIDER",
            "browser_metadata": "NOT_EXPOSED_BY_HOST",
        }
        receipt = complete_entry_context(
            post_data=post_data,
            get_data=self.get_data,
            observed_at=self.now,
        )
        self.assertTrue(receipt["entry_open"])
        self.assertEqual(
            receipt["unavailable"]["conversation_ref"]["reason"],
            "NOT_EXPOSED_BY_PROVIDER",
        )

    def test_secret_bearing_payload_is_rejected(self):
        post_data = dict(self.post_data)
        post_data["access_token"] = "not-allowed"
        with self.assertRaises(ValueError):
            complete_entry_context(
                post_data=post_data,
                get_data=self.get_data,
                observed_at=self.now,
            )

    def test_get_wins_for_repository_verification_fields(self):
        post_data = dict(self.post_data)
        post_data["repository"] = "attacker/other"
        receipt = complete_entry_context(
            post_data=post_data,
            get_data=self.get_data,
            observed_at=self.now,
        )
        self.assertEqual(receipt["fields"]["repository"]["value"], "owner/repo")
        self.assertEqual(receipt["fields"]["repository"]["source_method"], "GET")

    def test_receipt_never_grants_invocation_or_mutation_authority(self):
        receipt = complete_entry_context(
            post_data=self.post_data,
            get_data=self.get_data,
            observed_at=self.now,
        )
        self.assertFalse(receipt["invocation_authority_granted"])
        self.assertFalse(receipt["mutation_authority_granted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
