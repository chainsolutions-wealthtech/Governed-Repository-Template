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


if __name__ == "__main__":
    unittest.main(verbosity=2)
