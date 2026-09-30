#!/usr/bin/env python3
from __future__ import annotations

from adaptive_question_planner import load_catalogue, resolve_next_question


ALLOWED_EFFECTS = {"CLASSIFY", "DERIVE", "PREPARE", "SCHEDULE", "GATE"}
ALLOWED_POLICIES = {
    "OBSERVED_FACT_AUTO_RESOLVE",
    "OBSERVED_THEN_OWNER_IF_AMBIGUOUS",
    "OWNER_CHOICE_REQUIRED",
}


def assert_catalogue_contract() -> None:
    catalogue = load_catalogue()
    questions = catalogue["questions"]

    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: duplicate question id")

    fields = [q["field"] for q in questions]
    if len(fields) != len(set(fields)):
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: duplicate question field")

    if len(questions) < 30:
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: catalogue unexpectedly incomplete")

    for q in questions:
        response = q.get("response") or {}
        source = response.get("choice_source") or {}
        if response.get("type") != "CHOICE":
            raise SystemExit(f"ADAPTIVE_QUESTION_TEST_FAILED: {q['id']} is not choice-based")
        if response.get("cardinality") not in {"ONE", "MANY"}:
            raise SystemExit(f"ADAPTIVE_QUESTION_TEST_FAILED: {q['id']} cardinality")
        if source.get("type") not in {"STATIC", "OBSERVED", "OBSERVED_PLUS_STATIC"}:
            raise SystemExit(f"ADAPTIVE_QUESTION_TEST_FAILED: {q['id']} invalid choice source")
        if q.get("resolution_policy") not in ALLOWED_POLICIES:
            raise SystemExit(f"ADAPTIVE_QUESTION_TEST_FAILED: {q['id']} invalid resolution policy")
        if q.get("execution_authority_granted") is not False:
            raise SystemExit(f"ADAPTIVE_QUESTION_TEST_FAILED: {q['id']} answer grants execution")
        for effect in q.get("effects") or []:
            if effect.get("kind") not in ALLOWED_EFFECTS:
                raise SystemExit(f"ADAPTIVE_QUESTION_TEST_FAILED: {q['id']} effect may execute")

    future = {item["id"]: item for item in catalogue.get("future_incremental_implementation") or []}
    for required in ["AQI-04", "AQI-05", "AQI-06", "AQI-07", "AQI-08"]:
        if future.get(required, {}).get("status") != "PLANNED":
            raise SystemExit(f"ADAPTIVE_QUESTION_TEST_FAILED: {required} must remain planned")
    if catalogue.get("status") != "PLANNING_ONLY_NOT_RUNTIME_BOUND":
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: catalogue must not become a parallel runtime")


def assert_africafunds_existing_fixture() -> None:
    observations = {
        "facts": {
            "project.existence": "EXISTING",
            "git.provider": "GITHUB",
            "repository.topology": "MULTI_REPOSITORY",
            "environment.scope": "PRODUCTION",
            "project.profile": "application",
            "infrastructure.server_binding_mode": "EXISTING_SINGLE",
        },
        "choice_sources": {
            "REPOSITORIES": [
                "Wealthtechinnovations/api_opcv",
                "Wealthtechinnovations/front_end_opcvm",
            ],
            "SERVERS": ["S2"],
            "DEPLOYMENT_PATHS": [
                "/var/www/vhosts/chainsolutions.fr/africafunds.chainsolutions.fr/api",
                "/var/www/vhosts/chainsolutions.fr/africafunds.chainsolutions.fr/frontend",
            ],
            "DOMAINS": [
                "africafunds.chainsolutions.fr",
                "api.africafunds.chainsolutions.fr",
            ],
            "RUNTIMES": ["OBSERVED_EXISTING_RUNTIME"],
            "DATABASES": ["OBSERVED_EXISTING_DATABASE"],
        },
    }

    first = resolve_next_question("ADOPT_EXISTING_REPOSITORY", observations=observations)
    q = first["question"]
    if q["id"] != "AQ-004" or q["field"] != "repository_members":
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: AfricaFunds should reuse topology facts then ask repository membership")
    expected_repos = {
        "Wealthtechinnovations/api_opcv",
        "Wealthtechinnovations/front_end_opcvm",
    }
    if not expected_repos.issubset(set(q["choices"])):
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: AfricaFunds observed repositories missing from choices")
    for field in ["project_existence", "git_provider", "repository_topology"]:
        if field not in first["auto_resolved"]:
            raise SystemExit(f"ADAPTIVE_QUESTION_TEST_FAILED: AfricaFunds did not reuse observed {field}")

    answers = {
        "repository_members": [
            "Wealthtechinnovations/api_opcv",
            "Wealthtechinnovations/front_end_opcvm",
        ]
    }
    second = resolve_next_question("ADOPT_EXISTING_REPOSITORY", answers=answers, observations=observations)
    if second["question"]["id"] != "AQ-006":
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: AfricaFunds next decision should be governance adoption posture")
    if "PRESERVE_AND_COMPLETE" not in second["question"]["choices"]:
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: additive adoption option missing")

    answers.update({
        "governance_adoption_posture": "PRESERVE_AND_COMPLETE",
        "architecture_posture": "PRESERVE_EXISTING",
    })
    third = resolve_next_question("ADOPT_EXISTING_REPOSITORY", answers=answers, observations=observations)
    # S2 is a single factual candidate, so server selection is auto-resolved.
    if third["question"]["id"] != "AQ-011":
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: observed S2 should avoid a redundant server question")
    if third["auto_resolved"].get("server_selection") != ["S2"]:
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: S2 was not auto-reused")


def assert_fresh_ekyc_fixture() -> None:
    observations = {
        "facts": {
            "project.existence": "NEW",
            "git.provider": "GITHUB",
            "repository.topology": "SINGLE_REPOSITORY",
            "environment.scope": "DEVELOPMENT",
            "project.profile": "chainsolutions-fullstack-web",
            "infrastructure.server_binding_mode": "NONE_PLAN_NEW",
        },
        "choice_sources": {
            "SERVERS": [],
            "DOMAINS": [],
            "DEPLOYMENT_PATHS": [],
            "RUNTIMES": [],
            "DATABASES": [],
        },
    }
    result = resolve_next_question("CREATE_NEW_REPOSITORY", observations=observations)
    q = result["question"]
    if q["id"] != "AQ-013" or q["field"] != "domain_posture":
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: new project should reach domain intent after factual reuse")
    if "CREATE_NEW" not in q["choices"] or "DECIDE_LATER" not in q["choices"]:
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: new-project domain choices incomplete")
    if q["execution_authority_granted"] is not False:
        raise SystemExit("ADAPTIVE_QUESTION_TEST_FAILED: domain choice must not execute creation")


def main() -> None:
    assert_catalogue_contract()
    assert_africafunds_existing_fixture()
    assert_fresh_ekyc_fixture()
    print("ADAPTIVE_CHOICE_QUESTION_CATALOGUE_TEST_PASS")


if __name__ == "__main__":
    main()
