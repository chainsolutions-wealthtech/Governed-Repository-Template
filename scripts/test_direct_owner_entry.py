#!/usr/bin/env python3
"""A-G acceptance matrix for both repository entry doors, pure isolated fixtures."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from gscc_entry_router import route as gscc_route
from repository_entry_router import select_entry, DIRECT, GOVERNED

ROOT=Path(__file__).resolve().parents[1]
REPO="chainsolutions-wealthtech/Governed-Repository-Template"
HEAD="b"*40
MISSION=[
 ("JE VIENS CODER","CODE_AGENT","CODE_CHANGE"),
 ("JE VIENS SUPERVISER","SUPERVISOR","OBSERVE"),
 ("JE VIENS FAIRE UN INTAKE","INTAKER","INFORMATION_INTAKE"),
 ("JE VIENS VÉRIFIER","REVIEWER","REVIEW"),
 ("JE VIENS PLANIFIER","PLANNER_AGENT","CONTEXT_INTAKE"),
]

def adapter(login="Wealthtechinnovations",pull=True,push=True,
            repo=REPO,sha=HEAD,default_branch="main",
            omit_permissions=False):
    def read(path):
        if path=="/user":return {"login":login,"id":94637590}
        if path=="/repos/"+REPO:
            val={"full_name":repo,"default_branch":default_branch}
            if not omit_permissions:
                val["permissions"]={"pull":pull,"push":push,"admin":push}
            return val
        if path=="/repos/"+REPO+"/commits/"+default_branch:return {"sha":sha}
        raise AssertionError("Unexpected REST path: "+path)
    return read

class DirectOwnerEntry(unittest.TestCase):
    def test_A_default_entry_is_unmodified_gscc(self):
        expected=gscc_route("ARRIVAL")
        got=select_entry()
        self.assertEqual(got["target"],"00_GSCC_ENTRY.md")
        self.assertEqual(got["next_step"],"R1_PROVIDER_CONTEXT")
        self.assertFalse(got["may_write"])
        for k,v in expected.items():
            self.assertEqual(got[k],v,k)
        self.assertEqual(gscc_route("00_GSCC_ENTRY.md")["next_step"],"Q1")
        self.assertEqual(gscc_route("00_GSCC_ENTRY.md","ENTRY_BLOCKED")["next_step"],"BLOCK_UNRESOLVED")
        self.assertEqual(gscc_route("ARRIVAL")["target"],"00_GSCC_ENTRY.md")

    def test_A_explicit_governed_stays_governed(self):
        self.assertEqual(select_entry(GOVERNED)["entry"],"GOVERNED")
        self.assertEqual(gscc_route("ARRIVAL",entry_file=GOVERNED)["target"],GOVERNED)

    def test_B_explicit_owner_authenticated_and_f1_independent(self):
        for login in ["Wealthtechinnovations","Patricked-code"]:
            with self.subTest(login=login):
                d=select_entry(DIRECT,"JE VIENS CODER",read_github=adapter(login=login))
                self.assertEqual(d["status"],"DIRECT_OWNER_VERIFIED")
                self.assertTrue(d["authenticated"])
                self.assertEqual(d["authenticated_actor"],login)
                self.assertEqual(d["observed_head"],HEAD)
                self.assertTrue(d["may_attempt_git_write"])
                self.assertTrue(d["may_attempt_direct_main_write"])
                self.assertFalse(d["requires_gacr"])
                self.assertFalse(d["requires_f1"])
                self.assertFalse(d["requires_preassigned_work_item"])
                self.assertFalse(d["creates_gscc_receipt"])
                self.assertFalse(d["grants_gacr_claim"])
                self.assertFalse(d["main_write_success_claimed"])
                self.assertFalse(d["branch_protection_bypass_granted"])

    def test_C_spontaneous_coding_role_without_task_claim(self):
        d=gscc_route("ARRIVAL",entry_file=DIRECT,mission="JE VIENS CODER",
                     read_github=adapter())
        self.assertEqual(d["role"],"CODE_AGENT")
        self.assertEqual(d["connection_intent"],"CODE_CHANGE")
        self.assertEqual(d["next_action"],"EXECUTE_SCOPED_GITHUB_OPERATION_WITH_EXACT_HEAD_AND_NATIVE_CONTROLS")
        self.assertTrue(d["native_github_enforces_every_write"])
        self.assertFalse(d["requires_preassigned_work_item"])

    def test_D_main_write_is_attempt_not_granted_success(self):
        d=select_entry(DIRECT,"JE VIENS CODER",read_github=adapter())
        self.assertTrue(d["may_attempt_direct_main_write"])
        self.assertFalse(d["main_write_success_claimed"])
        self.assertFalse(d["branch_protection_bypass_granted"])
        self.assertEqual(d["trace"],"GITHUB_NATIVE_COMMIT_PR_ISSUE_OR_REVIEW")

    def test_E_lab_without_gacr_mint(self):
        d=select_entry(DIRECT,"JE VIENS CODER",read_github=adapter())
        for field in ("requires_gscc","requires_gse","requires_gacr","requires_f1","requires_preassigned_work_item","grants_gacr_claim","creates_gscc_receipt"):
            self.assertFalse(d[field],field)

    def test_F_untrusted_nonowner_refused_even_with_push(self):
        for actor in ["user-claims-owner","attacker","github-actions[bot]","wealThtechinnovations"]:
            with self.subTest(actor=actor):
                v=select_entry(DIRECT,"JE VIENS CODER",read_github=adapter(login=actor))
                self.assertFalse(v["may_write"])
                self.assertEqual(v["status"],"GITHUB_OWNER_NOT_AUTHORIZED")

    def test_F_prompt_and_github_actor_env_are_not_auth(self):
        with patch.dict(os.environ,{"GITHUB_ACTOR":"Wealthtechinnovations"}):
            d=select_entry(DIRECT,"JE VIENS CODER")
            self.assertEqual(d["status"],"AUTHENTICATION_REQUIRED")
            self.assertFalse(d["may_write"])

    def test_F_github_verified_identity_ignores_role_text(self):
        d=select_entry(DIRECT,"JE VIENS CODER",read_github=adapter(login="outsider"))
        self.assertEqual(d["status"],"GITHUB_OWNER_NOT_AUTHORIZED")

    def test_F_missing_repo_push_is_read_only(self):
        d=select_entry(DIRECT,"JE VIENS CODER",read_github=adapter(push=False))
        self.assertEqual(d["status"],"DIRECT_OWNER_VERIFIED")
        self.assertFalse(d["may_write"])
        self.assertFalse(d["may_attempt_direct_main_write"])
        self.assertEqual(d["next_action"],"READ_ONLY_NATIVE_GITHUB_OPERATIONS")

    def test_F_missing_permissions_fail_closed(self):
        d=select_entry(DIRECT,"JE VIENS CODER",read_github=adapter(omit_permissions=True))
        self.assertEqual(d["status"],"GITHUB_REPOSITORY_PERMISSION_PROOF_UNAVAILABLE")
        self.assertFalse(d["may_write"])

    def test_F_wrong_repo_fails(self):
        d=select_entry(DIRECT,"JE VIENS CODER",read_github=adapter(repo="impostor/other"))
        self.assertEqual(d["status"],"GITHUB_REPOSITORY_PERMISSION_PROOF_UNAVAILABLE")

    def test_F_head_moved_fails(self):
        d=select_entry(DIRECT,"JE VIENS CODER",read_github=adapter(),expected_head="a"*40)
        self.assertEqual(d["status"],"GITHUB_HEAD_MOVED")
        self.assertFalse(d["may_write"])

    def test_F_unavailable_head_fails(self):
        d=select_entry(DIRECT,"JE VIENS CODER",read_github=adapter(sha="unknown"))
        self.assertEqual(d["status"],"GITHUB_HEAD_UNAVAILABLE")
        self.assertFalse(d["may_write"])

    def test_F_auth_endpoint_failure_fails(self):
        def fail(_):raise RuntimeError("not authenticated")
        # Only an authenticated adapter may be passed in production. The API adapter
        # explicitly converts network/auth failures into AuthFailed and fails closed.
        from repository_entry_router import AuthFailed
        def verified_fail(_):raise AuthFailed("GITHUB_VERIFICATION_UNAVAILABLE")
        d=select_entry(DIRECT,"JE VIENS CODER",read_github=verified_fail)
        self.assertEqual(d["status"],"GITHUB_VERIFICATION_UNAVAILABLE")
        self.assertFalse(d["may_write"])

    def test_F_no_role_no_entry(self):
        d=select_entry(DIRECT,read_github=adapter())
        self.assertEqual(d["status"],"ROLE_DECLARATION_REQUIRED")
        self.assertFalse(d["authenticated"])

    def test_F_no_implicit_direct_for_mission_only(self):
        d=select_entry(mission="JE VIENS CODER",read_github=adapter())
        self.assertEqual(d["entry"],"GOVERNED")

    def test_F_unknown_entry_does_not_fallback_to_owner(self):
        d=select_entry("anything-else.md","JE VIENS CODER",read_github=adapter())
        self.assertEqual(d["status"],"UNKNOWN_ENTRY_FILE")
        self.assertFalse(d["may_write"])

    def test_roles_use_historical_intents_without_mutation_by_role(self):
        for phrase,role,intent in MISSION:
            with self.subTest(mission=phrase):
                d=select_entry(DIRECT,phrase,read_github=adapter(push=False))
                self.assertEqual(d["role"],role)
                self.assertEqual(d["connection_intent"],intent)
                self.assertFalse(d["may_write"])

    def test_G_docs_and_old_router_contract_remain_in_place(self):
        old=(ROOT/"00_GSCC_ENTRY.md").read_text()
        direct=(ROOT/"00_DIRECT_OWNER_ENTRY.md").read_text()
        doc=(ROOT/"AGENTS.md").read_text()
        self.assertIn("GSCC → GSE → GACR",old)
        self.assertIn("00_DIRECT_OWNER_ENTRY.md",doc)
        self.assertIn("00_DIRECT_OWNER_ENTRY.md",old)
        self.assertIn("aucun first touch",direct.lower())
        config=json.loads((ROOT/".governance/repository-entry-gates.json").read_text())
        self.assertTrue(config["direct_entry_must_be_explicit"])
        self.assertTrue(config["no_gacr_session_required"])
        for name in (".github/copilot-instructions.md","CLAUDE.md","GEMINI.md"):
            content=(ROOT/name).read_text()
            self.assertIn("00_GSCC_ENTRY.md",content)
            self.assertIn("00_DIRECT_OWNER_ENTRY.md",content)

    def test_real_cli_gscc_unchanged(self):
        run=subprocess.run([sys.executable,str(ROOT/"scripts/repository_entry_router.py")],
                           text=True,capture_output=True,cwd=ROOT)
        self.assertEqual(run.returncode,0,run.stderr)
        val=json.loads(run.stdout)
        self.assertEqual(val["selected_entry_file"],GOVERNED)
        self.assertFalse(val["may_write"])

    def test_real_cli_explicit_door_b_no_token_fails(self):
        env=dict(os.environ)
        env.pop("GH_TOKEN",None)
        env.pop("GITHUB_TOKEN",None)
        env["GITHUB_ACTOR"]="Wealthtechinnovations"
        run=subprocess.run([sys.executable,str(ROOT/"scripts/gscc_entry_router.py"),
            "--current","ARRIVAL","--entry-file",DIRECT,
            "--mission","JE VIENS CODER"],
            text=True,capture_output=True,cwd=ROOT,env=env)
        self.assertEqual(run.returncode,2,run.stderr)
        v=json.loads(run.stdout)
        self.assertEqual(v["status"],"AUTHENTICATION_REQUIRED")
        self.assertFalse(v["may_write"])

if __name__=="__main__":
    unittest.main()
