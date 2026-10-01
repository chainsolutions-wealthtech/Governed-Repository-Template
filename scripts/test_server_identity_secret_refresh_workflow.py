#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WF=ROOT/'.github/workflows/server-identity-secret-refresh.yml'

def main():
    text=WF.read_text(encoding='utf-8')
    required=[
        'workflow_dispatch:',
        'server_identity_secret_refresh',
        '/refresh-server-identity-secret-facts',
        'persist-credentials: false',
        'control_plane_server_identity_secret_metadata.py --server ALL --live',
        'control_plane_server_identity_secret_facts.py',
        '--expected-revision',
        'server-identity-secret-facts.json',
        'actions/create-github-app-token@v3',
        'permission-contents: write',
        'permission-pull-requests: write',
        'Automated governed read-only KBI-04O refresh'
    ]
    for marker in required:
        if marker not in text:
            raise SystemExit(f'KBI_04O_WORKFLOW_TEST_FAILED: missing {marker}')
    forbidden=[
        'actions/upload-artifact',
        'server_connection_coordinates',
        '--execute',
        'permission-administration: write'
    ]
    for marker in forbidden:
        if marker in text:
            raise SystemExit(f'KBI_04O_WORKFLOW_TEST_FAILED: forbidden {marker}')
    normalized=[line.strip() for line in text.splitlines()]
    if 'git add .' in normalized or 'git add --all' in normalized or 'git add -A' in normalized:
        raise SystemExit('KBI_04O_WORKFLOW_TEST_FAILED: broad git add forbidden')
    before_permissions=text.split('permissions:',1)[0]
    if 'schedule:' in before_permissions:
        raise SystemExit('KBI_04O_WORKFLOW_TEST_FAILED: refresh must be event/need based')
    if 'GOVERNED_MCP_AUTH_TOKEN' not in text:
        raise SystemExit('KBI_04O_WORKFLOW_TEST_FAILED: runtime MCP credential missing')
    print('KBI_04O_WORKFLOW_TEST_PASS')

if __name__=='__main__':
    main()
