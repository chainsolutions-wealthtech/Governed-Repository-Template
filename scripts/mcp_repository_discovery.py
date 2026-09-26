#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from local_governed_entry import record_mcp_discovery
from local_entry_issue_bridge import api, extract_state, persist, render

DIRECT_TO_SSH = {
    "ping": "ping",
    "get_project_context": "project-context",
    "list_domains_s1": "list-domains-s1",
    "list_domains_s2": "list-domains-s2",
    "get_write_tools_context": "write-tools-context",
}
SSH_OIDC_AUDIENCE = "https://mcp.wealthtechinnovations.com/access/github/repository-ssh"
SSH_BROKER_BASE_URL = "https://mcp.wealthtechinnovations.com"
REQUIRED_DISCOVERY_TOOLS = ("ping", "get_project_context")


def parse_mcp_body(raw: str):
    raw = raw.strip()
    if not raw:
        return {}
    if raw.startswith("{"):
        return json.loads(raw)
    events = []
    for line in raw.splitlines():
        if line.startswith("data:"):
            data = line[5:].strip()
            if data:
                try:
                    events.append(json.loads(data))
                except Exception:
                    pass
    return events[-1] if events else {"raw": raw[:12000]}


def post(endpoint, token, payload, session_id=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "governed-repository-mcp-discovery",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    req = urllib.request.Request(
        endpoint,
        method="POST",
        headers=headers,
        data=json.dumps(payload).encode(),
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return (
            parse_mcp_body(response.read().decode(errors="replace")),
            response.headers.get("Mcp-Session-Id") or session_id,
        )


def call_tool(endpoint, token, session_id, idx, name):
    payload = {
        "jsonrpc": "2.0",
        "id": idx,
        "method": "tools/call",
        "params": {"name": name, "arguments": {}},
    }
    result, _ = post(endpoint, token, payload, session_id)
    return result


def discover_direct(endpoint, token):
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "governed-repository-bootstrap", "version": "1.0"},
        },
    }
    init_result, session = post(endpoint, token, initialize)
    try:
        post(
            endpoint,
            token,
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            session,
        )
    except Exception:
        pass

    observed = {}
    for idx, name in enumerate(DIRECT_TO_SSH, start=2):
        try:
            observed[name] = {
                "status": "PASS",
                "result": call_tool(endpoint, token, session, idx, name),
            }
        except Exception as exc:
            observed[name] = {"status": "ERROR", "error": str(exc)[:1000]}
    for required in REQUIRED_DISCOVERY_TOOLS:
        if observed.get(required, {}).get("status") != "PASS":
            raise RuntimeError(f"DIRECT_DISCOVERY_REQUIRED_PROBE_FAILED:{required}")
    status = "PASS" if all(item.get("status") == "PASS" for item in observed.values()) else "PARTIAL"
    return {"status": status, "initialize": init_result, "tools": observed}


def mcp_base_url(endpoint: str) -> str:
    value = endpoint.rstrip("/")
    if value.endswith("/mcp"):
        value = value[:-4]
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise RuntimeError("MCP_ENDPOINT_INVALID")
    return value


def github_oidc_token() -> str:
    request_url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")
    request_token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    if not request_url or not request_token:
        raise RuntimeError("GITHUB_OIDC_CONTEXT_MISSING")
    separator = "&" if "?" in request_url else "?"
    url = request_url + separator + urllib.parse.urlencode({"audience": SSH_OIDC_AUDIENCE})
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"Authorization": f"bearer {request_token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        raw = response.read(32769)
    if len(raw) > 32768:
        raise RuntimeError("GITHUB_OIDC_RESPONSE_TOO_LARGE")
    body = json.loads(raw.decode())
    token = body.get("value")
    if not isinstance(token, str) or not (32 <= len(token) <= 16384):
        raise RuntimeError("GITHUB_OIDC_TOKEN_INVALID")
    return token


