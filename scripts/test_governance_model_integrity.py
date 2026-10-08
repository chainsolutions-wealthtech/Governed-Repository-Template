#!/usr/bin/env python3
from __future__ import annotations
import copy
import hashlib
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


def validate_g01_materialized(blueprint: dict, artifact_by_id: dict, produced_copy: dict) -> None:
    decisions = (ROOT / "docs/control-plane/DECISIONS_LOG.md").read_text(encoding="utf-8")
    if "### CPD-076 —" not in decisions:
        fail("CPD-076 missing for GMC-G01 materialization")

    g01 = next((g for g in blueprint.get("groups") or [] if g.get("group_id") == "GMC-G01"), None)
    if not g01:
        fail("GMC-G01 missing")
    if g01.get("knowledge_materialization_authorized") is not True:
        fail("GMC-G01 materialization authorization missing")
    if g01.get("knowledge_materialization_decision_id") != "CPD-076":
        fail("GMC-G01 materialization decision must be CPD-076")
    if g01.get("implementation_authorized") is not False:
        fail("GMC-G01 general implementation authority must remain false")

    docs = {}
    for artifact_id, path in G01_GMA_PATHS.items():
        if not path.exists():
            fail(f"materialized GMA body missing: {path.relative_to(ROOT)}")
        doc = load(path)
        docs[artifact_id] = doc

        if doc.get("schema_version") != "gma-artifact/v1":
            fail(f"{artifact_id} schema_version invalid")
        if doc.get("artifact_id") != artifact_id:
            fail(f"{artifact_id} body identity mismatch")
        if doc.get("artifact_version") != "v1":
            fail(f"{artifact_id} initial artifact_version must be v1")
        if doc.get("producer") != "GMC-G01":
            fail(f"{artifact_id} producer mismatch")
        if doc.get("content_ref") != str(path.relative_to(ROOT)):
            fail(f"{artifact_id} content_ref mismatch")
        if doc.get("status") not in {"PRODUCED", "VALIDATED"}:
            fail(f"{artifact_id} body status invalid")
        if doc.get("validation_state") not in {"PENDING_VALIDATION", "VALIDATED"}:
            fail(f"{artifact_id} validation_state invalid")

        representation = doc.get("representation") or {}
        if representation.get("decision_id") != "CPD-076":
            fail(f"{artifact_id} representation decision mismatch")
        if representation.get("class") != "SOURCE_ONLY_VERSIONED_BODY_WITH_EXISTING_REFERENCE_PROJECTION":
            fail(f"{artifact_id} representation class invalid")
        if representation.get("encoding") != "JSON" or representation.get("package_unit") != "ONE_DOCUMENT_PER_GMA_ARTIFACT":
            fail(f"{artifact_id} packaging contract invalid")
        if representation.get("authority_scope") != "SOURCE_ONLY":
            fail(f"{artifact_id} must remain SOURCE_ONLY")
        if representation.get("implementation_authority_granted") is not False:
            fail(f"{artifact_id} must not grant implementation authority")

        subject = doc.get("subject") or {}
        if subject.get("repository") != "chainsolutions-wealthtech/Governed-Repository-Template":
            fail(f"{artifact_id} subject repository mismatch")
        if not re.fullmatch(r"[0-9a-f]{40}", str(subject.get("head_sha") or "")):
            fail(f"{artifact_id} subject HEAD invalid")
        if subject.get("work_package") != "GMC-G01":
            fail(f"{artifact_id} work package mismatch")

        digest = doc.get("content_digest") or {}
        if digest.get("algorithm") != "sha256":
            fail(f"{artifact_id} digest algorithm invalid")
        digest_doc = copy.deepcopy(doc)
        digest_doc.setdefault("content_digest", {})["value"] = None
        canonical = json.dumps(digest_doc, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        actual_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if digest.get("value") != actual_digest:
            fail(f"{artifact_id} content digest mismatch")

        registry = artifact_by_id.get(artifact_id) or {}
        produced = produced_copy.get(artifact_id) or {}
        for projection_name, projection in (("knowledge_artifacts", registry), ("produced_artifacts", produced)):
            if projection.get("content_ref") != str(path.relative_to(ROOT)):
                fail(f"{artifact_id} {projection_name} content_ref mismatch")
            if projection.get("status") != doc.get("status"):
                fail(f"{artifact_id} {projection_name} status mismatch")
            if projection.get("validation_state") != doc.get("validation_state"):
                fail(f"{artifact_id} {projection_name} validation state mismatch")
            if projection.get("artifact_version") != doc.get("artifact_version"):
                fail(f"{artifact_id} {projection_name} version mismatch")
            if (projection.get("content_digest") or {}).get("value") != digest.get("value"):
                fail(f"{artifact_id} {projection_name} digest mismatch")
            if projection.get("materialization_decision_id") != "CPD-076":
                fail(f"{artifact_id} {projection_name} materialization decision mismatch")

        if sorted(doc.get("consumed_by") or []) != sorted(registry.get("consumed_by") or []):
            fail(f"{artifact_id} body consumers diverge from blueprint")
        if doc.get("validation_state") == "VALIDATED" and not (doc.get("validation_evidence") or []):
            fail(f"{artifact_id} VALIDATED requires validation evidence")

    matrix = docs["GMA-MODEL-BOUNDARY-MATRIX"]
    taxonomy = docs["GMA-MODEL-CLASSIFICATION-TAXONOMY"]
    unresolved = docs["GMA-UNRESOLVED-BOUNDARY-ITEMS"]

    entries = (matrix.get("body") or {}).get("entries") or []
    if not entries:
        fail("GMA boundary matrix has no entries")
    matrix_ids = [entry.get("boundary_item_id") for entry in entries]
    if len(matrix_ids) != len(set(matrix_ids)):
        fail("GMA boundary matrix has duplicate boundary_item_id")

    unresolved_refs = set()
    for entry in entries:
        classes = set(entry.get("classifications") or [])
        if not classes or not classes <= G01_ALLOWED_CLASSES:
            fail(f"invalid GMA classifications for {entry.get('boundary_item_id')}: {sorted(classes)}")
        state = entry.get("resolution_state")
        if state not in G01_ALLOWED_RESOLUTION_STATES:
            fail(f"invalid GMA resolution state for {entry.get('boundary_item_id')}: {state}")
        if not (entry.get("provenance") or []):
            fail(f"GMA matrix provenance missing for {entry.get('boundary_item_id')}")
        if state == "UNRESOLVED":
            ref = entry.get("unresolved_ref")
            prefix = "GMA-UNRESOLVED-BOUNDARY-ITEMS#"
            if not isinstance(ref, str) or not ref.startswith(prefix):
                fail(f"unresolved matrix entry lacks reciprocal unresolved_ref: {entry.get('boundary_item_id')}")
            unresolved_refs.add(ref[len(prefix):])

    classes = (taxonomy.get("body") or {}).get("classes") or []
    class_names = {item.get("name") for item in classes}
    if class_names != G01_ALLOWED_CLASSES:
        fail(f"GMA taxonomy classes invalid: {sorted(class_names)}")
    if any(not (item.get("provenance") or []) for item in classes):
        fail("GMA taxonomy class provenance incomplete")

    resolution_states = {
        item.get("name") for item in (taxonomy.get("body") or {}).get("resolution_states") or []
    }
    if resolution_states != G01_ALLOWED_RESOLUTION_STATES:
        fail(f"GMA taxonomy resolution states invalid: {sorted(resolution_states)}")
    if len((taxonomy.get("body") or {}).get("cross_cutting_invariants") or []) < 12:
        fail("GMA taxonomy must preserve all established cross-cutting invariants")

    unresolved_items = (unresolved.get("body") or {}).get("items") or []
    unresolved_ids = {item.get("unresolved_id") for item in unresolved_items}
    if None in unresolved_ids or len(unresolved_ids) != len(unresolved_items):
        fail("GMA unresolved IDs missing or duplicated")
    if unresolved_refs != unresolved_ids:
        fail(f"GMA unresolved reciprocity mismatch matrix={sorted(unresolved_refs)} items={sorted(unresolved_ids)}")
    for item in unresolved_items:
        if not (item.get("provenance") or []):
            fail(f"GMA unresolved provenance missing for {item.get('unresolved_id')}")
        if item.get("blocking_effect") == "EXIT_BLOCKING":
            fail(f"GMC-G01 critical unresolved blocker remains: {item.get('unresolved_id')}")

def main() -> None:
    if not (ROOT/".template-source").exists():
        print("GOVERNANCE_MODEL_SOURCE_ONLY_SKIP: client repository has no source-only model state")
        return
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

    validate_g01_materialized(blueprint, artifact_by_id, produced_copy)

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
