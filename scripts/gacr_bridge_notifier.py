#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from gacr_continuity_bus import STATE_PATH as CONTINUITY_PATH
from gacr_continuity_bus import mark_delivery_docs, mark_supervision_delivery_docs, read_json as read_continuity_json, write_json as write_continuity_json

ROOT=Path(__file__).resolve().parents[1]
GOV=ROOT/".governance"
TEMPLATE_SOURCE=(ROOT/".template-source").exists()
DISPATCHES_PATH=(
    GOV/"control-plane-state"/"gacr-dispatches.json"
    if TEMPLATE_SOURCE
    else GOV/"agent-relay"/"dispatches.json"
)


def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0)


def read_json(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path:Path,value:dict)->None:
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")


def build_payload(repository:str, item:dict)->dict:
    if item.get("dispatch_kind")=="CONTINUITY_SUPERVISION_ALERT":
        return {
            "schema_version":"1.0.0",
            "event":"GACR_CONTINUITY_EARLY_SUPERVISION_ALERT",
            "dispatch_id":item["dispatch_id"],
            "repository":repository,
            "target_session_id":item["target_session_id"],
            "target_client_instance_id":item.get("target_client_instance_id"),
            "bridge_registration_ref":item.get("bridge_registration_ref"),
            "continuity":{
                "continuity_id":item.get("continuity_id"),
                "supervision_alert_id":item.get("supervision_alert_id"),
                "scope_id":item.get("scope_id"),
                "payload_ref":item.get("payload_ref"),
                "projection_only":True,
                "changes_session_status":False,
                "changes_lease":False,
                "grants_mutation_authority":False,
            },
            "delivery":{"idempotency_key":item["dispatch_id"],"requires_context_fetch":True,"may_write":False},
        }
    if item.get("dispatch_kind")=="CONTINUITY_EVENT":
        return {
            "schema_version":"1.0.0",
            "event":"GACR_CONTINUITY_EVENT",
            "dispatch_id":item["dispatch_id"],
            "repository":repository,
            "target_session_id":item["target_session_id"],
            "target_client_instance_id":item.get("target_client_instance_id"),
            "bridge_registration_ref":item.get("bridge_registration_ref"),
            "continuity":{
                "continuity_id":item.get("continuity_id"),
                "event_id":item.get("continuity_event_id"),
                "sequence":item.get("continuity_sequence"),
                "correlation_id":item.get("correlation_id"),
                "reply_to_event_id":item.get("reply_to_event_id"),
                "event_kind":item.get("event_kind"),
                "payload_ref":item.get("payload_ref"),
                "requires_ack":bool(item.get("requires_ack")),
                "observed_head_sha":item.get("observed_head_sha"),
                "scope_id":item.get("scope_id"),
                "collision_domains":item.get("collision_domains") or [],
                "expires_at":item.get("expires_at"),
                "projection_only":True,
                "grants_mutation_authority":False,
            },
            "delivery":{
                "idempotency_key":item["dispatch_id"],
                "requires_context_fetch":True,
                "may_write":False,
            },
        }
    return {
        "schema_version":"1.0.0",
        "event":"GACR_TAKEOVER_READY",
        "dispatch_id":item["dispatch_id"],
        "repository":repository,
        "target_session_id":item["target_session_id"],
        "target_client_instance_id":item.get("target_client_instance_id"),
        "bridge_registration_ref":item.get("bridge_registration_ref"),
        "task_id":item.get("task_id"),
        "branch":item.get("branch"),
        "pull_request":item.get("pull_request"),
        "takeover_id":item["takeover_id"],
        "stalled_session_id":item["stalled_session_id"],
        "delivery":{"idempotency_key":item["dispatch_id"],"requires_context_fetch":True,"may_write":False},
    }


def eligible(items:list[dict])->list[dict]:
    return [
        item for item in items
        if item.get("status")=="READY"
        and item.get("dispatch_kind") in {None,"TAKEOVER","CONTINUITY_EVENT","CONTINUITY_SUPERVISION_ALERT"}
        and "EXTERNAL_BRIDGE" in (item.get("delivery_modes") or [])
        and (
            item.get("dispatch_kind") not in {"CONTINUITY_EVENT","CONTINUITY_SUPERVISION_ALERT"}
            or item.get("preferred_delivery_mode") in {None,"EXTERNAL_BRIDGE"}
        )
    ]


