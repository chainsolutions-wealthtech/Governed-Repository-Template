#!/usr/bin/env python3
from __future__ import annotations

import unittest

from chatgpt_github_surface_instrumentation import (
    PLUGIN_PREFIX,
    canonical_github_tool_names,
    instrument_github_plugin_surface,
    instrument_github_plugin_surface_with_first_touch,
)
from gscc import InMemoryTransport, SessionEndpoint


class GitHubPluginSurfaceInstrumentationTests(unittest.TestCase):
    def endpoint(self):
        transport = InMemoryTransport()
        endpoint = SessionEndpoint(
            transport,
            source={"provider": "chatgpt", "client_instance_id": "UNAVAILABLE"},
            target={"system": "gscc"},
            scope={"repository": "chainsolutions-wealthtech/Governed-Repository-Template"},
        )
        return endpoint, transport

    def test_snapshot_declares_89_unique_tools(self):
        names = canonical_github_tool_names()
        self.assertEqual(len(names), 89)
        self.assertEqual(len(names), len(set(names)))
        self.assertIn("get_repo", names)
        self.assertIn("fetch_file", names)
        self.assertIn("search_commits", names)
        self.assertIn("create_pull_request", names)

    def test_complete_runtime_surface_is_fully_wrapped(self):
        names = canonical_github_tool_names()
        calls = []
        before = []

        def make_tool(name):
            def tool(*args, **kwargs):
                calls.append((name, args, kwargs))
                return {"tool": name}
            return tool

        runtime = {
            f"{PLUGIN_PREFIX}{name}": make_tool(name)
            for name in names
        }
        endpoint, transport = self.endpoint()
        wrapped = instrument_github_plugin_surface(
            endpoint,
            runtime,
            before_tool_call=lambda tool_name: before.append(tool_name) or {"status": "OK"},
        )

        self.assertEqual(len(wrapped), 89)
        for name in ("get_repo", "fetch_file", "search_commits", "create_pull_request"):
            full = f"{PLUGIN_PREFIX}{name}"
            result = wrapped[full]()
            self.assertEqual(result["tool"], name)

        self.assertEqual(
            before,
            [
                f"{PLUGIN_PREFIX}get_repo",
                f"{PLUGIN_PREFIX}fetch_file",
                f"{PLUGIN_PREFIX}search_commits",
                f"{PLUGIN_PREFIX}create_pull_request",
            ],
        )
        event_types = [message.type for message in transport.sent]
        self.assertEqual(event_types.count("TOOL_STARTED"), 4)
        self.assertEqual(event_types.count("TOOL_COMPLETED"), 4)

    def test_short_runtime_names_are_supported(self):
        endpoint, _ = self.endpoint()
        runtime = {"get_repo": lambda: "ok"}
        wrapped = instrument_github_plugin_surface(
            endpoint,
            runtime,
            require_complete_surface=False,
        )
        self.assertEqual(wrapped["get_repo"](), "ok")

    def test_complete_surface_fails_closed_when_any_snapshot_tool_is_missing(self):
        names = canonical_github_tool_names()
        runtime = {
            f"{PLUGIN_PREFIX}{name}": (lambda name=name: name)
            for name in names
            if name != "get_repo"
        }
        endpoint, _ = self.endpoint()
        with self.assertRaisesRegex(ValueError, "surface incomplete"):
            instrument_github_plugin_surface(endpoint, runtime)



    def test_first_touch_is_emitted_once_across_multiple_surface_functions(self):
        endpoint, _ = self.endpoint()
        runtime = {
            "get_repo": lambda: {"ok": "repo"},
            "fetch_file": lambda: {"ok": "file"},
            "search_commits": lambda: {"ok": "commits"},
        }
        dispatches = []

        def dispatch(repository, envelope, token):
            dispatches.append((repository, envelope["tool"]["name"], envelope["provider_context"]))
            return 204

        wrapped = instrument_github_plugin_surface_with_first_touch(
            endpoint,
            runtime,
            event_base={
                "provider": "chatgpt",
                "transport": "chatgpt-github-plugin",
                "repository": "chainsolutions-wealthtech/Governed-Repository-Template",
                "identity": {
                    "conversation_ref": "UNAVAILABLE",
                    "session_ref": "UNAVAILABLE",
                    "connection_ref": "UNAVAILABLE",
                },
            },
            token="test",
            dispatch_fn=dispatch,
            require_complete_surface=False,
        )

        wrapped["get_repo"]()
        wrapped["fetch_file"]()
        wrapped["search_commits"]()

        self.assertEqual(len(dispatches), 1)
        self.assertEqual(dispatches[0][1], "mcp__GitHub__get_repo")
        self.assertEqual(dispatches[0][2]["agent"]["provider"], "chatgpt")
        self.assertEqual(
            dispatches[0][2]["session"]["conversation_ref"],
            "UNAVAILABLE",
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)
