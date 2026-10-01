#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from governed_execution_engine import ROOT, REGISTRY_PATH, SNAPSHOT_PATH, ExecutionError, compile_plan, load_json

STATE_VERSION="1.0.0"
TERMINAL={"DONE","SKIPPED"}
FAILURE={"FAILED","FAILED_ROLLED_BACK","FAILED_MANUAL_RECOVERY_REQUIRED","BLOCKED"}


class LoopBindingError(ValueError):
    pass


def initialize_state(blueprint:dict)->dict:
    if blueprint.get("schema_version")!="1.0.0":
        raise LoopBindingError("LOOP_BLUEPRINT_VERSION_INVALID")
    nodes=blueprint.get("nodes")
    if not isinstance(nodes,list) or not nodes:
        raise LoopBindingError("LOOP_BLUEPRINT_NODES_REQUIRED")
    return {
        "schema_version":STATE_VERSION,
        "authority_id":"CP-EXECUTION-001",
        "blueprint_id":blueprint["blueprint_id"],
        "project_id":blueprint["project_id"],
        "revision":0,
        "status":"ACTIVE",
        "nodes":{
            node["node_id"]:{
                "status":"PENDING",
                "attempts":0,
                "last_receipt_status":None,
                "last_receipt_ref":None,
                "completed_at":None,
            }
            for node in nodes
        },
        "execution_authority_granted":False,
        "secret_values_persisted":False,
    }


def validate_state(blueprint:dict,state:dict)->None:
    if state.get("schema_version")!=STATE_VERSION:
        raise LoopBindingError("LOOP_STATE_VERSION_INVALID")
    if state.get("blueprint_id")!=blueprint.get("blueprint_id"):
        raise LoopBindingError("LOOP_STATE_BLUEPRINT_MISMATCH")
    ids={n["node_id"] for n in blueprint["nodes"]}
    if set((state.get("nodes") or {}).keys())!=ids:
        raise LoopBindingError("LOOP_STATE_NODE_SET_MISMATCH")
    if not isinstance(state.get("revision"),int) or state["revision"]<0:
        raise LoopBindingError("LOOP_STATE_REVISION_INVALID")
    if state.get("execution_authority_granted") is not False:
        raise LoopBindingError("LOOP_STATE_MUST_NOT_GRANT_AUTHORITY")
    if state.get("secret_values_persisted") is not False:
        raise LoopBindingError("LOOP_STATE_SECRET_PERSISTENCE_FORBIDDEN")


def _by_id(blueprint:dict)->dict[str,dict]:
    return {node["node_id"]:node for node in blueprint["nodes"]}


def dependency_status(node:dict,state:dict)->tuple[bool,list[str]]:
    unresolved=[]
    for dep in node.get("depends_on") or []:
        status=state["nodes"][dep]["status"]
        if status not in TERMINAL:
            unresolved.append(dep)
    return not unresolved,unresolved


def node_runtime_readiness(node:dict,registry:dict,snapshot:dict)->dict:
    if node.get("compile_status")!="READY":
        return {
            "ready":False,
            "reason":"COMPILE_NOT_READY",
            "compile_status":node.get("compile_status"),
            "blockers":copy.deepcopy(node.get("blockers") or []),
            "missing_inputs":copy.deepcopy(node.get("missing_inputs") or []),
        }
    try:
        plan=compile_plan(node["package"],registry,snapshot)
    except ExecutionError as exc:
        return {"ready":False,"reason":exc.code,"detail":exc.detail}
    if not plan.get("executable_now"):
        return {
            "ready":False,
            "reason":"LIVE_PLAN_BLOCKED",
            "blockers":copy.deepcopy(plan.get("missing_capabilities_or_bindings") or []),
        }
    authority=node["package"].get("authority") or {}
    spec=registry["intents"][node["intent"]]
    if spec.get("side_effecting") and authority.get("approved") is not True:
        return {"ready":False,"reason":"AUTHORITY_NOT_APPROVED"}
    return {"ready":True,"reason":"READY","plan":plan}


def evaluate(blueprint:dict,state:dict,*,registry:dict,snapshot:dict)->dict:
    validate_state(blueprint,state)
    by_id=_by_id(blueprint)
    ready=[]
    blocked=[]
    waiting=[]
    failed=[]
    done=[]

    for node_id,node_state in state["nodes"].items():
        node=by_id[node_id]
        status=node_state["status"]
        if status in TERMINAL:
            done.append(node_id);continue
        if status in FAILURE:
            failed.append(node_id);continue
        deps_ok,unresolved=dependency_status(node,state)
        if not deps_ok:
            waiting.append({"node_id":node_id,"dependencies":unresolved});continue
        readiness=node_runtime_readiness(node,registry,snapshot)
        if readiness["ready"]:
            ready.append({"node_id":node_id,"intent":node["intent"],"package":copy.deepcopy(node["package"])})
        else:
            blocked.append({"node_id":node_id,"intent":node["intent"],**readiness})

    # Deterministic single-next execution preserves one writer / short iteration semantics.
    next_node=ready[0] if ready else None
    overall=(
        "DONE" if len(done)==len(state["nodes"]) else
        "FAILED" if failed else
        "READY" if next_node else
        "BLOCKED" if blocked and not waiting else
        "WAITING"
    )
    return {
        "schema_version":"1.0.0",
        "authority_id":"CP-EXECUTION-001",
        "blueprint_id":blueprint["blueprint_id"],
        "state_revision":state["revision"],
        "status":overall,
        "next_executable":next_node,
        "ready_nodes":[item["node_id"] for item in ready],
        "blocked":blocked,
        "waiting":waiting,
        "failed":failed,
        "done":done,
        "single_writer_selection":True,
        "execution_performed":False,
    }


