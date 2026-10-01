#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'scripts'/'governed_agent_continuity_relay.py'
TELEMETRY=ROOT/'scripts'/'gacr_agent_telemetry.py'

def add(args:list[str], flag:str, value):
    if value is None or value=='':
        return
    args.extend([flag,str(value)])

def main():
    event_path=os.environ.get('GITHUB_EVENT_PATH')
    event_name=os.environ.get('GITHUB_EVENT_NAME','')
    event={}
    if event_path and Path(event_path).exists():
        event=json.loads(Path(event_path).read_text(encoding='utf-8'))

    payload={}
    command=None
    if event_name=='schedule':
        command='scan'
    elif event_name=='repository_dispatch':
        action=str(event.get('action') or '')
        command=action.removeprefix('gacr_')
        payload=event.get('client_payload') or {}
    elif event_name=='workflow_dispatch':
        payload=event.get('inputs') or {}
        command=payload.get('command')
    else:
        raise SystemExit(f'GACR_WORKFLOW_BRIDGE_FAILED: unsupported event {event_name}')

    core_commands={'register','heartbeat','scan','status','takeover-plan','takeover-accept'}
    telemetry_commands={'beacon','correlate','dispatch','context','telemetry-status'}
    if command not in core_commands | telemetry_commands:
        raise SystemExit(f'GACR_WORKFLOW_BRIDGE_FAILED: unsupported command {command}')

    if command in telemetry_commands:
        telemetry_command='status' if command=='telemetry-status' else command
        args=[sys.executable,str(TELEMETRY),telemetry_command]
    else:
        args=[sys.executable,str(CORE),command]
    if command=='register':
        add(args,'--agent',payload.get('agent') or os.environ.get('GITHUB_ACTOR') or 'github-actions')
        add(args,'--provider',payload.get('provider') or 'github-actions')
        add(args,'--provider-ref',payload.get('provider_ref'))
        add(args,'--provider-url',payload.get('provider_url'))
        add(args,'--connection-ref',payload.get('connection_ref'))
        add(args,'--repository',payload.get('repository') or os.environ.get('GITHUB_REPOSITORY'))
        add(args,'--observed-head',payload.get('observed_head'))
        add(args,'--branch',payload.get('branch'))
        add(args,'--task-id',payload.get('task_id'))
        add(args,'--pull-request',payload.get('pull_request'))
        add(args,'--client-instance-id',payload.get('client_instance_id'))
        add(args,'--agent-role',payload.get('agent_role'))
        add(args,'--bridge-registration-ref',payload.get('bridge_registration_ref'))
        for capability in str(payload.get('capabilities') or '').split(','):
            capability=capability.strip()
            if capability:
                add(args,'--capability',capability)
        for channel in str(payload.get('wake_channels') or '').split(','):
            channel=channel.strip()
            if channel:
                add(args,'--wake-channel',channel)
        if str(payload.get('standby','')).lower() in {'1','true','yes','on'}:
            args.append('--standby')
    elif command=='heartbeat':
        add(args,'--session-id',payload.get('session_id'))
        add(args,'--observed-head',payload.get('observed_head'))
        add(args,'--action',payload.get('action_label'))
        add(args,'--evidence',payload.get('evidence'))
    elif command=='beacon':
        add(args,'--session-id',payload.get('session_id'))
        add(args,'--event-type',payload.get('event_type') or 'CONNECT')
        add(args,'--provider',payload.get('provider'))
        add(args,'--provider-ref',payload.get('provider_ref'))
        add(args,'--provider-url',payload.get('provider_url'))
        add(args,'--client-instance-id',payload.get('client_instance_id'))
        add(args,'--connection-ref',payload.get('connection_ref'))
        add(args,'--task-id',payload.get('task_id'))
        add(args,'--branch',payload.get('branch'))
        add(args,'--pull-request',payload.get('pull_request'))
        add(args,'--agent-role',payload.get('agent_role'))
        for capability in str(payload.get('capabilities') or '').split(','):
            capability=capability.strip()
            if capability:
                add(args,'--capability',capability)
    elif command=='context':
        add(args,'--session-id',payload.get('session_id'))
    elif command=='takeover-plan':
        add(args,'--stalled-session-id',payload.get('stalled_session_id'))
    elif command=='takeover-accept':
        add(args,'--stalled-session-id',payload.get('stalled_session_id'))
        add(args,'--successor-session-id',payload.get('successor_session_id'))
        add(args,'--reconciled-head',payload.get('reconciled_head'))

    cp=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
    if cp.stdout:
        print(cp.stdout,end='')
    if cp.stderr:
        print(cp.stderr,file=sys.stderr,end='')
    if cp.returncode!=0:
        raise SystemExit(cp.returncode)

    output=os.environ.get('GITHUB_OUTPUT')
    if output:
        with open(output,'a',encoding='utf-8') as fh:
            fh.write(f'command={command}\n')

if __name__=='__main__':
    main()
