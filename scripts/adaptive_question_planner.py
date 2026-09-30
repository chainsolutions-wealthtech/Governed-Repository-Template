#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ROOT / ".governance" / "control-plane-state" / "adaptive-question-catalogue.json"

SENTINEL_CHOICES = {
    "UNKNOWN_DISCOVER",
    "DISCOVER_MORE",
    "NONE_OF_THESE",
    "PLAN_NEW_SERVER",
    "PLAN_NEW_PATH",
    "DECIDE_LATER",
}


def load_catalogue(path: Path = CATALOGUE_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _choice_values(question: dict, observations: dict) -> tuple[list, list]:
    source = (question.get("response") or {}).get("choice_source") or {}
    source_type = source.get("type")
    observed_values: list = []
    values: list = []

    if source_type in {"OBSERVED", "OBSERVED_PLUS_STATIC"}:
        kind = source.get("kind")
        observed_values = copy.deepcopy(
            ((observations.get("choice_sources") or {}).get(kind)) or []
        )
        values.extend(observed_values)

    if source_type == "STATIC":
        values.extend(copy.deepcopy(source.get("values") or []))
    elif source_type == "OBSERVED":
        values.extend(copy.deepcopy(source.get("fallback_values") or []))
    elif source_type == "OBSERVED_PLUS_STATIC":
        values.extend(copy.deepcopy(source.get("static_values") or []))

    unique = []
    for value in values:
        if value not in unique:
            unique.append(value)
    return unique, observed_values


def _single_observed_candidate(observed_values: list):
    candidates = [v for v in observed_values if v not in SENTINEL_CHOICES]
    if len(candidates) == 1:
        return candidates[0]
    return None


def resolve_next_question(
    case: str,
    answers: dict | None = None,
    observations: dict | None = None,
    path: Path = CATALOGUE_PATH,
) -> dict:
    """
    Pure planning helper.

    It never performs discovery, writes, provisioning or mutation. It only:
    - reuses explicit answers;
    - auto-resolves fresh unambiguous factual observations;
    - returns the next choice-based question and its current choices.
    """
    catalogue = load_catalogue(path)
    answers = copy.deepcopy(answers or {})
    observations = copy.deepcopy(observations or {})
    facts = observations.get("facts") or {}
    auto_resolved = {}

    if case not in catalogue.get("cases", []):
        raise ValueError(f"unsupported case: {case}")

    for question in catalogue.get("questions", []):
        if case not in question.get("applies_to", []):
            continue

        field = question["field"]
        if field in answers:
            continue

        policy = question.get("resolution_policy")
        fact_key = question.get("observed_fact_key")
        if fact_key and fact_key in facts and policy in {
            "OBSERVED_FACT_AUTO_RESOLVE",
            "OBSERVED_THEN_OWNER_IF_AMBIGUOUS",
        }:
            auto_resolved[field] = copy.deepcopy(facts[fact_key])
            answers[field] = copy.deepcopy(facts[fact_key])
            continue

        choices, observed_values = _choice_values(question, observations)
        if policy == "OBSERVED_THEN_OWNER_IF_AMBIGUOUS":
            candidate = _single_observed_candidate(observed_values)
            if candidate is not None:
                value = [candidate] if (question.get("response") or {}).get("cardinality") == "MANY" else candidate
                auto_resolved[field] = copy.deepcopy(value)
                answers[field] = copy.deepcopy(value)
                continue

        return {
            "status": "QUESTION_REQUIRED",
            "case": case,
            "question": {
                "id": question["id"],
                "group": question["group"],
                "field": field,
                "text": question["text"],
                "cardinality": (question.get("response") or {}).get("cardinality", "ONE"),
                "choices": choices,
                "resolution_policy": policy,
                "effects": copy.deepcopy(question.get("effects") or []),
                "execution_authority_granted": False,
            },
            "auto_resolved": auto_resolved,
            "answers_after_observation_reuse": answers,
        }

    return {
        "status": "QUESTIONNAIRE_COMPLETE",
        "case": case,
        "question": None,
        "auto_resolved": auto_resolved,
        "answers_after_observation_reuse": answers,
        "execution_authority_granted": False,
    }


if __name__ == "__main__":
    print(json.dumps(resolve_next_question("ADOPT_EXISTING_REPOSITORY"), indent=2, ensure_ascii=False))
