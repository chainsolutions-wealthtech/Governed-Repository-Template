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
CAPACITY=ROOT/'scripts'/'gacr_capacity_dispatch.py'
AUTO_ATTACH=ROOT/'scripts'/'gacr_auto_attach.py'
HOST_INGRESS=ROOT/'scripts'/'gacr_host_issue_ingress.py'
CONTROL_INGRESS=ROOT/'scripts'/'gscc_control_issue_ingress.py'
CONTROL_BRIDGE=ROOT/'scripts'/'gscc_gacr'/'issue_control_bridge.py'

def add(args:list[str], flag:str, value):
    if value is None or value=='':
        return
    args.extend([flag,str(value)])

AUTO_ATTACH_ARRIVAL_CONTEXT_KEYS={
    'repository','repository_id','organization','git_provider','github_actor',
    'github_app_installation','observed_head','branch','base_branch','pull_request',
    'workflow_run_id','job_id','run_attempt','event_type','delivery_correlation_id',
    'last_action','last_evidence','entry_action','connection_intent','task_id',
    'claim_id','heartbeat_seq','checkpoint'
}

def expand_auto_attach_payload(payload:dict)->dict:
    result=dict(payload or {})
    nested=result.pop('arrival_context',None)
    if nested is None:
        return result
    if not isinstance(nested,dict):
        raise ValueError('arrival_context must be an object')
    for key in AUTO_ATTACH_ARRIVAL_CONTEXT_KEYS:
        if key not in result and nested.get(key) not in (None,''):
            result[key]=nested[key]
    return result

