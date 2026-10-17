#!/usr/bin/env python3
"""Create a GitHub LAB with a development continuity, chronological registry, agent pool and draft PR.

Only a verified GitHub Actions workflow_dispatch may apply changes. The output
does not create GACR sessions, claims, leases, dispatch authority or merge rights.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / ".governance/repository-entry-gates.json"
SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
SHA = re.compile(r"^[0-9a-f]{40}$")


class LabEntryError(ValueError):
    pass


def ids(slug, objective):
    if not isinstance(slug, str) or len(slug) < 3 or len(slug) > 36 or not SLUG.fullmatch(slug):
        raise LabEntryError("INVALID_SLUG")
    if not isinstance(objective, str) or not (12 <= len(objective.strip()) <= 1200):
        raise LabEntryError("INVALID_OBJECTIVE")
    name = slug.upper().replace("-", "_")
    return {"continuity_id": "GRT-CONT-LAB-" + name,
            "pool_id": "GRT-POOL-LAB-" + name, "branch": "lab/" + slug}


def tasks(continuity_id):
    ordered = [
        ("01-OBSERVE", [], "ARCH", "Inspect repository, governance, HEAD, risks and baseline"),
        ("02-MEMORY", ["01-OBSERVE"], "ARCH", "Create chronological canonical memory and checkpoint trail"),
        ("03-ARCH", ["02-MEMORY"], "ARCH", "Document existing and target architecture, impacts"),
        ("04-SPEC", ["03-ARCH"], "PLAN", "Write specifications, acceptance, negative tests"),
        ("05-PLAN", ["04-SPEC"], "PLAN", "Break implementation into dependency-ordered lots with evidence"),
        ("06-REVIEW", ["05-PLAN"], "REVIEW", "Independently review and request canonical queue promotion"),
        ("07-CODE", ["06-REVIEW"], "CODE", "Implement claimed lots under real permissions without regression"),
        ("08-TEST", ["07-CODE"], "CODE", "Run tests and capture independent CI evidence"),
        ("09-VERIFY", ["08-TEST"], "REVIEW", "Reconcile HEAD, review code, attest LAB readiness"),
        ("10-MERGE", ["09-VERIFY"], "REVIEW", "Separate authorized PR merge gate"),
        ("11-DEPLOY", ["10-MERGE"], "PLAN", "Separate deployment, smoke and rollback gate")
    ]
    return [{"id": continuity_id + "-" + step, "sequence": i,
             "depends_on": [continuity_id + "-" + d for d in deps],
             "suggested_role": role, "objective": title,
             "status": "PLANNED", "dispatch_release": "NOT_RELEASED",
             "claim_id": None, "lease_id": None, "evidence": []}
            for i, (step, deps, role, title) in enumerate(ordered, 1)]


def package(slug, objective, actor, repository, head, issue, time):
    vals = ids(slug, objective)
    if not SHA.fullmatch(head) or not isinstance(issue, int) or issue <= 0:
        raise LabEntryError("UNVERIFIED_BASE_OR_ISSUE")
    cont, pool_id = vals["continuity_id"], vals["pool_id"]
    root = "docs/labs/" + cont + "/"
    pool_roles = [
        ("ARCH", "ARCHITECT_MEMORY", "Architecture, memory, chronology, code/documentation"),
        ("PLAN", "PLANNER_COORDINATOR", "Specifications, ordered tasks and code/documentation"),
        ("CODE", "CODE_AGENT", "Non-regressive implementation and tests"),
        ("REVIEW", "INDEPENDENT_REVIEWER", "Independent verification, test fixes and documentation")
    ]
    pool = {"schema": "grt-lab-minimum-pool/v1", "pool_id": pool_id,
            "continuity_id": cont, "state": "SLOTS_RESERVED_UNBOUND",
            "allow_additional_agents": True, "gacr_bindings": [],
            "members": [
                {"slot": role, "slot_id": pool_id + "-" + role, "role": label,
                 "responsibility": mission, "can_propose_code_change": True,
                 "session_id": None, "agent_id": None, "status": "VACANT",
                 "actual_write_permission": "NOT_ATTESTED_MUST_CHECK_GITHUB"}
                for role, label, mission in pool_roles]}
    queue = {"schema": "grt-lab-staged-queue/v1", "continuity_id": cont,
             "target": ".governance/control-plane-state/tasks.json",
             "dispatcher": "scripts/gacr_capacity_dispatch.py",
             "promotion_status": "PENDING_GOVERNED_REVIEW",
             "authorizes_dispatch": False, "authorizes_claim": False,
             "tasks": tasks(cont)}
    journal = [
        {"seq": 1, "at": time, "event": "TRUSTED_GITHUB_OWNER_ENTRY", "actor": actor, "base_head": head},
        {"seq": 2, "at": time, "event": "ISSUE_REGISTERED", "issue": issue},
        {"seq": 3, "at": time, "event": "LAB_BRANCH_CREATED", "branch": vals["branch"]},
        {"seq": 4, "at": time, "event": "POOL_AND_QUEUE_STAGED", "pool_id": pool_id}
    ]
    registry = {"schema": "grt-development-continuity/v1", **vals,
                "repository": repository, "objective": objective.strip(),
                "creator_github_actor": actor, "created_at": time,
                "base_head": head, "issue_number": issue, "pr_number": None,
                "state": "BOOTSTRAPPING", "chronology": journal,
                "session_continuity_links": [], "gacr_sessions": [],
                "merger_authority": False, "deployment_authority": False}
    lab_doc = "\n".join([
        "# LAB " + cont, "", "## Identity",
        "Objective: " + objective.strip(),
        "Creator GitHub: " + actor,
        "Development continuity ID: " + cont,
        "Pool ID: " + pool_id,
        "Repository: " + repository, "Base HEAD: " + head,
        "Branch: " + vals["branch"], "Coordination issue: #" + str(issue),
        "Continuity PR: see REGISTRY.json and coordination issue", "",
        "## Chronology, memory and architecture",
        "Keep REGISTRY.json append-only in chronology, with genuine authors, events,",
        "decisions, code, test results, change scopes, HEADs, checkpoints, next action.",
        "Architect observes the existing system before preparing design and specification.",
        "Planner decomposes tasks with dependencies and measurable acceptance.",
        "Reviewer validates before any real claim, code dispatch or integration.", "",
        "## Execution and governance",
        "POOL.json reserves agent roles, not real authenticated members.",
        "Every agent must independently prove native GitHub permissions to write.",
        "QUEUE.json contains staged proposals; the existing canonical task graph and",
        "GACR dispatcher alone decide actual eligible dispatch, claims and collisions.",
        "No fabricated GACR session, no claim, no task release, no automatic merge.",
        "Merge and deployment require independent approvals and evidence.", ""
    ]) + "\n"
    return {root + "LAB.md": lab_doc,
            root + "REGISTRY.json": json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
            root + "POOL.json": json.dumps(pool, ensure_ascii=False, indent=2) + "\n",
            root + "QUEUE.json": json.dumps(queue, ensure_ascii=False, indent=2) + "\n"}


def link_pr(registry_text, pr_number, observed_head, time):
    doc = json.loads(registry_text)
    if doc.get("pr_number") is not None or not SHA.fullmatch(observed_head) or pr_number < 1:
        raise LabEntryError("BAD_OR_DUPLICATE_PR_LINK")
    doc["pr_number"] = pr_number
    doc["state"] = "LAB_CREATED_AWAITING_ARCHITECTURE"
    doc["chronology"].append({"seq": len(doc["chronology"]) + 1,
                              "at": time, "event": "DRAFT_PR_LINKED",
                              "pr_number": pr_number,
                              "head_before_link_commit": observed_head})
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def verify_trusted_event(env, event, policy):
    actor = env.get("GITHUB_ACTOR")
    repo = env.get("GITHUB_REPOSITORY")
    if env.get("GITHUB_ACTIONS") != "true" or env.get("GITHUB_EVENT_NAME") != "workflow_dispatch":
        raise LabEntryError("TRUSTED_WORKFLOW_DISPATCH_REQUIRED")
    if actor not in policy["authenticated_owner_logins"] or actor != (event.get("sender") or {}).get("login"):
        raise LabEntryError("ACTOR_NOT_AUTHENTICATED_OWNER")
    if repo != policy["repository"] or repo != (event.get("repository") or {}).get("full_name"):
        raise LabEntryError("REPOSITORY_NOT_VERIFIED")
    if env.get("GITHUB_REF") != "refs/heads/main":
        raise LabEntryError("MAIN_WORKFLOW_REF_REQUIRED")
    return actor, repo


class API:
    def __init__(self, token):
        if not token:
            raise LabEntryError("GITHUB_TOKEN_UNAVAILABLE")
        self.token = token

    def req(self, method, route, data=None, missing_ok=False):
        request = urllib.request.Request(
            "https://api.github.com" + route,
            data=json.dumps(data).encode() if data is not None else None,
            method=method,
            headers={"Authorization": "Bearer " + self.token,
                     "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json",
                     "X-GitHub-Api-Version": "2022-11-28"})
        try:
            with urllib.request.urlopen(request, timeout=25) as answer:
                raw = answer.read(1500000).decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as err:
            if missing_ok and err.code == 404:
                return None
            raise LabEntryError("GITHUB_API_" + method + "_" + str(err.code)) from err

    def commit(self, repo, branch, parent, files, message):
        path = "/repos/" + repo
        base = self.req("GET", path + "/git/commits/" + parent)
        tree = self.req("POST", path + "/git/trees",
                        {"base_tree": base["tree"]["sha"],
                         "tree": [{"path": key, "mode": "100644", "type": "blob",
                                   "content": value} for key, value in sorted(files.items())]})
        new = self.req("POST", path + "/git/commits",
                       {"message": message, "tree": tree["sha"], "parents": [parent]})
        actual = self.req("GET", path + "/git/ref/heads/" + branch)["object"]["sha"]
        if actual != parent:
            raise LabEntryError("HEAD_MOVED_RECONCILE_REQUIRED")
        self.req("PATCH", path + "/git/refs/heads/" + branch, {"sha": new["sha"], "force": False})
        return new["sha"]


def run(api, slug, objective, actor, repository):
    vals = ids(slug, objective)
    path = "/repos/" + repository
    info = api.req("GET", path)
    if info.get("full_name") != repository or info.get("default_branch") != "main":
        raise LabEntryError("REPOSITORY_MISMATCH")
    sha = api.req("GET", path + "/commits/main")["sha"]
    if api.req("GET", path + "/git/ref/heads/" + vals["branch"], missing_ok=True) is not None:
        raise LabEntryError("LAB_ALREADY_EXISTS_RESUME_INSTEAD")
    # Use deterministic branch/ID as replay guard. An interrupted bootstrap
    # may leave one issue; reuse it, never silently create a second one.
    issue = None
    for page in range(1, 6):
        page_items = api.req("GET", path + "/issues?state=all&per_page=100&page=" + str(page))
        issue = next((x for x in page_items if x.get("title") == "[LAB-ENTRY] " + vals["continuity_id"]), None)
        if issue or len(page_items) < 100:
            break
    else:
        raise LabEntryError("INCOMPLETE_ISSUE_INDEX")
    if issue and (issue.get("state") != "open" or
                  ("Objective: " + objective.strip()) not in (issue.get("body") or "")):
        raise LabEntryError("EXISTING_LAB_ISSUE_MISMATCH")
    if issue is None:
        content = "\n".join([
            "# LAB ENTRY " + vals["continuity_id"], "",
            "Objective: " + objective.strip(),
            "Creator: " + actor, "Branch: " + vals["branch"],
            "Pool: " + vals["pool_id"], "Observed base HEAD: " + sha,
            "State: BOOTSTRAPPING; no GACR session/claim authority.", ""])
        issue = api.req("POST", path + "/issues",
                        {"title": "[LAB-ENTRY] " + vals["continuity_id"], "body": content})
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    files = package(slug, objective, actor, repository, sha, issue["number"], now)
    api.req("POST", path + "/git/refs", {"ref": "refs/heads/" + vals["branch"], "sha": sha})
    first = api.commit(repository, vals["branch"], sha, files, "lab: create canonical LAB pool and staged queue")
    pr = api.req("POST", path + "/pulls",
                 {"head": vals["branch"], "base": "main", "draft": True,
                  "title": "[LAB][DRAFT] " + vals["continuity_id"],
                  "body": "Continuity: " + vals["continuity_id"] + "\nPool: " +
                          vals["pool_id"] + "\nIssue: #" + str(issue["number"]) +
                          "\nNo merge or deployment approval; staged tasks only.\n"})
    registry = "docs/labs/" + vals["continuity_id"] + "/REGISTRY.json"
    latest = api.commit(repository, vals["branch"], first,
                        {registry: link_pr(files[registry], pr["number"], first, now)},
                        "lab: persist linked PR #" + str(pr["number"]))
    issue_body = (issue.get("body") or "") + "\n\n## LAB READY\n" + (
        "Branch: " + vals["branch"] + "\nContinuity: " + vals["continuity_id"] +
        "\nPool: " + vals["pool_id"] + "\nPR: #" + str(pr["number"]) +
        "\nLab HEAD: " + latest + "\nPool slots: UNBOUND; queue: NOT_DISPATCHED.\n")
    api.req("PATCH", path + "/issues/" + str(issue["number"]), {"body": issue_body})
    # GITHUB_TOKEN-created PR events do not reliably trigger pull_request CI.
    api.req("POST", path + "/actions/workflows/governance-ci.yml/dispatches",
            {"ref": vals["branch"]})
    return {**vals, "issue": issue["number"], "pr": pr["number"],
            "lab_head": latest, "ci": "DISPATCH_REQUESTED", "queue": "NOT_RELEASED"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    vals = ids(args.slug, args.objective)
    if args.plan_only:
        print(json.dumps({"ids": vals, "tasks": tasks(vals["continuity_id"])}, indent=2))
        return
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise LabEntryError("EVENT_PATH_UNAVAILABLE")
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    actor, repo = verify_trusted_event(os.environ, event, policy)
    print(json.dumps(run(API(os.environ.get("GITHUB_TOKEN")), args.slug,
                         args.objective, actor, repo), indent=2))


if __name__ == "__main__":
    main()