def request_ssh_certificate(repository: str, head_sha: str, public_key: str):
    oidc = github_oidc_token()
    try:
        body = json.dumps(
            {"sha": head_sha, "repository": repository, "publicKey": public_key}
        ).encode()
        req = urllib.request.Request(
            SSH_BROKER_BASE_URL + "/access/github/repository-ssh/certificate",
            method="POST",
            headers={
                "Authorization": f"Bearer {oidc}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "governed-repository-ssh-bootstrap",
            },
            data=body,
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read(32769)
    finally:
        oidc = ""
    if len(raw) > 32768:
        raise RuntimeError("SSH_CERTIFICATE_RESPONSE_TOO_LARGE")
    return json.loads(raw.decode())


def validate_ssh_certificate(cert, repository: str, expected_profile: dict):
    if not isinstance(cert, dict):
        raise RuntimeError("SSH_CERTIFICATE_INVALID")
    if cert.get("repository") != repository or cert.get("principal") != "root":
        raise RuntimeError("SSH_CERTIFICATE_IDENTITY_MISMATCH")
    certificate = cert.get("certificate")
    if not isinstance(certificate, str) or not certificate.startswith(
        "ssh-ed25519-cert-v01@openssh.com "
    ):
        raise RuntimeError("SSH_CERTIFICATE_INVALID")
    known_hosts = cert.get("knownHosts")
    if not isinstance(known_hosts, str) or len(known_hosts) > 4096 or "\n" in known_hosts:
        raise RuntimeError("SSH_KNOWN_HOSTS_INVALID")
    if cert.get("mutationAllowed") is not False:
        raise RuntimeError("SSH_CERTIFICATE_MUTATION_NOT_FALSE")
    valid_for = cert.get("validForSeconds")
    if not isinstance(valid_for, int) or valid_for < 1 or valid_for > 600:
        raise RuntimeError("SSH_CERTIFICATE_LIFETIME_INVALID")
    fingerprint = cert.get("fingerprint")
    if not isinstance(fingerprint, str) or not fingerprint.startswith("SHA256:"):
        raise RuntimeError("SSH_CERTIFICATE_FINGERPRINT_INVALID")

    expected_host = expected_profile.get("host")
    expected_user = expected_profile.get("user")
    expected_port = int(expected_profile.get("port", 22))
    if (
        cert.get("host") != expected_host
        or cert.get("username") != expected_user
        or int(cert.get("port", -1)) != expected_port
    ):
        raise RuntimeError("SSH_PROFILE_MISMATCH")

    return {
        "certificate": certificate,
        "known_hosts": known_hosts,
        "fingerprint": fingerprint,
        "valid_for_seconds": valid_for,
        "host": expected_host,
        "username": expected_user,
        "port": expected_port,
    }


def run_ssh_probe(profile, private_key, certificate, known_hosts, command):
    args = [
        "ssh",
        "-i", str(private_key),
        "-o", f"CertificateFile={certificate}",
        "-o", "IdentitiesOnly=yes",
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=yes",
        "-o", f"UserKnownHostsFile={known_hosts}",
        "-o", "PasswordAuthentication=no",
        "-o", "KbdInteractiveAuthentication=no",
        "-o", "ConnectTimeout=10",
        "-p", str(profile["port"]),
        f"{profile['username']}@{profile['host']}",
        command,
    ]
    completed = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    stdout = completed.stdout[:200000]
    stderr = completed.stderr[:4000]
    if completed.returncode != 0:
        raise RuntimeError(f"SSH_PROBE_FAILED:{completed.returncode}:{stderr}")
    try:
        return json.loads(stdout)
    except Exception:
        return {"raw": stdout}


def discover_ssh(repository: str, head_sha: str, profile: dict):
    with tempfile.TemporaryDirectory(prefix="governed-ssh-") as tmp:
        root = pathlib.Path(tmp)
        key = root / "id_ed25519"
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-q", "-N", "", "-f", str(key)],
            check=True,
            timeout=10,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.chmod(key, 0o600)
        public_key = (root / "id_ed25519.pub").read_text(encoding="utf-8").strip()
        cert_raw = request_ssh_certificate(repository, head_sha, public_key)
        cert = validate_ssh_certificate(cert_raw, repository, profile)

        certificate_path = root / "id_ed25519-cert.pub"
        certificate_path.write_text(cert["certificate"] + "\n", encoding="utf-8")
        known_hosts_path = root / "known_hosts"
        known_hosts_path.write_text(cert["known_hosts"] + "\n", encoding="utf-8")

        observed = {}
        for direct_name, ssh_name in DIRECT_TO_SSH.items():
            try:
                observed[direct_name] = {
                    "status": "PASS",
                    "result": run_ssh_probe(
                        cert,
                        key,
                        certificate_path,
                        known_hosts_path,
                        ssh_name,
                    ),
                }
            except Exception as exc:
                observed[direct_name] = {"status": "ERROR", "error": str(exc)[:1000]}

        for required in REQUIRED_DISCOVERY_TOOLS:
            if observed.get(required, {}).get("status") != "PASS":
                raise RuntimeError(f"SSH_DISCOVERY_REQUIRED_PROBE_FAILED:{required}")
        status = "PASS" if all(item.get("status") == "PASS" for item in observed.values()) else "PARTIAL"

        return {
            "status": status,
            "authentication": "GITHUB_OIDC_EPHEMERAL_SSH_CERTIFICATE",
            "broker": SSH_BROKER_BASE_URL,
            "certificate_fingerprint": cert["fingerprint"],
            "valid_for_seconds": cert["valid_for_seconds"],
            "host": cert["host"],
            "port": cert["port"],
            "username": cert["username"],
            "mutationAllowed": False,
            "tools": observed,
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-number", type=int, required=True)
    args = parser.parse_args()

    repository = os.environ["GITHUB_REPOSITORY"]
    issue = api("GET", f"/repos/{repository}/issues/{args.issue_number}")
    state = extract_state(issue.get("body"))
    if (state.get("next_request") or {}).get("kind") != "MCP_DISCOVERY":
        raise SystemExit("MCP_DISCOVERY_SKIPPED")

    expected_head = state.get("expected_head_sha")
    workflow_head = os.environ.get("GITHUB_SHA")
    if not isinstance(expected_head, str) or workflow_head != expected_head:
        raise SystemExit(
            f"HEAD_MOVED: expected={expected_head or 'UNKNOWN'} workflow={workflow_head or 'UNKNOWN'}"
        )

    answers = state.get("answers", {})
    transport = answers.get("mcp_transport")
    endpoint = os.environ.get("GOVERNED_MCP_URL") or answers.get("mcp_endpoint")
    if not isinstance(endpoint, str) or not endpoint:
        raise SystemExit("MCP_ENDPOINT_MISSING")

    observed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    evidence = {
        "transport": transport,
        "endpoint": endpoint,
        "observed_at": observed_at,
        "direct_mcp": None,
        "ssh_certificate": None,
    }

    if transport in {"DIRECT_MCP_TOKEN", "BOTH"}:
        token = os.environ.get("GOVERNED_MCP_AUTH_TOKEN")
        if not token:
            if transport=="DIRECT_MCP_TOKEN":
                raise SystemExit("MCP_DIRECT_CREDENTIAL_MISSING")
            evidence["direct_mcp"] = {
                "status": "UNAVAILABLE_CREDENTIAL",
                "reason": "GOVERNED_MCP_AUTH_TOKEN_MISSING",
                "fallback": "SSH_OIDC_READONLY",
            }
        else:
            evidence["direct_mcp"] = discover_direct(endpoint, token)

    if transport in {"SSH", "BOTH"}:
        profile = answers.get("ssh_connection_profile")
        if not isinstance(profile, dict):
            raise SystemExit("SSH_PROFILE_MISSING")
        evidence["ssh_certificate"] = discover_ssh(
            repository,
            expected_head,
            profile,
        )

    if transport not in {"DIRECT_MCP_TOKEN", "SSH", "BOTH"}:
        raise SystemExit("MCP_TRANSPORT_INVALID")

    components = [
        part for part in (evidence.get("direct_mcp"), evidence.get("ssh_certificate"))
        if isinstance(part, dict)
    ]
    if not components:
        raise SystemExit("MCP_DISCOVERY_NO_EVIDENCE")
    successful = [part for part in components if part.get("status") in {"PASS","PARTIAL"}]
    if not successful:
        raise SystemExit("MCP_DISCOVERY_NO_USABLE_EVIDENCE")
    evidence["status"] = "PASS" if all(part.get("status")=="PASS" for part in components) else "PARTIAL"
    evidence["degraded"] = any(part.get("status")=="UNAVAILABLE_CREDENTIAL" for part in components)

    state2 = record_mcp_discovery(state, evidence)
    persist(args.issue_number, issue.get("body"), state2)
    api(
        "POST",
        f"/repos/{repository}/issues/{args.issue_number}/comments",
        {"body": render(state2)},
    )


if __name__ == "__main__":
    main()
