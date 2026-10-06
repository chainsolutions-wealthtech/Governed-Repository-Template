#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from provider_first_tool_hook import FirstToolHook, send_dispatch

JsonRequest = Callable[[str, str], tuple[int, Any]]

def _get_json(url: str, token: str) -> tuple[int, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "gscc-governed-github-read-wrapper/1",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        raw = response.read()
        return int(response.status), json.loads(raw.decode("utf-8")) if raw else None

@dataclass
class GovernedGitHubReadConnector:
    repository: str
    provider: str = "chatgpt"
    transport: str = "governed-github-connector"
    identity: dict[str, Any] = field(default_factory=dict)
    token: str | None = None
    api_base: str = "https://api.github.com"
    request_fn: JsonRequest = _get_json
    dispatch_fn: Callable[..., int] = send_dispatch
    state_file: str | None = None
    _first_touch_done: bool = field(default=False, init=False)
    _hook: FirstToolHook = field(default_factory=FirstToolHook, init=False)

    def __post_init__(self) -> None:
        if self.repository.count("/") != 1:
            raise ValueError("repository must use owner/name")
        if self.state_file and Path(self.state_file).exists():
            loaded = json.loads(Path(self.state_file).read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                self._first_touch_done = bool(loaded.get("first_touch_done", False))
                emitted = loaded.get("emitted")
                if isinstance(emitted, dict):
                    self._hook.emitted.update({str(k): bool(v) for k, v in emitted.items()})

    def _persist(self) -> None:
        if not self.state_file:
            return
        Path(self.state_file).write_text(
            json.dumps(
                {
                    "first_touch_done": self._first_touch_done,
                    "emitted": dict(self._hook.emitted),
                },
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )

    def _runtime_token(self) -> str:
        value = (self.token or os.environ.get("GITHUB_TOKEN") or "").strip()
        if not value:
            raise RuntimeError("GitHub transport credential unavailable")
        return value

    def _before_read(self, *, tool_name: str, operation: str, category: str = "READ") -> dict[str, Any]:
        if self._first_touch_done:
            return {
                "status": "FIRST_TOUCH_ALREADY_EMITTED",
                "event_type": "gscc_provider_first_touch",
                "mutation_authority_granted": False,
            }

        event = {
            "provider": self.provider,
            "transport": self.transport,
            "repository": self.repository,
            "identity": {
                "conversation_ref": self.identity.get("conversation_ref", "UNAVAILABLE"),
                "session_ref": self.identity.get("session_ref", "UNAVAILABLE"),
                "connection_ref": self.identity.get("connection_ref", "UNAVAILABLE"),
            },
            "first_tool_call": True,
            "tool_name": tool_name,
            "operation": operation,
            "category": category,
            "success": True,
        }
        result = self._hook.maybe_emit_first_touch(
            event,
            token=self._runtime_token(),
            dispatch_fn=self.dispatch_fn,
        )
        self._first_touch_done = True
        self._persist()
        return result

    def _repo_root(self) -> str:
        owner, name = self.repository.split("/", 1)
        return (
            f"{self.api_base.rstrip('/')}/repos/"
            f"{urllib.parse.quote(owner)}/{urllib.parse.quote(name)}"
        )

    def get_repo(self) -> dict[str, Any]:
        first_touch = self._before_read(
            tool_name="get_repo",
            operation="read_repository_metadata",
        )
        status, payload = self.request_fn(self._repo_root(), self._runtime_token())
        if not 200 <= status < 300:
            raise RuntimeError(f"GitHub get_repo returned HTTP {status}")
        return {
            "first_touch": first_touch,
            "operation": "get_repo",
            "repository": self.repository,
            "http_status": status,
            "result": payload,
        }

    def fetch_file(self, path: str, *, ref: str | None = None) -> dict[str, Any]:
        if not path or path.startswith("/"):
            raise ValueError("path must be repository-relative")
        first_touch = self._before_read(
            tool_name="fetch_file",
            operation="read_repository_file",
        )
        url = f"{self._repo_root()}/contents/{urllib.parse.quote(path, safe='/')}"
        if ref:
            url += "?ref=" + urllib.parse.quote(ref, safe="")
        status, payload = self.request_fn(url, self._runtime_token())
        if not 200 <= status < 300:
            raise RuntimeError(f"GitHub fetch_file returned HTTP {status}")
        return {
            "first_touch": first_touch,
            "operation": "fetch_file",
            "repository": self.repository,
            "path": path,
            "ref": ref,
            "http_status": status,
            "result": payload,
        }
