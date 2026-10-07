#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MASTER="docs/control-plane/MASTER_SYSTEM_MAP.md"
REQ="docs/control-plane/REQUIREMENTS_ROADMAP.md"

LINK_SURFACES=[
    "README.md",
    "00_START_HERE.md",
    "AGENTS.md",
    "docs/control-plane/CANONICAL_ARCHITECTURE.md",
    "docs/control-plane/DATA_MODEL.md",
    "docs/control-plane/GSCC_GSE_GACR_REUSABLE_CAPSULE.md",
]

def fail(msg:str)->None:
    raise SystemExit("MASTER_DOCUMENTATION_INTEGRITY_FAILED: "+msg)

def read(path:str)->str:
    p=ROOT/path
    if not p.exists():
        fail(f"missing {path}")
    return p.read_text(encoding="utf-8")

def load(path:str)->dict:
    return json.loads(read(path))

def main()->None:
    master=read(MASTER)
    req=read(REQ)

    for surface in LINK_SURFACES:
        text=read(surface)
        if MASTER not in text:
            fail(f"{surface} does not link master system map")
        if REQ not in text:
            fail(f"{surface} does not link requirements roadmap")

    required_master=[
        "GSCC","GSE","GACR","F1","00_START_HERE.md",
        "WORK_ON_CONTROL_PLANE","APPLY_GOVERNANCE_CASE",
        "CREATE_NEW_REPOSITORY","ADOPT_EXISTING_REPOSITORY",
        "MAP_EXISTING_PROJECT","LAB_EVOLUTION",
        "run_answers","checkpoints","handoffs",
        "P12-S6","GMC-01..GMC-19","RTE-001..RTE-012","CAP-001..CAP-012","SAA-001..SAA-015",
        "https://mcp.wealthtechinnovations.com/template",
        "PLANNED_NOT_ACTIVE",
    ]
    for token in required_master:
        if token not in master:
            fail(f"master map missing {token}")

    for token in ("RQ-01","RQ-12","RQ-19","RQ-28","Definition of done","Current roadmap"):
        if token not in req:
            fail(f"requirements roadmap missing {token}")

    arch=load(".governance/control-plane-state/canonical-architecture.json")
    if arch.get("current_revision") != 8:
        fail("canonical architecture current revision must be 8")
    if (arch.get("revision") or {}).get("revision_id") != "CP-ARCH-001-R8":
        fail("canonical architecture revision id mismatch")
    if (arch.get("live_execution_reference") or {}).get("master_system_map") != MASTER:
        fail("canonical architecture machine projection missing master map")
    if (arch.get("live_execution_reference") or {}).get("requirements_roadmap") != REQ:
        fail("canonical architecture machine projection missing requirements roadmap")

    current=load(".governance/control-plane-state/current.json")
    if ((current.get("canonical_architecture") or {}).get("revision")) != 8:
        fail("current projection architecture revision mismatch")
    docs=((current.get("knowledge_enrichment") or {}).get("master_architecture_documentation") or {})
    if docs.get("navigation_only_no_parallel_authority") is not True:
        fail("master documentation must remain navigation-only")

    tasks=load(".governance/control-plane-state/tasks.json")
    active=[x.get("id") for x in tasks.get("items",[]) if x.get("status")=="IN_PROGRESS"]
    if active != ["P12-S6"]:
        fail(f"unexpected active global tasks: {active}")
    cap=next((x for x in tasks.get("items",[]) if x.get("id")=="CAP-001"),None)
    if not cap:
        fail("CAP-001 missing")
    expected={"GMC-19","RTE-012","ARCH-006","IDN-006"}
    if set(cap.get("depends_on") or []) != expected:
        fail("CAP-001 dependency gate drift")
    saa=next((x for x in tasks.get("items",[]) if x.get("id")=="SAA-013"),None)
    if not saa or saa.get("next_action") != "DEPLOY_PRODUCTION_MCP_WEALTHTECHINNOVATIONS_TEMPLATE":
        fail("SAA-013 production deployment task missing or drifted")
    if "https://mcp.wealthtechinnovations.com/template" not in str(saa.get("objective") or ""):
        fail("SAA-013 production URL drift")

    policy=load(".governance/control-plane-policy.json")
    routing=(policy.get("agent_purpose_routing") or {})
    if routing.get("status") != "PLANNED_NOT_ACTIVE":
        fail("two-stage purpose router must not be silently activated")
    if routing.get("continue_governed_work_is_fifth_case") is not False:
        fail("CONTINUE_GOVERNED_WORK must not become a fifth case")

    data_model=read("docs/control-plane/DATA_MODEL.md")
    if "Current LIVE identity/session chain and planned normalized registry" not in data_model:
        fail("data model must distinguish live identity chain from planned normalization")
    if "This chain is LIVE proven through `IDN-006`." not in data_model:
        fail("data model missing live IDN-006 attestation")

    print("MASTER_DOCUMENTATION_INTEGRITY_PASS")

if __name__=="__main__":
    main()
