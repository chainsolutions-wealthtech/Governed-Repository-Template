#!/usr/bin/env python3
from __future__ import annotations

from mcp_repository_discovery import (
    SshProfileMismatch,
    summarize_discovery_evidence,
    unavailable_direct_credential_evidence,
    validate_ssh_certificate,
)


def main() -> None:
    fallback = summarize_discovery_evidence({
        "transport": "BOTH",
        "routing_mode": "DUAL_READY_SMART_ROUTING",
        "direct_mcp": unavailable_direct_credential_evidence(),
        "ssh_certificate": {"status": "PASS", "authentication": "GITHUB_OIDC_EPHEMERAL_SSH_CERTIFICATE"},
    })
    if fallback["status"] != "PASS" or fallback["selected_transport"] != "SSH":
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: successful fallback must satisfy discovery")
    if fallback["fallback_used"] is not True or fallback["simultaneous_execution_required"] is not False:
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: BOTH smart routing semantics")
    if fallback["direct_mcp"]["status"] != "UNAVAILABLE_CREDENTIAL":
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: direct credential absence not preserved")

    direct = summarize_discovery_evidence({
        "transport": "BOTH",
        "routing_mode": "DUAL_READY_SMART_ROUTING",
        "selected_transport": "DIRECT_MCP_TOKEN",
        "direct_mcp": {"status": "PASS"},
        "ssh_certificate": {
            "status": "CONFIGURED_NOT_ATTEMPTED",
            "reason": "ALTERNATE_ROUTE_NOT_REQUIRED_FOR_THIS_DISCOVERY",
        },
    })
    if direct["status"] != "PASS" or direct["selected_transport"] != "DIRECT_MCP_TOKEN":
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: direct route selection")
    if direct["fallback_used"] is not False or direct["alternate_transport_status"] != "CONFIGURED_NOT_ATTEMPTED":
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: alternate SSH must not be required after direct success")

    complete = summarize_discovery_evidence({
        "transport": "BOTH",
        "direct_mcp": {"status": "PASS"},
        "ssh_certificate": {"status": "PASS"},
    })
    if complete["status"] != "PASS" or complete["selected_transport"] != "DIRECT_MCP_TOKEN":
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: legacy dual-pass evidence should prefer direct without coupling")

    direct_failed_fallback = summarize_discovery_evidence({
        "transport": "BOTH",
        "direct_mcp": {"status": "ERROR", "failure_code": "DIRECT_TEMPORARY_FAILURE"},
        "ssh_certificate": {"status": "PASS"},
    })
    if direct_failed_fallback["status"] != "PASS" or direct_failed_fallback["selected_transport"] != "SSH":
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: SSH fallback after direct failure")
    if direct_failed_fallback["fallback_used"] is not True:
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: fallback usage not recorded")

    certificate={
        "repository":"owner/repo",
        "principal":"root",
        "certificate":"ssh-ed25519-cert-v01@openssh.com TEST",
        "knownHosts":"212.227.212.33 ssh-ed25519 AAAATEST",
        "mutationAllowed":False,
        "validForSeconds":600,
        "fingerprint":"SHA256:TEST",
        "host":"212.227.212.33",
        "port":22,
        "username":"root"
    }
    try:
        validate_ssh_certificate(certificate,"owner/repo",{"host":"mcp.example.test","port":22,"user":"root"})
    except SshProfileMismatch as exc:
        if exc.observed_profile!={"host":"212.227.212.33","port":22,"user":"root","source":"SIGNED_MCP_SSH_BROKER_RESPONSE"}:
            raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: signed broker profile evidence mismatch")
    else:
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: SSH profile mismatch not classified")

    try:
        summarize_discovery_evidence({
            "transport": "BOTH",
            "direct_mcp": unavailable_direct_credential_evidence(),
            "ssh_certificate": {"status": "ERROR"},
        })
    except RuntimeError as exc:
        if str(exc) != "MCP_DISCOVERY_NO_USABLE_EVIDENCE":
            raise
    else:
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: unusable routes accepted")

    print("BOTH_SSH_FALLBACK_SELFTEST_PASS")


if __name__ == "__main__":
    main()
