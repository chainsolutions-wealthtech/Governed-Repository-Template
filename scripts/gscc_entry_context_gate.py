#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from gscc.entry_gate import complete_entry_context


def _parse_post_json(raw: str | None) -> dict[str, Any]:
    if raw is None or not raw.strip():
        return {}
    value = json.loads(raw)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("entry POST payload must be a JSON object")
    return value


def _repository_get_context(
    *,
    repository: str,
    default_branch: str,
    requested_ref: str,
    observed_head_sha: str,
) -> dict[str, Any]:
    parts = repository.split("/", 1)
    if len(parts) != 2 or not all(parts):
        raise ValueError("repository must use owner/name")
    owner, name = parts
    for field_name, value in (
        ("default_branch", default_branch),
        ("requested_ref", requested_ref),
        ("observed_head_sha", observed_head_sha),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be non-empty")
    return {
        "repository": repository,
        "repository_owner": owner,
        "repository_name": name,
        "default_branch": default_branch,
        "requested_ref": requested_ref,
        "observed_head_sha": observed_head_sha,
    }


def _write_output(name: str, value: Any) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    rendered = str(value).lower() if isinstance(value, bool) else str(value)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"{name}={rendered}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="GSCC closed-until-complete entry context gate")
    parser.add_argument("--post-json", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--default-branch", required=True)
    parser.add_argument("--requested-ref", required=True)
    parser.add_argument("--observed-head", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--require-open", action="store_true")
    args = parser.parse_args()

    receipt = complete_entry_context(
        post_data=_parse_post_json(args.post_json),
        get_data=_repository_get_context(
            repository=args.repository,
            default_branch=args.default_branch,
            requested_ref=args.requested_ref,
            observed_head_sha=args.observed_head,
        ),
    )
    Path(args.output).write_text(
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_output("entry_open", receipt["entry_open"])
    _write_output("entry_receipt", receipt.get("entry_receipt") or "")
    _write_output("context_digest", receipt["context_digest"])
    _write_output("missing_required", ",".join(receipt["missing_required"]))
    print(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False))
    if args.require_open and not receipt["entry_open"]:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
