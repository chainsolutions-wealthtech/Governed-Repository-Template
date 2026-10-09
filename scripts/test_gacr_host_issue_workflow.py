#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "governed-agent-continuity-relay.yml"
UPGRADER = ROOT / "scripts" / "control_plane_upgrade_local_entry.py"


def assert_true(value, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert_true("issue_comment:" in text, "issue_comment trigger missing")
    assert_true("github.event.issue.number == 115" not in text, "source issue number must not be hard-coded in generic workflow")
    assert_true("startsWith(github.event.comment.body, '/gacr-host ')" in text, "host ingress prefix gate missing")

    reconcile = text.index("Reconcile relay ingress to latest default branch")
    capture = text.index("Capture exact base HEAD")
    execute = text.index("Execute GACR command")
    persist = text.index("Persist changed relay state")
    assert_true(reconcile < capture < execute < persist, "relay ingress reconciliation must precede base capture and execution")
    reconcile_block = text[reconcile:capture]
    assert_true(
        "github.event_name == 'issue_comment' || github.event_name == 'repository_dispatch'"
        in reconcile_block,
        "issue_comment and repository_dispatch must share live default-branch reconciliation",
    )
    assert_true('git fetch origin "$DEFAULT_BRANCH"' in text, "latest default branch fetch missing")
    assert_true("git checkout --detach FETCH_HEAD" in reconcile_block, "reconciled relay ingress must execute from fetched default-branch head")
    assert_true("scripts/gacr_host_issue_ingress.py" in text, "host ingress adapter compile validation missing")

    control_delivery = "Deliver pending GSCC control commands"
    delivery_reconcile = "Reconcile continuity delivery projection"
    assert_true(control_delivery in text, "GSCC control command delivery step missing")
    assert_true(delivery_reconcile in text, "continuity delivery reconciliation step missing")
    assert_true(
        text.index(control_delivery) < text.index(delivery_reconcile) < persist,
        "control delivery must be projected back into continuity state before persistence",
    )
    assert_true(
        "startsWith(github.event.comment.body, '/gscc-control ')" in text,
        "live GSCC issue control request must remain admitted by the workflow gate",
    )

    upgrader = UPGRADER.read_text(encoding="utf-8")
    assert_true('host_bridge["issue_number"]=None' in upgrader, "client upgrade must clear source host issue number")
    assert_true('host_bridge["source_issue_number_distributed"]=False' in upgrader, "client upgrade must mark source issue number non-distributed")
    assert_true('TITLE_FALLBACK_UNTIL_LOCAL_NUMBER_BOUND' in upgrader, "client title fallback strategy missing")

    print("GACR_HOST_ISSUE_WORKFLOW_TEST_PASS")


if __name__ == "__main__":
    main()