def deliver(url:str, token:str, payload:dict)->int:
    body=json.dumps(payload,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    request=urllib.request.Request(
        url, method="POST", data=body,
        headers={"Content-Type":"application/json","Authorization":f"Bearer {token}","User-Agent":"gacr-bridge-notifier/1.1","X-GACR-Dispatch-Id":payload["dispatch_id"]},
    )
    try:
        with urllib.request.urlopen(request,timeout=10) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GACR bridge returned HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("GACR bridge delivery failed") from exc


def main()->None:
    url=(os.environ.get("GACR_BRIDGE_WEBHOOK_URL") or "").strip()
    token=(os.environ.get("GACR_BRIDGE_WEBHOOK_TOKEN") or "").strip()
    if not url and not token:
        print("GACR_EXTERNAL_BRIDGE_SKIP: not configured")
        return
    if not url or not token:
        raise SystemExit("GACR_EXTERNAL_BRIDGE_CONFIG_INCOMPLETE")

    repository=(os.environ.get("GITHUB_REPOSITORY") or "UNKNOWN_REPOSITORY").strip()
    store=read_json(DISPATCHES_PATH)
    continuity=read_continuity_json(CONTINUITY_PATH,{"schema_version":"1.0.0","revision":0,"items":[]})
    candidates=eligible(store.get("items") or [])
    if not candidates:
        print("GACR_EXTERNAL_BRIDGE_NO_READY_DISPATCH")
        return

    delivered=[]
    fallback=[]
    changed=False
    for item in candidates:
        payload=build_payload(repository,item)
        try:
            status=deliver(url,token,payload)
            if status<200 or status>=300:
                raise RuntimeError(f"GACR bridge returned HTTP {status}")
        except RuntimeError:
            if item.get("dispatch_kind") not in {"CONTINUITY_EVENT","CONTINUITY_SUPERVISION_ALERT"}:
                raise
            item["status"]="FALLBACK_POLL_REQUIRED"
            item["fallback_mode"]="POLL_REPOSITORY"
            if item.get("dispatch_kind")=="CONTINUITY_EVENT":
                mark_delivery_docs(
                    continuity,
                    continuity_id=item["continuity_id"],
                    event_id=item["continuity_event_id"],
                    target_session_id=item["target_session_id"],
                    delivery_state="FALLBACK_POLL_REQUIRED",
                    timestamp=now_utc(),
                    evidence_ref="external-bridge:delivery-failed",
                )
            else:
                mark_supervision_delivery_docs(
                    continuity,
                    continuity_id=item["continuity_id"],
                    alert_id=item["supervision_alert_id"],
                    delivery_state="FALLBACK_POLL_REQUIRED",
                    timestamp=now_utc(),
                    evidence_ref="external-bridge:delivery-failed",
                )
            fallback.append(item["dispatch_id"])
            changed=True
            continue

        item["status"]="DELIVERED"
        item["delivered_at"]=now_utc().isoformat()
        delivered.append(item["dispatch_id"])
        changed=True
        if item.get("dispatch_kind")=="CONTINUITY_EVENT":
            mark_delivery_docs(
                continuity,
                continuity_id=item["continuity_id"],
                event_id=item["continuity_event_id"],
                target_session_id=item["target_session_id"],
                delivery_state="DELIVERED",
                timestamp=now_utc(),
                evidence_ref="external-bridge:delivered",
            )
        elif item.get("dispatch_kind")=="CONTINUITY_SUPERVISION_ALERT":
            mark_supervision_delivery_docs(
                continuity,
                continuity_id=item["continuity_id"],
                alert_id=item["supervision_alert_id"],
                delivery_state="DELIVERED",
                timestamp=now_utc(),
                evidence_ref="external-bridge:delivered",
            )

    if changed:
        store["revision"]=int(store.get("revision",0))+1
        write_json(DISPATCHES_PATH,store)
        write_continuity_json(CONTINUITY_PATH,continuity)

    print(json.dumps({"status":"GACR_EXTERNAL_BRIDGE_DELIVERY_COMPLETE","dispatch_ids":delivered,"fallback_poll_dispatch_ids":fallback,"count":len(delivered)},indent=2))


if __name__=="__main__":
    main()
