#!/usr/bin/env python3
"""Negative and happy-path LAB entry tests; fake native API, no GitHub writes."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab_entry_bootstrap as lab

REPO = "chainsolutions-wealthtech/Governed-Repository-Template"
HEAD = "a" * 40
TIME = "2026-10-17T00:00:00+00:00"


class FakeAPI:
    def __init__(self):
        self.head = None
        self.issue = None
        self.commits = 0
        self.prs = 0
        self.ci = 0

    def commit(self, repo, branch, parent, files, message):
        api = lab.API.__new__(lab.API)
        api.req = self.req
        return lab.API.commit(api, repo, branch, parent, files, message)

    def req(self, method, route, data=None, missing_ok=False):
        prefix = "/repos/" + REPO
        if method == "GET" and route == prefix:
            return {"full_name": REPO, "default_branch": "main"}
        if method == "GET" and route == prefix + "/commits/main":
            return {"sha": HEAD}
        if method == "GET" and route.startswith(prefix + "/git/ref/heads/"):
            return {"object": {"sha": self.head}} if self.head else None
        if method == "GET" and route.startswith(prefix + "/issues?"):
            return [self.issue] if self.issue else []
        if method == "POST" and route == prefix + "/issues":
            self.issue = {"number": 450, "title": data["title"], "body": data["body"], "state": "open"}
            return self.issue
        if method == "POST" and route == prefix + "/git/refs":
            self.head = data["sha"]
            return {}
        if method == "GET" and route.startswith(prefix + "/git/commits/"):
            return {"tree": {"sha": "f" * 40}}
        if method == "POST" and route == prefix + "/git/trees":
            assert len(data["tree"]) in (1, 4)
            return {"sha": "d" * 40}
        if method == "POST" and route == prefix + "/git/commits":
            self.commits += 1
            return {"sha": ("b" if self.commits == 1 else "c") * 40}
        if method == "PATCH" and route.startswith(prefix + "/git/refs/heads/"):
            assert data["force"] is False
            self.head = data["sha"]
            return {}
        if method == "POST" and route == prefix + "/pulls":
            assert data["draft"] is True
            self.prs += 1
            return {"number": 451}
        if method == "PATCH" and route == prefix + "/issues/450":
            self.issue["body"] = data["body"]
            return {}
        if method == "POST" and route == prefix + "/actions/workflows/governance-ci.yml/dispatches":
            self.ci += 1
            return {}
        raise AssertionError("Unexpected GitHub request: " + method + " " + route)


class LabEntryTests(unittest.TestCase):
    def test_ids_and_bad_inputs(self):
        ids = lab.ids("lab-context-demo", "Create a canonical LAB framework")
        self.assertEqual(ids["continuity_id"], "GRT-CONT-LAB-LAB_CONTEXT_DEMO")
        self.assertEqual(ids["pool_id"], "GRT-POOL-LAB-LAB_CONTEXT_DEMO")
        self.assertNotEqual(ids["pool_id"], ids["continuity_id"])
        for s in ("", "../foo", "Bad-Slug", "x", "name/next", "épreuve"):
            with self.assertRaises(lab.LabEntryError):
                lab.ids(s, "A valid objective string")
        with self.assertRaises(lab.LabEntryError):
            lab.ids("good-slug", "short")

    def test_package_pool_queue_and_memory(self):
        files = lab.package("sample-lab", "A testable lab with durable registry", "Wealthtechinnovations",
                            REPO, HEAD, 450, TIME)
        self.assertEqual(len(files), 4)
        pool = json.loads(next(v for k, v in files.items() if k.endswith("POOL.json")))
        queue = json.loads(next(v for k, v in files.items() if k.endswith("QUEUE.json")))
        register = json.loads(next(v for k, v in files.items() if k.endswith("REGISTRY.json")))
        self.assertEqual(len(pool["members"]), 4)
        self.assertTrue(all(m["status"] == "VACANT" and m["session_id"] is None for m in pool["members"]))
        self.assertTrue(all(m["can_propose_code_change"] for m in pool["members"]))
        binding = pool["gacr_link_contract"]
        self.assertEqual(binding["status"], "REQUIRED_NOT_YET_ATTESTED")
        self.assertEqual(binding["pool_id"], pool["pool_id"])
        self.assertIsNone(binding["gacr_continuity_id"])
        self.assertIsNone(binding["gacr_logical_agent_id"])
        self.assertIsNone(binding["gacr_session_id"])
        self.assertTrue(binding["no_synthetic_gacr_ids"])
        self.assertTrue(binding["membership_not_inferred_from_github_actor"])

        self.assertEqual(len(queue["tasks"]), 11)
        self.assertFalse(queue["authorizes_dispatch"])
        self.assertFalse(queue["authorizes_claim"])
        self.assertTrue(queue["projection_only"])
        self.assertFalse(queue["separate_authoritative_queue_created"])
        self.assertFalse(queue["initial_lab_setup_requires_gacr_claim"])
        self.assertFalse(queue["initial_lab_setup_requires_gacr_offer"])
        self.assertTrue(queue["claim_required_when_real_canonical_task_dispatched"])
        self.assertTrue(all(t["dispatch_release"] == "NOT_RELEASED" for t in queue["tasks"]))
        self.assertEqual(register["session_continuity_links"], [])
        self.assertEqual(register["gacr_sessions"], [])
        self.assertEqual(len(register["chronology"]), 4)
        new = lab.link_pr(next(v for k, v in files.items() if k.endswith("REGISTRY.json")), 451, HEAD, TIME)
        self.assertEqual(json.loads(new)["pr_number"], 451)
        with self.assertRaises(lab.LabEntryError):
            lab.link_pr(new, 452, HEAD, TIME)

    def test_event_cannot_be_forged_from_prompt_or_wrong_ref(self):
        policy = {"authenticated_owner_logins": ["Wealthtechinnovations", "Patricked-code"],
                  "repository": REPO}
        env = {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch",
               "GITHUB_ACTOR": "Wealthtechinnovations", "GITHUB_REPOSITORY": REPO,
               "GITHUB_REF": "refs/heads/main"}
        event = {"sender": {"login": "Wealthtechinnovations"}, "repository": {"full_name": REPO}}
        self.assertEqual(lab.verify_trusted_event(env, event, policy), ("Wealthtechinnovations", REPO))
        variants = [
            ({"GITHUB_ACTOR": "outsider"}, event),
            ({"GITHUB_EVENT_NAME": "pull_request"}, event),
            ({"GITHUB_ACTIONS": "false"}, event),
            ({"GITHUB_REF": "refs/heads/lab/unsafe"}, event),
            ({}, {"sender": {"login": "Patricked-code"}, "repository": {"full_name": REPO}}),
            ({}, {"sender": {"login": "Wealthtechinnovations"}, "repository": {"full_name": "other/repo"}}),
        ]
        for patch, changed_event in variants:
            with self.assertRaises(lab.LabEntryError):
                lab.verify_trusted_event({**env, **patch}, changed_event, policy)

    def test_bootstrap_ci_and_duplicate_rejection(self):
        gh = FakeAPI()
        result = lab.run(gh, "new-pool-lab", "A LAB with pool and work queue",
                         "Wealthtechinnovations", REPO)
        self.assertEqual(result["issue"], 450)
        self.assertEqual(result["pr"], 451)
        self.assertEqual(result["lab_head"], "c" * 40)
        self.assertEqual(result["queue"], "NOT_RELEASED")
        self.assertEqual(gh.commits, 2)
        self.assertEqual(gh.prs, 1)
        self.assertEqual(gh.ci, 1)
        with self.assertRaisesRegex(lab.LabEntryError, "ALREADY_EXISTS"):
            lab.run(gh, "new-pool-lab", "A LAB with pool and work queue",
                    "Wealthtechinnovations", REPO)
        self.assertEqual(gh.prs, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
