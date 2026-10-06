#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "first_touch_expected_field_registry.py"

spec = importlib.util.spec_from_file_location("first_touch_expected_field_registry", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

def main():
    probes = sorted(mod.PROBE_ROOT.glob("*.md"))
    assert len(probes) >= 2, probes

    total_observations = 0
    unique_keys = set()
    per_probe = {}
    for path in probes:
        observations = mod.parse_probe(path)
        per_probe[str(path.relative_to(ROOT))] = len(observations)
        total_observations += len(observations)
        unique_keys.update(mod.norm_key(key) for key, *_ in observations if mod.norm_key(key))

    canonical = {mod.norm_key(x) for x in mod.CANONICAL_CONNECTION_FIELDS}
    assert canonical
    assert canonical.issubset(unique_keys | canonical)

    # PR #195 already established at least 400 normalized Codex observations.
    codex = [
        count for path, count in per_probe.items()
        if "FT-CODEX-PROBE-20261006-01.md" in path
    ]
    assert codex and codex[0] >= 400, codex

    print("FIRST_TOUCH_EXPECTED_FIELD_REGISTRY_TEST_PASS")
    print(f"PROBE_FILES={len(probes)}")
    print(f"TOTAL_NORMALIZED_OBSERVATIONS={total_observations}")
    print(f"UNIQUE_NORMALIZED_FIELD_KEYS={len(unique_keys)}")
    print(f"CANONICAL_CONNECTION_FIELDS={len(canonical)}")
    for path, count in sorted(per_probe.items()):
        print(f"PROBE_OBSERVATIONS {path}={count}")

if __name__ == "__main__":
    main()