def apply_receipt(blueprint:dict,state:dict,receipt:dict,*,expected_revision:int)->dict:
    validate_state(blueprint,state)
    if state["revision"]!=expected_revision:
        raise LoopBindingError("LOOP_STATE_REVISION_MOVED")
    operation_id=receipt.get("operation_id")
    by_id=_by_id(blueprint)
    if operation_id not in by_id:
        raise LoopBindingError("LOOP_RECEIPT_OPERATION_UNKNOWN")
    current=state["nodes"][operation_id]
    if current["status"] in TERMINAL:
        raise LoopBindingError("LOOP_RECEIPT_ALREADY_TERMINAL")

    receipt_status=receipt.get("status")
    mapping={
        "PASS":"DONE",
        "READY":"PENDING",
        "BLOCKED_MISSING_CAPABILITY":"BLOCKED",
        "FAILED_NO_SIDE_EFFECT_CONFIRMED":"FAILED",
        "FAILED_ROLLED_BACK":"FAILED_ROLLED_BACK",
        "FAILED_MANUAL_RECOVERY_REQUIRED":"FAILED_MANUAL_RECOVERY_REQUIRED",
    }
    if receipt_status not in mapping:
        raise LoopBindingError("LOOP_RECEIPT_STATUS_UNSUPPORTED")

    result=copy.deepcopy(state)
    target=result["nodes"][operation_id]
    target["status"]=mapping[receipt_status]
    target["attempts"]=int(target.get("attempts") or 0)+(0 if receipt_status=="READY" else 1)
    target["last_receipt_status"]=receipt_status
    target["last_receipt_ref"]=receipt.get("receipt_ref") or receipt.get("operation_id")
    target["completed_at"]=receipt.get("completed_at") if mapping[receipt_status]=="DONE" else None
    result["revision"]+=1

    statuses=[x["status"] for x in result["nodes"].values()]
    if all(x in TERMINAL for x in statuses):
        result["status"]="DONE"
    elif any(x in {"FAILED","FAILED_ROLLED_BACK","FAILED_MANUAL_RECOVERY_REQUIRED"} for x in statuses):
        result["status"]="HOLD"
    else:
        result["status"]="ACTIVE"
    return result


def materialize_next_package(evaluation:dict,output_dir:Path)->Path|None:
    next_node=evaluation.get("next_executable")
    if not next_node:
        return None
    output_dir=output_dir.resolve()
    allowed=(ROOT/".governance"/"control-plane-state"/"execution-packages").resolve()
    try:
        output_dir.relative_to(allowed)
    except ValueError as exc:
        raise LoopBindingError("LOOP_PACKAGE_OUTPUT_OUTSIDE_GOVERNED_DIRECTORY") from exc
    output_dir.mkdir(parents=True,exist_ok=True)
    path=output_dir/(next_node["node_id"]+".json")
    path.write_text(json.dumps(next_node["package"],indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return path


def main():
    parser=argparse.ArgumentParser(description="Select the next governed execution package from a compiled project DAG.")
    parser.add_argument("--blueprint",type=Path,required=True)
    parser.add_argument("--state",type=Path)
    parser.add_argument("--initialize-state",action="store_true")
    parser.add_argument("--receipt",type=Path)
    parser.add_argument("--expected-revision",type=int)
    parser.add_argument("--materialize-next",type=Path)
    args=parser.parse_args()

    blueprint=load_json(args.blueprint)
    if args.initialize_state:
        state=initialize_state(blueprint)
    elif args.state:
        state=load_json(args.state)
    else:
        raise SystemExit("LOOP_STATE_REQUIRED")

    if args.receipt:
        if args.expected_revision is None:
            raise SystemExit("LOOP_EXPECTED_REVISION_REQUIRED")
        state=apply_receipt(blueprint,state,load_json(args.receipt),expected_revision=args.expected_revision)

    result=evaluate(
        blueprint,state,
        registry=load_json(REGISTRY_PATH),
        snapshot=load_json(SNAPSHOT_PATH),
    )
    output={"state":state,"evaluation":result}
    if args.materialize_next:
        path=materialize_next_package(result,args.materialize_next)
        output["materialized_package"]=str(path.relative_to(ROOT)) if path else None
    print(json.dumps(output,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
