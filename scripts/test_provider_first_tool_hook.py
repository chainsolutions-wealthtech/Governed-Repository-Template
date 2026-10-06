#!/usr/bin/env python3
from __future__ import annotations
import unittest

from provider_first_tool_hook import FirstToolHook, FirstTouchBeforeToolCall, build_envelope

def event():
    return {
        "provider":"chatgpt",
        "transport":"chatgpt-github-direct",
        "repository":"chainsolutions-wealthtech/Governed-Repository-Template",
        "actor":"Wealthtechinnovations",
        "model":"GPT-5.6 Sol",
        "branch":"main",
        "observed_head":"a"*40,
        "identity":{
            "conversation_ref":"UNAVAILABLE",
            "session_ref":"UNAVAILABLE",
            "connection_ref":"conn_ft_test_12345678",
        },
        "tool_name":"mcp__GitHub__get_repo",
        "operation":"read_repository",
        "category":"READ",
        "success":True,
    }

class ProviderFirstToolHookTests(unittest.TestCase):
    def test_build_envelope(self):
        env=build_envelope(event())
        self.assertEqual(env["schema"],"gscc-provider-first-touch-envelope/v1")
        self.assertEqual(env["provider"],"chatgpt")
        self.assertEqual(env["identity"]["connection_ref"],"conn_ft_test_12345678")
        self.assertTrue(env["direct_github_functions_used"])
        self.assertFalse(env["codex_used"])

    def test_exactly_once_per_host_marker(self):
        calls=[]
        def dispatch(repository,envelope,token):
            calls.append((repository,envelope,token))
            return 204
        hook=FirstToolHook({})
        first=hook.maybe_emit_first_touch(event(),token="test",dispatch_fn=dispatch)
        second=hook.maybe_emit_first_touch(event(),token="test",dispatch_fn=dispatch)
        self.assertEqual(first["status"],"FIRST_TOUCH_EMITTED")
        self.assertEqual(second["status"],"FIRST_TOUCH_ALREADY_EMITTED")
        self.assertEqual(len(calls),1)

    def test_distinct_connection_ref_emits_distinct_first_touch(self):
        calls=[]
        def dispatch(repository,envelope,token):
            calls.append(envelope["identity"]["connection_ref"])
            return 204
        hook=FirstToolHook({})
        one=event()
        two=event()
        two["identity"]["connection_ref"]="conn_ft_test_87654321"
        hook.maybe_emit_first_touch(one,token="test",dispatch_fn=dispatch)
        hook.maybe_emit_first_touch(two,token="test",dispatch_fn=dispatch)
        self.assertEqual(len(calls),2)

    def test_missing_stable_identity_still_emits_capture_signal(self):
        value=event()
        value["identity"]={
            "conversation_ref":"UNAVAILABLE",
            "session_ref":"UNAVAILABLE",
            "connection_ref":"UNAVAILABLE",
        }
        value["first_tool_call"]=True
        calls=[]
        def dispatch(repository,envelope,token):
            calls.append(envelope)
            return 204
        hook=FirstToolHook({})
        result=hook.maybe_emit_first_touch(value,token="test",dispatch_fn=dispatch)
        self.assertEqual(result["status"],"FIRST_TOUCH_EMITTED")
        self.assertEqual(result["marker"],"UNRESOLVED")
        self.assertEqual(result["envelope"]["identity_status"],"UNRESOLVED")
        self.assertEqual(len(calls),1)

    def test_non_first_tool_call_does_not_emit(self):
        value=event()
        value["first_tool_call"]=False
        calls=[]
        def dispatch(repository,envelope,token):
            calls.append(envelope)
            return 204
        hook=FirstToolHook({})
        result=hook.maybe_emit_first_touch(value,token="test",dispatch_fn=dispatch)
        self.assertEqual(result["status"],"NOT_FIRST_TOOL_CALL")
        self.assertEqual(calls,[])


    def test_generic_before_tool_adapter_emits_only_once_for_any_tool(self):
        calls=[]
        def dispatch(repository,envelope,token):
            calls.append(envelope["tool"]["name"])
            return 204
        adapter=FirstTouchBeforeToolCall(
            event_base={
                "provider":"chatgpt",
                "transport":"chatgpt-github-direct",
                "repository":"chainsolutions-wealthtech/Governed-Repository-Template",
                "identity":{
                    "conversation_ref":"UNAVAILABLE",
                    "session_ref":"UNAVAILABLE",
                    "connection_ref":"conn-generic-1",
                },
            },
            token="test",
            dispatch_fn=dispatch,
        )
        first=adapter("mcp__GitHub__get_repo")
        second=adapter("mcp__GitHub__fetch_file")
        third=adapter("mcp__GitHub__search_commits")
        self.assertEqual(first["status"],"FIRST_TOUCH_EMITTED")
        self.assertEqual(second["status"],"FIRST_TOUCH_ALREADY_EMITTED")
        self.assertEqual(third["status"],"FIRST_TOUCH_ALREADY_EMITTED")
        self.assertEqual(calls,["mcp__GitHub__get_repo"])

if __name__=="__main__":
    unittest.main()
