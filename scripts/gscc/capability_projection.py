from __future__ import annotations

import copy
from typing import Any

PORTABLE_SCHEMA = "gscc-portable-capability-projection/v1"


def build_portable_capability_projection(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise ValueError("CAPABILITY_SNAPSHOT_OBJECT_REQUIRED")
    if snapshot.get("status") != "CURRENT":
        raise ValueError("CAPABILITY_SNAPSHOT_CURRENT_REQUIRED")

    catalogue = snapshot.get("catalogue")
    if not isinstance(catalogue, dict) or catalogue.get("status") != "CURRENT":
        raise ValueError("CAPABILITY_CATALOGUE_CURRENT_REQUIRED")

    refresh_policy = snapshot.get("refresh_policy")
    if not isinstance(refresh_policy, dict):
        refresh_policy = {}

    return {
        "schema": PORTABLE_SCHEMA,
        "status": "CURRENT",
        "scope": "PORTABLE_CLIENT_PROJECTION",
        "source_authority_id": snapshot.get("authority_id"),
        "source_observed_at": snapshot.get("observed_at"),
        "source_catalogue_digest": catalogue.get("catalogue_digest"),
        "refresh_policy": copy.deepcopy(refresh_policy),
        "catalogue": copy.deepcopy(catalogue),
    }
