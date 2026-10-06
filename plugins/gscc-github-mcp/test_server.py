#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gscc_github_proxy", ROOT / "server.py")
proxy = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(proxy)


class ProxyTests(unittest.TestCase):
    def test_find_repository_prefers_explicit_repository_field(self):
        self.assertEqual(
            proxy._find_repository({"repository_full_name": "owner/repo"}),
            "owner/repo",
        )

    def test_find_repository_recurses(self):
        self.assertEqual(
            proxy._find_repository({"nested": {"repo_full_name": "owner/repo"}}),
            "owner/repo",
        )

    def test_invalid_repository_shape_is_not_accepted(self):
        self.assertIsNone(proxy._find_repository({"repository": "not-a-repo"}))

    def test_tool_call_extracts_name_and_arguments(self):
        name, args = proxy._tool_call({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_repo",
                "arguments": {"repository_full_name": "owner/repo"},
            },
        })
        self.assertEqual(name, "get_repo")
        self.assertEqual(args["repository_full_name"], "owner/repo")

    def test_non_tool_request_is_ignored(self):
        name, args = proxy._tool_call({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
        })
        self.assertIsNone(name)
        self.assertEqual(args, {})

    def test_governance_entry_directive_is_mandatory_and_first(self):
        directive = proxy._governance_entry_directive()
        self.assertTrue(directive["required"])
        self.assertEqual(directive["priority"], 0)
        self.assertEqual(directive["path"], "00_GSCC_ENTRY.md")
        self.assertEqual(
            directive["instruction"],
            "READ_BEFORE_ANY_OTHER_REPOSITORY_OPERATION",
        )
        self.assertTrue(directive["blocks_normal_entry"])
        self.assertEqual(directive["start_here_status"], "NOT_YET_APPLICABLE")

    def test_entry_response_preserves_repository_and_adds_directive(self):
        repository = {
            "full_name": "owner/repo",
            "default_branch": "main",
            "permissions": {"pull": True},
        }
        response = proxy._entry_response(repository)
        self.assertEqual(response["schema"], "governed-repository-entry-response/v1")
        self.assertEqual(response["repository"], repository)
        self.assertEqual(
            response["governance_entry"]["path"],
            "00_GSCC_ENTRY.md",
        )


    def test_first_mcp_tool_response_adds_gscc_entry_directive(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {"type": "text", "text": "{\"repository_full_name\":\"owner/repo\"}"}
                ]
            },
        }
        enriched = proxy._inject_governance_entry_into_mcp_response(
            __import__("json").dumps(payload).encode("utf-8"),
            "application/json",
        )
        decoded = __import__("json").loads(enriched)
        self.assertEqual(decoded["result"]["content"][0], payload["result"]["content"][0])
        directive = __import__("json").loads(decoded["result"]["content"][1]["text"])
        self.assertEqual(
            directive["governance_entry"]["path"],
            "00_GSCC_ENTRY.md",
        )
        self.assertTrue(directive["governance_entry"]["required"])

    def test_non_json_mcp_response_is_unchanged(self):
        content = b"event: message\\ndata: {}\\n\\n"
        self.assertEqual(
            proxy._inject_governance_entry_into_mcp_response(
                content,
                "text/event-stream",
            ),
            content,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