def main():
    event_path=os.environ.get('GITHUB_EVENT_PATH')
    event_name=os.environ.get('GITHUB_EVENT_NAME','')
    event={}
    if event_path and Path(event_path).exists():
        event=json.loads(Path(event_path).read_text(encoding='utf-8'))

    payload={}
    command=None
    if event_name=='issue_comment':
        body=str(((event.get('comment') or {}).get('body') or ''))
        ingress=CONTROL_INGRESS if body.startswith('/gscc-control ') else HOST_INGRESS
        cp=subprocess.run([sys.executable,str(ingress)],cwd=ROOT,text=True,capture_output=True)
        if cp.stdout:
            print(cp.stdout,end='')
        if cp.stderr:
            print(cp.stderr,file=sys.stderr,end='')
        if cp.returncode!=0:
            raise SystemExit(cp.returncode)
        output=os.environ.get('GITHUB_OUTPUT')
        if output:
            with open(output,'a',encoding='utf-8') as fh:
                fh.write('command=host-issue-event\\n')
        return
    if event_name=='schedule':
        command='scan'
    elif event_name=='push':
        command='auto-attach'
        payload={'allow_unobservable_skip': True}
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
    telemetry_commands={'beacon','correlate','dispatch','context','forensics','telemetry-status'}
    capacity_commands={'pool','plan-work','dispatch-work','work-offer-accept'}
    auto_attach_commands={'auto-attach'}
    control_commands={'control-challenge'}
    if command not in core_commands | telemetry_commands | capacity_commands | auto_attach_commands | control_commands:
        raise SystemExit(f'GACR_WORKFLOW_BRIDGE_FAILED: unsupported command {command}')

    if command in control_commands:
        args=[sys.executable,str(CONTROL_BRIDGE),'challenge']
    elif command in telemetry_commands:
        telemetry_command='status' if command=='telemetry-status' else command
        args=[sys.executable,str(TELEMETRY),telemetry_command]
    elif command in capacity_commands:
        capacity_command='accept-work' if command=='work-offer-accept' else command
        args=[sys.executable,str(CAPACITY),capacity_command]
    elif command in auto_attach_commands:
        args=[sys.executable,str(AUTO_ATTACH)]
    else:
        args=[sys.executable,str(CORE),command]
    if command=='control-challenge':
        add(args,'--session-id',payload.get('session_id'))
        add(args,'--ttl-seconds',payload.get('ttl_seconds'))
    elif command=='auto-attach':
        payload=expand_auto_attach_payload(payload)
        add(args,'--agent',payload.get('agent'))
        add(args,'--provider',payload.get('provider'))
        add(args,'--provider-ref',payload.get('provider_ref'))
        add(args,'--provider-url',payload.get('provider_url'))
        add(args,'--connection-ref',payload.get('connection_ref'))
        add(args,'--client-instance-id',payload.get('client_instance_id'))
        add(args,'--bridge-registration-ref',payload.get('bridge_registration_ref'))
        add(args,'--repository',payload.get('repository') or os.environ.get('GITHUB_REPOSITORY'))
        add(args,'--repository-id',payload.get('repository_id'))
        add(args,'--organization',payload.get('organization'))
        add(args,'--git-provider',payload.get('git_provider'))
        add(args,'--github-actor',payload.get('github_actor'))
        add(args,'--github-app-installation',payload.get('github_app_installation'))
        add(args,'--connection-method',payload.get('connection_method'))
        add(args,'--surface-class',payload.get('surface_class'))
        add(args,'--agent-type-model',payload.get('agent_type_model'))
        add(args,'--permissions-json',payload.get('permissions_json'))
        add(args,'--observed-head',payload.get('observed_head'))
        add(args,'--branch',payload.get('branch'))
        add(args,'--base-branch',payload.get('base_branch'))
        add(args,'--task-id',payload.get('task_id'))
        add(args,'--claim-id',payload.get('claim_id'))
        add(args,'--pull-request',payload.get('pull_request'))
        add(args,'--workflow-run-id',payload.get('workflow_run_id'))
        add(args,'--job-id',payload.get('job_id'))
        add(args,'--run-attempt',payload.get('run_attempt'))
        add(args,'--event-type',payload.get('event_type'))
        add(args,'--delivery-correlation-id',payload.get('delivery_correlation_id'))
        add(args,'--observed-at',payload.get('observed_at'))
        add(args,'--heartbeat-seq',payload.get('heartbeat_seq'))
        add(args,'--checkpoint',payload.get('checkpoint'))
        add(args,'--last-action',payload.get('last_action'))
        add(args,'--last-evidence',payload.get('last_evidence'))
        add(args,'--entry-action',payload.get('entry_action'))
        add(args,'--connection-intent',payload.get('connection_intent'))
        add(args,'--agent-role',payload.get('agent_role'))
        add(args,'--source',payload.get('source'))
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
        if str(payload.get('prefer_chronicle','')).lower() in {'1','true','yes','on'}:
            args.append('--prefer-chronicle')
        if str(payload.get('allow_unobservable_skip','')).lower() in {'1','true','yes','on'}:
            args.append('--allow-unobservable-skip')
    elif command=='register':
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
        add(args,'--source',payload.get('source'))
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
        add(args,'--entry-purpose',payload.get('entry_purpose'))
        add(args,'--work-kind',payload.get('work_kind'))
        for capability in str(payload.get('capabilities') or '').split(','):
            capability=capability.strip()
            if capability:
                add(args,'--capability',capability)
        add(args,'--action-id',payload.get('action_id')); add(args,'--action-label',payload.get('action_label')); add(args,'--action-phase',payload.get('action_phase'))
        add(args,'--tool-name',payload.get('tool_name')); add(args,'--tool-call-id',payload.get('tool_call_id')); add(args,'--outcome',payload.get('outcome')); add(args,'--written-head',payload.get('written_head'))
        add(args,'--checkpoint-ref',payload.get('checkpoint_ref')); add(args,'--evidence-ref',payload.get('evidence_ref')); add(args,'--interruption-code',payload.get('interruption_code'))
        add(args,'--availability-state',payload.get('availability_state'))
        add(args,'--availability-reason-code',payload.get('availability_reason_code'))
    elif command=='work-offer-accept':
        add(args,'--dispatch-id',payload.get('dispatch_id'))
        add(args,'--session-id',payload.get('session_id'))
    elif command=='context':
        add(args,'--session-id',payload.get('session_id'))
    elif command=='forensics':
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