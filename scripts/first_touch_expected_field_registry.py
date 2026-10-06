#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE_ROOT = ROOT / "docs" / "control-plane" / "probes"
OUT = ROOT / ".governance" / "control-plane-state" / "first-touch-expected-field-registry.json"
TOOL_SCHEMA_SNAPSHOT = ROOT / ".governance" / "control-plane-state" / "chatgpt-github-tool-schema-snapshot.json"

CANONICAL_CONNECTION_FIELDS = [
    "request.request_id","request.correlation_id","request.idempotency_key","request.issued_at","request.observed_at",
    "agent.agent_type","agent.provider","agent.requested_role",
    "client.client_instance_id","client.client_type",
    "session.conversation_ref",
    "connection.connection_ref","connection.connection_method","connection.surface_class","connection.wake_channels",
    "target.repository","target.requested_branch",
    "intent.entry_action","intent.connection_intent","intent.requested_capabilities",
    "control_capabilities.heartbeat","control_capabilities.command_receive","control_capabilities.command_ack",
    "control_capabilities.challenge_response","control_capabilities.checkpoint_report","control_capabilities.progress_report",
    "control_capabilities.context_report","control_capabilities.reobserve_head",
    "repository.full_name","repository.id","repository.node_id","repository.owner","repository.default_branch",
    "repository.visibility","repository.private","repository.is_template",
    "github.actor.login","github.actor.id","github.actor.node_id","github.permission",
    "github.installation.id","github.installation.account_login","github.installation.account_id",
    "git.head","git.ref","git.branch",
    "workflow.run_id","workflow.run_number","workflow.run_attempt","workflow.job","workflow.event_type",
    "gacr.session_id","gacr.beacon_id","gacr.correlation_id","gacr.connection_fingerprint",
    "gacr.connection_envelope_digest","gacr.context_digest","gacr.dedupe_key",
    "gacr.session_status","gacr.connected_at","gacr.last_seen_at","gacr.lease_expires_at",
    "gacr.provider_conversation_ref","gacr.provider_conversation_url",
    "task.task_id","claim.claim_id","pull_request.number","checkpoint.ref",
]

STATUS_VALUES = [
    "OBSERVED","DERIVED","UNAVAILABLE","UNKNOWN","NOT_EXPOSED","REDACTED","DENIED","STALE","NOT_APPLICABLE"
]

def norm_key(value: str) -> str:
    value = value.strip().strip(chr(96))
    value = re.sub(r"[^A-Za-z0-9_.:/-]+", "_", value)
    return value.strip("_").lower()

