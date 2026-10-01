#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY_PATH=ROOT/".governance"/"control-plane-state"/"namespace-work-registry.json"


def load_json(path:str):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))


def assert_unique(values:list[str], label:str):
    duplicates=sorted(k for k,v in Counter(values).items() if v>1)
    if duplicates:
        raise SystemExit(f"NAMESPACE_REGISTRY_VALIDATION_FAILED: duplicate {label}: {duplicates}")


def namespace_matches(registry:dict, value:str)->list[str]:
    matches=[]
    for ns in registry.get("namespaces") or []:
        if re.fullmatch(ns["pattern"], value):
            matches.append(ns["id"])
    return matches


def assert_registered(registry:dict, values:list[str], label:str):
    for value in values:
        matches=namespace_matches(registry,value)
        if not matches:
            raise SystemExit(f"NAMESPACE_REGISTRY_VALIDATION_FAILED: unregistered {label} id {value}")
        if len(matches)>1:
            raise SystemExit(f"NAMESPACE_REGISTRY_VALIDATION_FAILED: ambiguous {label} id {value}: {matches}")


def extract_decisions()->list[str]:
    text=(ROOT/"docs/control-plane/DECISIONS_LOG.md").read_text(encoding="utf-8")
    return re.findall(r"^###\s+(CPD-\d{3})\s+—",text,re.MULTILINE)


def extract_task_ids()->list[str]:
    return [x["id"] for x in load_json(".governance/control-plane-state/tasks.json").get("items") or []]


def extract_aq_ids()->list[str]:
    data=load_json(".governance/control-plane-state/adaptive-question-catalogue.json")
    values=[x["id"] for x in data.get("questions") or []]
    values += [x["id"] for x in data.get("future_incremental_implementation") or []]
    return values


def extract_kbi_and_recipe_ids()->tuple[list[str],list[str],list[str]]:
    kb=load_json(".governance/control-plane-state/knowledge-base.json")
    server=load_json(".governance/control-plane-state/server-knowledge-model.json")
    ident=load_json(".governance/control-plane-state/identity-secret-lifecycle.json")
    kbi=[x["id"] for x in kb.get("future_incremental_work") or []]
    kbi += [x["id"] for x in server.get("next_incremental_slices") or []]
    kbi += [x["id"] for x in ident.get("future_incremental_slices") or []]
    srv=[x["id"] for x in server.get("operation_recipes") or []]
    idsec=[x["id"] for x in ident.get("lifecycle_operations") or []]
    return kbi,srv,idsec


def extract_gmc_ids()->dict[str,list[str]]:
    bp=load_json(".governance/control-plane-state/governance-model-execution-blueprint.json")
    groups=[]; legacy=[]; tasks=[]; exits=[]; artifacts=[]; evidence=[]
    for group in bp.get("groups") or []:
        groups.append(group["group_id"])
        if group.get("legacy_id"):
            legacy.append(group["legacy_id"])
        tasks += [x["task_id"] for x in group.get("atomic_tasks") or []]
        exits += [x["control_id"] for x in group.get("exit_controls") or []]
        artifacts += [x["artifact_id"] for x in group.get("produced_artifacts") or []]
        evidence += [
            x["evidence_requirement_id"]
            for x in (group.get("dependency_contract") or {}).get("evidence_dependencies") or []
            if x.get("evidence_requirement_id")
        ]
    # Global artifact catalogue repeats produced_artifacts by design; it is a projection,
    # not a second canonical definition source, so it is intentionally not re-counted.
    return {
        "GMC group":groups,
        "GMC legacy":legacy,
        "GMC task":tasks,
        "GMC exit":exits,
        "GMA artifact":artifacts,
        "EVREQ":evidence,
    }


def extract_continuity()->list[str]:
    cp=load_json(".governance/control-plane-state/checkpoint.json")
    ho=load_json(".governance/control-plane-state/handoff.json")
    return [cp["checkpoint_id"],ho["handoff_id"]]


def main():
    registry=json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if registry.get("authority_id")!="CP-NAMESPACE-001":
        raise SystemExit("NAMESPACE_REGISTRY_VALIDATION_FAILED: authority")

    namespace_ids=[x["id"] for x in registry.get("namespaces") or []]
    assert_unique(namespace_ids,"namespace")
    for ns in registry.get("namespaces") or []:
        re.compile(ns["pattern"])

    authorities=registry.get("canonical_authorities") or []
    assert_unique(authorities,"canonical authority")
    assert_registered(registry,authorities,"canonical authority")

    definitions={
        "CPD":extract_decisions(),
        "task":extract_task_ids(),
        "AQ/AQI":extract_aq_ids(),
        "continuity":extract_continuity(),
    }
    kbi,srv,idsec=extract_kbi_and_recipe_ids()
    definitions["KBI"]=kbi
    definitions["SRV-OP"]=srv
    definitions["IDSEC-OP"]=idsec
    definitions.update(extract_gmc_ids())

    for label,values in definitions.items():
        assert_unique(values,label)
        assert_registered(registry,values,label)

    reconciliations=registry.get("legacy_reconciliation") or []
    for item in reconciliations:
        if item["canonicalized_id"] not in definitions["CPD"]:
            raise SystemExit(
                "NAMESPACE_REGISTRY_VALIDATION_FAILED: legacy CPD reconciliation target not defined: "
                + item["canonicalized_id"]
            )

    contract=registry.get("multi_agent_collision_contract") or {}
    guards=set(contract.get("required_guards") or [])
    required_guards={
        "registered namespace","unique canonical definition id",
        "dependency-safe dispatch","claim before mutable work",
        "single writer per collision domain","exact-head precondition",
        "reconcile on HEAD_MOVED","structured checkpoint and handoff"
    }
    if required_guards-guards:
        raise SystemExit("NAMESPACE_REGISTRY_VALIDATION_FAILED: incomplete multi-agent collision contract")

    print("CANONICAL_NAMESPACE_WORK_REGISTRY_VALIDATION_PASS")


if __name__=="__main__":
    main()
