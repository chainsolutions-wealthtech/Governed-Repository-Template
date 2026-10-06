#!/usr/bin/env python3
from __future__ import annotations

import unittest

from provider_first_touch_repository_enrichment import enrich_envelope
from provider_first_touch_ingress import build_capture

REPO="chainsolutions-wealthtech/Governed-Repository-Template"
HEAD="1234567890abcdef1234567890abcdef12345678"

def fake_request(url, token):
    if url.endswith("/repos/chainsolutions-wealthtech/Governed-Repository-Template"):
        return 200, {
            "id":1386478935,
            "node_id":"R_kgDUMMY",
            "name":"Governed-Repository-Template",
            "full_name":REPO,
            "owner":{"login":"chainsolutions-wealthtech","id":299685687,"type":"Organization"},
            "visibility":"public",
            "private":False,
            "archived":False,
            "fork":False,
            "default_branch":"main",
            "size":5627,
            "html_url":"https://github.com/"+REPO,
            "clone_url":"https://github.com/"+REPO+".git",
            "git_url":"git://github.com/"+REPO+".git",
            "url":"https://api.github.com/repos/"+REPO,
            "commits_url":"https://api.github.com/repos/"+REPO+"/commits{/sha}",
            "git_refs_url":"https://api.github.com/repos/"+REPO+"/git/refs{/sha}",
            "created_at":"2026-01-01T00:00:00Z",
            "updated_at":"2026-10-06T06:00:00Z",
            "pushed_at":"2026-10-06T06:00:00Z",
            "language":"Python",
            "topics":["governance"],
            "description":"Governed repository",
            "is_template":True,
            "permissions":{"admin":True,"maintain":True,"push":True,"pull":True,"triage":True},
        }
    if "/branches/main" in url:
        return 200, {"name":"main","protected":True,"commit":{"sha":HEAD}}
    if "/commits/"+HEAD in url:
        return 200, {
            "sha":HEAD,
            "html_url":"https://github.com/"+REPO+"/commit/"+HEAD,
            "url":"https://api.github.com/repos/"+REPO+"/commits/"+HEAD,
            "commit":{
                "message":"test commit",
                "author":{"name":"Author","email":"author@example.com","date":"2026-10-06T06:00:00Z"},
                "committer":{"name":"Committer","email":"committer@example.com","date":"2026-10-06T06:00:01Z"},
                "tree":{"sha":"a"*40,"url":"https://api.github.com/tree"},
                "comment_count":0,
                "verification":{"verified":True,"reason":"valid"},
            },
            "parents":[{"sha":"b"*40}],
            "stats":{"additions":10,"deletions":2},
            "files":[{"filename":"x.py"}],
        }
    if "/actions/workflows?" in url:
        return 200, {"total_count":1,"workflows":[{"id":376067150,"name":"GSCC Provider First Touch Ingress","path":".github/workflows/gscc-provider-first-touch-ingress.yml","state":"active"}]}
    if "/actions/runs?" in url:
        return 200, {"workflow_runs":[{"id":1,"workflow_id":376067150,"name":"GSCC Provider First Touch Ingress","event":"repository_dispatch","status":"completed","conclusion":"success","head_branch":"main","head_sha":HEAD,"run_number":1,"run_attempt":1,"created_at":"2026-10-06T06:00:02Z","updated_at":"2026-10-06T06:00:03Z"}]}
    return 404, {"message":"not found"}

class RepositoryEnrichmentTests(unittest.TestCase):
    def test_minimal_signal_is_enriched_by_repository(self):
        minimal={
            "schema":"gscc-provider-first-touch-envelope/v1",
            "provider":"chatgpt",
            "transport":"chatgpt-github-direct",
            "repository":REPO,
            "identity":{
                "conversation_ref":"UNAVAILABLE",
                "session_ref":"UNAVAILABLE",
                "connection_ref":"UNAVAILABLE",
            },
            "tool":{"name":"get_repo","operation":"read_repository","category":"READ","success":True},
            "direct_github_functions_used":True,
            "repository_mutated":False,
            "token_exposed":False,
        }
        enriched=enrich_envelope(minimal,"test-token",observed_at="2026-10-06T06:00:04+00:00",request_fn=fake_request)
        self.assertEqual(enriched["repository_id"],1386478935)
        self.assertEqual(enriched["default_branch"],"main")
        self.assertEqual(enriched["observed_head"],HEAD)
        self.assertTrue(enriched["permissions"]["admin"])
        self.assertEqual(enriched["git"]["head"],HEAD)
        self.assertEqual(enriched["commit"]["sha"],HEAD)
        self.assertEqual(enriched["tree"]["sha"],"a"*40)
        self.assertEqual(enriched["workflow"]["run_id"],1)
        self.assertFalse(enriched["repository_enrichment"]["mutation_authority_granted"])

        capture=build_capture(enriched,observed_at="2026-10-06T06:00:04+00:00")
        rows={row["field_id"]:row for row in capture["field_evidence"]}
        self.assertEqual(rows["repository.id"]["status"],"OBSERVED")
        self.assertEqual(rows["repository.visibility"]["value"],"public")
        self.assertEqual(rows["permissions.admin"]["value"],True)
        self.assertEqual(rows["git.head"]["value"],HEAD)
        self.assertEqual(rows["commit.sha"]["value"],HEAD)
        self.assertEqual(rows["tree.sha"]["value"],"a"*40)
        self.assertEqual(rows["workflow.run_id"]["value"],1)
        self.assertEqual(rows["session.conversation_ref"]["status"],"UNAVAILABLE")
        self.assertEqual(capture["safe_ingress"]["status"],"INVALID")

if __name__=="__main__":
    unittest.main()
