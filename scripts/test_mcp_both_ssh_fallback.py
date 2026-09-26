#!/usr/bin/env python3
from __future__ import annotations

from mcp_repository_discovery import summarize_discovery_evidence, unavailable_direct_credential_evidence


def main() -> None:
    evidence = summarize_discovery_evidence({
        "transport": "BOTH",
        "direct_mcp": unavailable_direct_credential_evidence(),
        "ssh_certificate": {"status": "PASS", "authentication": "GITHUB_OIDC_EPHEMERAL_SSH_CERTIFICATE"},
    })
    if evidence["status"] != "PARTIAL" or evidence["degraded"] is not True:
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: degraded BOTH must be PARTIAL")
    if evidence["direct_mcp"]["status"] != "UNAVAILABLE_CREDENTIAL":
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: direct credential absence not preserved")
    if evidence["ssh_certificate"]["status"] != "PASS":
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: SSH evidence lost")

    complete = summarize_discovery_evidence({
        "transport": "BOTH",
        "direct_mcp": {"status": "PASS"},
        "ssh_certificate": {"status": "PASS"},
    })
    if complete["status"] != "PASS" or complete["degraded"] is not False:
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: complete BOTH evidence")

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
        raise SystemExit("BOTH_SSH_FALLBACK_SELFTEST_FAILED: unusable fallback accepted")

    print("BOTH_SSH_FALLBACK_SELFTEST_PASS")


if __name__ == "__main__":
    main()
