#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from governed_github_read_connector import GovernedGitHubReadConnector

REPO="chainsolutions-wealthtech/Governed-Repository-Template"

class GovernedGitHubReadConnectorTests(unittest.TestCase):
    def setUp(self):
        self.dispatches=[]
        self.requests=[]

    def dispatch(self, repository, envelope, token):
        self.dispatches.append((repository,envelope,token))
        return 204

    def request(self, url, token):
        self.requests.append((url,token))
        if "/contents/" in url:
            return 200, {"type":"file","path":"README.md","content":"UkVBRE1F"}
        return 200, {
            "id":1386478935,
            "full_name":REPO,
            "default_branch":"main",
        }

    def make(self, **kwargs):
        return GovernedGitHubReadConnector(
            repository=REPO,
            token="test-token",
            request_fn=self.request,
            dispatch_fn=self.dispatch,
            **kwargs,
        )

    def test_get_repo_emits_first_touch_before_read(self):
        c=self.make(identity={"connection_ref":"conn-1"})
        result=c.get_repo()
        self.assertEqual(len(self.dispatches),1)
        self.assertEqual(len(self.requests),1)
        self.assertEqual(self.dispatches[0][1]["tool"]["name"],"get_repo")
        self.assertEqual(result["first_touch"]["status"],"FIRST_TOUCH_EMITTED")

    def test_fetch_file_can_be_the_first_touch(self):
        c=self.make(identity={"connection_ref":"conn-2"})
        result=c.fetch_file("README.md",ref="main")
        self.assertEqual(len(self.dispatches),1)
        self.assertEqual(len(self.requests),1)
        self.assertEqual(self.dispatches[0][1]["tool"]["name"],"fetch_file")
        self.assertEqual(result["first_touch"]["status"],"FIRST_TOUCH_EMITTED")

    def test_second_read_does_not_emit_second_first_touch(self):
        c=self.make(identity={"connection_ref":"conn-3"})
        c.get_repo()
        second=c.fetch_file("README.md")
        self.assertEqual(len(self.dispatches),1)
        self.assertEqual(len(self.requests),2)
        self.assertEqual(second["first_touch"]["status"],"FIRST_TOUCH_ALREADY_EMITTED")

    def test_unresolved_identity_still_emits_only_once_per_connector_session(self):
        c=self.make(identity={
            "conversation_ref":"UNAVAILABLE",
            "session_ref":"UNAVAILABLE",
            "connection_ref":"UNAVAILABLE",
        })
        c.get_repo()
        c.fetch_file("README.md")
        self.assertEqual(len(self.dispatches),1)
        self.assertEqual(self.dispatches[0][1]["identity_status"],"UNRESOLVED")

    def test_state_file_preserves_first_touch_idempotence(self):
        with tempfile.TemporaryDirectory() as td:
            state=str(Path(td)/"state.json")
            c1=self.make(identity={"connection_ref":"conn-4"},state_file=state)
            c1.get_repo()
            c2=self.make(identity={"connection_ref":"conn-4"},state_file=state)
            second=c2.fetch_file("README.md")
            self.assertEqual(len(self.dispatches),1)
            self.assertEqual(second["first_touch"]["status"],"FIRST_TOUCH_ALREADY_EMITTED")

if __name__=="__main__":
    unittest.main()
