from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from typing import Any

from .protocol import MessageEnvelope, assert_secretless


class TransportError(RuntimeError):
    pass


class Transport(ABC):
    @abstractmethod
    def send(self, message: MessageEnvelope) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def receive(self, *, target: dict[str, Any] | None = None) -> list[MessageEnvelope]:
        raise NotImplementedError


class InMemoryTransport(Transport):
    def __init__(self) -> None:
        self.sent: list[MessageEnvelope] = []
        self.inbox: list[MessageEnvelope] = []

    def send(self, message: MessageEnvelope) -> dict[str, Any]:
        message.validated()
        self.sent.append(message)
        return {"status": "DISPATCHED", "message_id": message.message_id}

    def receive(self, *, target: dict[str, Any] | None = None) -> list[MessageEnvelope]:
        if target is None:
            items = list(self.inbox)
            self.inbox.clear()
            return items
        kept: list[MessageEnvelope] = []
        matched: list[MessageEnvelope] = []
        for item in self.inbox:
            if all(item.target.get(key) == value for key, value in target.items()):
                matched.append(item)
            else:
                kept.append(item)
        self.inbox = kept
        return matched

    def inject(self, message: MessageEnvelope) -> None:
        self.inbox.append(message.validated())


class GitHubDispatchTransport(Transport):
    EVENT_BY_KIND = {
        "EVENT": "gscc_event",
        "COMMAND": "gscc_command",
        "ACK": "gscc_ack",
        "CAPABILITIES": "gscc_capabilities",
    }

    def __init__(
        self,
        repository: str,
        *,
        token: str | None = None,
        api_base: str = "https://api.github.com",
        request_fn: Callable[..., tuple[int, bytes]] | None = None,
        receive_fn: Callable[[dict[str, Any] | None], Iterable[dict[str, Any] | MessageEnvelope]] | None = None,
    ) -> None:
        parts = repository.split("/")
        if len(parts) != 2 or not all(parts):
            raise ValueError("repository must use owner/name")
        self.repository = repository
        self._token = token
        self.api_base = api_base.rstrip("/")
        self.request_fn = request_fn or self._request
        self.receive_fn = receive_fn

    def _request(self, method: str, url: str, body: dict[str, Any]) -> tuple[int, bytes]:
        if not self._token:
            raise TransportError("GitHub transport credential unavailable")
        encoded = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url,
            method=method,
            data=encoded,
            headers={
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._token}",
                "User-Agent": "gscc-github-transport/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return int(response.status), response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise TransportError(f"GitHub dispatch HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise TransportError("GitHub dispatch unavailable") from exc

    def send(self, message: MessageEnvelope) -> dict[str, Any]:
        message.validated()
        payload = message.to_dict()
        assert_secretless(payload)
        event_type = self.EVENT_BY_KIND[message.kind]
        body = {"event_type": event_type, "client_payload": payload}
        owner, name = self.repository.split("/", 1)
        url = f"{self.api_base}/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(name)}/dispatches"
        status, _ = self.request_fn("POST", url, body)
        if not 200 <= status < 300:
            raise TransportError(f"GitHub repository_dispatch returned HTTP {status}")
        return {
            "status": "DISPATCHED",
            "http_status": status,
            "event_type": event_type,
            "message_id": message.message_id,
        }

    def receive(self, *, target: dict[str, Any] | None = None) -> list[MessageEnvelope]:
        if self.receive_fn is None:
            raise TransportError(
                "GitHub repository_dispatch is send-only from the client perspective; "
                "configure a governed poll/ingress receive_fn for bidirectional delivery"
            )
        items = self.receive_fn(target)
        result: list[MessageEnvelope] = []
        for item in items:
            result.append(item if isinstance(item, MessageEnvelope) else MessageEnvelope.from_dict(item))
        return result
