#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / ".governance/control-plane-state/governance-model-execution-blueprint.json"
CATALOGUE = ROOT / ".governance/control-plane-state/governance-model-catalogue.json"
GROUP_ID = re.compile(r"^GMC-G\d{2}$")

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def fail(message: str) -> None:
    raise SystemExit(f"GOVERNANCE_MODEL_INTEGRITY_FAILED: {message}")

def main() -> None:
    blueprint = load(BLUEPRINT)
    catalogue = load(CATALOGUE)
    groups = blueprint.get("groups") or []
    artifacts = blueprint.get("knowledge_artifacts") or []
    edges = blueprint.get("dependency_edges") or []

    if blueprint.get("work_package_count") != len(groups):
        fail("work_package_count does not match groups")
    atomic_count = sum(len(group.get("atomic_tasks") or []) for group in groups)
    if blueprint.get("atomic_task_count") != atomic_count:
        fail("atomic_task_count does not match group atomic tasks")

    group_ids = [group.get("group_id") for group in groups]
    if len(group_ids) != len(set(group_ids)):
        fail("duplicate group_id")
    group_order = {group_id: index for index, group_id in enumerate(group_ids)}

    artifact_by_id = {}
    for artifact in artifacts:
        artifact_id = artifact.get("artifact_id")
        if not artifact_id or artifact_id in artifact_by_id:
            fail(f"duplicate or missing artifact_id: {artifact_id!r}")
        artifact_by_id[artifact_id] = artifact

    expected_consumers = {artifact_id: set() for artifact_id in artifact_by_id}
    expected_edges = set()
    for group in groups:
        group_id = group.get("group_id")
        for dependency in (group.get("dependency_contract") or {}).get("artifact_dependencies") or []:
            artifact_id = dependency.get("artifact_id")
            producer = dependency.get("produced_by")
            if artifact_id not in artifact_by_id:
                fail(f"{group_id} references unknown artifact {artifact_id}")
            canonical_producer = artifact_by_id[artifact_id].get("produced_by")
            if producer != canonical_producer:
                fail(f"{group_id} producer mismatch for {artifact_id}: contract={producer} registry={canonical_producer}")
            expected_consumers[artifact_id].add(group_id)
            expected_edges.add((artifact_id, group_id, producer))

    actual_edges = set()
    for edge in edges:
        if edge.get("edge_type") != "ARTIFACT_DEPENDENCY":
            continue
        triple = (edge.get("from"), edge.get("to"), edge.get("produced_by"))
        if triple in actual_edges:
            fail(f"duplicate ARTIFACT_DEPENDENCY edge: {triple}")
        actual_edges.add(triple)
    if expected_edges != actual_edges:
        fail(f"dependency contract/edge divergence missing={sorted(expected_edges-actual_edges)} extra={sorted(actual_edges-expected_edges)}")

    produced_copy = {}
    for group in groups:
        for artifact in group.get("produced_artifacts") or []:
            artifact_id = artifact.get("artifact_id")
            if artifact_id in produced_copy:
                fail(f"artifact appears in multiple produced_artifacts lists: {artifact_id}")
            produced_copy[artifact_id] = artifact
            if artifact.get("produced_by") != group.get("group_id"):
                fail(f"produced_artifacts producer mismatch for {artifact_id}")
    if set(produced_copy) != set(artifact_by_id):
        fail("produced_artifacts and knowledge_artifacts do not contain identical artifact IDs")

    for artifact_id, artifact in artifact_by_id.items():
        expected = sorted(expected_consumers[artifact_id], key=group_order.get)
        declared = [v for v in artifact.get("consumed_by") or [] if GROUP_ID.fullmatch(v)]
        produced_declared = [v for v in produced_copy[artifact_id].get("consumed_by") or [] if GROUP_ID.fullmatch(v)]
        if declared != expected:
            fail(f"knowledge_artifact consumers diverge for {artifact_id}: {declared} != {expected}")
        if produced_declared != expected:
            fail(f"produced_artifact consumers diverge for {artifact_id}: {produced_declared} != {expected}")

    integrity = blueprint.get("projection_integrity_contract") or {}
    if integrity.get("canonical_artifact_dependency_source") != "groups[*].dependency_contract.artifact_dependencies":
        fail("projection integrity canonical source is invalid")
    if integrity.get("fail_closed_on_divergence") is not True:
        fail("projection integrity must fail closed")

    current_revision = catalogue.get("current_revision")
    revision = catalogue.get("revision") or {}
    if revision.get("revision_number") != current_revision:
        fail("catalogue revision number mismatch")
    if revision.get("revision_id") != f"CP-GOVMODEL-001-R{current_revision}":
        fail("catalogue revision id mismatch")
    if current_revision >= 2 and not revision.get("supersedes_revision_id"):
        fail("revision >= 2 must supersede a prior revision")
    last_decision = blueprint.get("last_enrichment_decision_id")
    if last_decision and last_decision not in (revision.get("source_decision_ids") or []):
        fail("current authority revision does not include blueprint last enrichment decision")

    print(f"GOVERNANCE_MODEL_INTEGRITY_PASS: groups={len(groups)} atomic_tasks={atomic_count} artifacts={len(artifacts)} artifact_edges={len(actual_edges)} catalogue_revision={current_revision}")

if __name__ == "__main__":
    main()
