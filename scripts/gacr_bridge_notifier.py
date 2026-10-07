#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GOV=ROOT/".governance"
TEMPLATE_SOURCE=(ROOT/".template-source").exists()
DISPATCHES_PATH=(
    GOV/"control-plane-state"/"gacr-dispatches.json"
    if TEMPLATE_SOURCE
    else GOV/"agent-relay"/"dispatches.json"
)


def read_json(path:Path)->dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(repository:str, item:dict)->dict:
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
        "delivery":{
            "idempotency_key":item["dispatch_id"],
            "requires_context_fetch":True,
            "may_write":False,
        },
    }


def eligible(items:list[dict])->list[dict]:
    return [
        item for item in items
        if item.get("status")=="READY"
        and item.get("dispatch_kind") in {None, "TAKEOVER"}
        and "EXTERNAL_BRIDGE" in (item.get("delivery_modes") or [])
    ]


def deliver(url:str, token:str, payload:dict)->int:
    body=json.dumps(payload,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    request=urllib.request.Request(
        url,
        method="POST",
        data=body,
        headers={
            "Content-Type":"application/json",
            "Authorization":f"Bearer {token}",
            "User-Agent":"gacr-bridge-notifier/1.0",
            "X-GACR-Dispatch-Id":payload["dispatch_id"],
        },
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
    candidates=eligible(store.get("items") or [])
    if not candidates:
        print("GACR_EXTERNAL_BRIDGE_NO_READY_DISPATCH")
        return

    delivered=[]
    for item in candidates:
        payload=build_payload(repository,item)
        status=deliver(url,token,payload)
        if status<200 or status>=300:
            raise SystemExit(f"GACR_EXTERNAL_BRIDGE_HTTP_{status}")
        delivered.append(item["dispatch_id"])

    print(json.dumps({
        "status":"GACR_EXTERNAL_BRIDGE_DELIVERED",
        "dispatch_ids":delivered,
        "count":len(delivered),
    },indent=2))


if __name__=="__main__":
    main()