def parse_probe(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    observations = []
    in_code = False
    raw = False
    buf = []
    section = ""
    for idx, line in enumerate(lines, start=1):
        h = re.match(r"^##\s+(?:(?:\d+)\.\s+)?(.+?)\s*$", line)
        if h and not in_code:
            section = h.group(1).strip()
            raw = section.lower() in {"raw inventory","raw anchor inventory"}
            continue
        if line.strip().startswith(chr(96) * 3):
            if in_code and raw:
                vals=[(n,t.strip()) for n,t in buf if t.strip()]
                for j in range(0,len(vals)-1,2):
                    observations.append((vals[j][1], vals[j+1][1], vals[j+1][0], section, "RAW_INVENTORY"))
                buf=[]
            in_code=not in_code
            continue
        if in_code:
            if raw: buf.append((idx,line))
            continue
        m=re.match(r"^[-*>]\s*([^:]+):\s*(.*?)\s*$", line)
        if m:
            observations.append((m.group(1),m.group(2),idx,section,"KEY_VALUE"))
            continue
        m=re.match(r"^([A-Za-z0-9_ /()#.+-]+):\s*$",line)
        if m:
            j=idx
            while j < len(lines) and not lines[j].strip():
                j+=1
            if j < len(lines):
                nxt=lines[j].strip()
                if nxt.startswith(chr(96)) and nxt.endswith(chr(96)):
                    observations.append((m.group(1),nxt,j+1,section,"LABEL_VALUE"))
    return observations

def main():
    fields={}
    probe_paths=sorted(PROBE_ROOT.glob("*.md"))
    parsed_probes={p: parse_probe(p) for p in probe_paths}
    tool_rows=[]
    if TOOL_SCHEMA_SNAPSHOT.exists():
        tool_rows=json.loads(TOOL_SCHEMA_SNAPSHOT.read_text(encoding="utf-8")).get("fields", [])

    for p in probe_paths:
        for key,value,line,section,kind in parsed_probes[p]:
            nk=norm_key(key)
            if not nk: continue
            item=fields.setdefault(nk,{
                "field_id":nk,
                "aliases":[],
                "sources":[],
                "expected_status_contract":STATUS_VALUES,
            })
            if key not in item["aliases"]: item["aliases"].append(key)
            item["sources"].append({
                "source_path":str(p.relative_to(ROOT)),
                "source_line":line,
                "section":section,
                "source_kind":kind,
            })
    if tool_rows:
        for row in tool_rows:
            key = str(row.get("field_id") or "")
            nk = norm_key(key)
            if not nk:
                continue
            item = fields.setdefault(nk, {
                "field_id": nk,
                "aliases": [],
                "sources": [],
                "expected_status_contract": STATUS_VALUES,
            })
            if key not in item["aliases"]:
                item["aliases"].append(key)
            item["sources"].append({
                "source_path": str(TOOL_SCHEMA_SNAPSHOT.relative_to(ROOT)),
                "source_line": None,
                "section": "github_tool_schema",
                "source_kind": "TOOL_SCHEMA",
            })

    for key in CANONICAL_CONNECTION_FIELDS:
        nk=norm_key(key)
        item=fields.setdefault(nk,{
            "field_id":nk,
            "aliases":[],
            "sources":[],
            "expected_status_contract":STATUS_VALUES,
        })
        if key not in item["aliases"]: item["aliases"].append(key)
        item["sources"].append({"source_path":"CANONICAL_CONNECTION_FIELDS","source_line":None,"section":"connection","source_kind":"CANONICAL"})
    out={
        "schema":"first-touch-expected-field-registry/v1",
        "purpose":"Every expected first-touch/connection field must have a value or an explicit non-value status; silent absence is not complete.",
        "source_probe_files":[str(p.relative_to(ROOT)) for p in probe_paths],
        "status_values":STATUS_VALUES,
        "probe_observation_count": sum(len(parsed_probes[p]) for p in probe_paths),
        "tool_schema_field_count": len(tool_rows),
        "field_count":len(fields),
        "fields":[fields[k] for k in sorted(fields)],
        "expected_observations": (
            [
                {
                    "observation_id": f"probe:{str(p.relative_to(ROOT))}:{line}:{norm_key(key)}",
                    "field_id": norm_key(key),
                    "source_kind": "PROBE_REFERENCE",
                    "source_path": str(p.relative_to(ROOT)),
                    "source_line": line,
                }
                for p in probe_paths
                for key, value, line, section, kind in parsed_probes[p]
                if norm_key(key)
            ]
            + [
                {
                    "observation_id": f"github_tool:{row.get('tool')}:{row.get('field')}",
                    "field_id": norm_key(str(row.get("field_id") or "")),
                    "source_kind": "TOOL_SCHEMA",
                    "source_path": str(TOOL_SCHEMA_SNAPSHOT.relative_to(ROOT)),
                    "source_line": None,
                }
                for row in tool_rows
                if norm_key(str(row.get("field_id") or ""))
            ]
            + [
                {
                    "observation_id": f"canonical:{norm_key(key)}",
                    "field_id": norm_key(key),
                    "source_kind": "CANONICAL_CONNECTION_FIELD",
                    "source_path": "CANONICAL_CONNECTION_FIELDS",
                    "source_line": None,
                }
                for key in CANONICAL_CONNECTION_FIELDS
            ]
        ),
        "authority_granted":False,
    }
    out["expected_observation_count"] = len(out["expected_observations"])
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"EXPECTED_FIELD_REGISTRY_BUILT","field_count":len(fields),"expected_observation_count":out["expected_observation_count"],"output":str(OUT)},indent=2))

if __name__=="__main__":
    main()
