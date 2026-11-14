"""Attest the configured installation-token signer before a governed CUG run."""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request

CUG_APP_ID = 5417646


def _part(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def sign_jwt(client_id: str, private_key: str, *, now: int) -> str:
    if not client_id or not private_key:
        raise ValueError("CUG_CONFIGURATION_REQUIRED")
    payload = {"iss": client_id, "iat": now - 30, "exp": now + 300}
    header = _part(b'{"alg":"RS256","typ":"JWT"}')
    unsigned = f"{header}.{_part(json.dumps(payload, separators=(',', ':')).encode())}"
    with tempfile.TemporaryDirectory(prefix="grt-cug-") as tmp:
        key_file = Path(tmp) / "key.pem"
        fd = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(private_key.replace("\\n", "\n"))
        result = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", str(key_file)],
            input=unsigned.encode(), capture_output=True, check=False, timeout=10,
        )
        if result.returncode != 0:
            raise ValueError("CUG_SIGNER_INVALID")
    return f"{unsigned}.{_part(result.stdout)}"


def verify_identity(metadata: dict, client_id: str, bot_login: str) -> None:
    slug = metadata.get("slug")
    if (metadata.get("id") != CUG_APP_ID or metadata.get("client_id") != client_id
            or not isinstance(slug, str) or not slug or bot_login != f"{slug}[bot]"):
        raise ValueError("CUG_APP_IDENTITY_MISMATCH")


def main() -> None:
    client_id = os.getenv("GOVERNED_CUG_APP_CLIENT_ID", "")
    key = os.getenv("GOVERNED_CUG_APP_PRIVATE_KEY", "")
    try:
        token = sign_jwt(client_id, key, now=int(time.time()))
        request = urllib.request.Request("https://api.github.com/app", headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "governed-cug-app-identity",
        })
        with urllib.request.urlopen(request, timeout=15) as response:
            verify_identity(json.load(response), client_id, os.getenv("GOVERNED_CUG_BOT_LOGIN", ""))
    except ValueError as error:
        raise SystemExit(str(error) if str(error) in {
            "CUG_CONFIGURATION_REQUIRED", "CUG_SIGNER_INVALID", "CUG_APP_IDENTITY_MISMATCH",
        } else "CUG_APP_IDENTITY_UNVERIFIED") from None
    except (OSError, subprocess.SubprocessError):
        raise SystemExit("CUG_APP_IDENTITY_UNVERIFIED") from None
    print(f"CUG_APP_IDENTITY_VERIFIED={CUG_APP_ID}")


if __name__ == "__main__":
    main()
