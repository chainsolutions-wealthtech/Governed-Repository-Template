#!/usr/bin/env python3
from first_touch_exhaustive_collector import build_capture

def fake_request(url, token):
    if url.endswith("/repos/acme/demo"):
        return 200, {"id": 1, "full_name": "acme/demo", "extra": {"x": 1}}
    if "/collaborators/alice/permission" in url:
        return 200, {"permission": "write"}
    if url.endswith("/issues/7"):
        return 200, {"id": 70, "number": 7, "node_id": "NODE7"}
    if "/actions/runs/99/jobs" in url:
        return 200, {"jobs": [{"id": 100, "name": "arrival"}]}
    if "/actions/runs/99" in url:
        return 200, {"id": 99, "event": "issues"}
    if url.endswith("/installation"):
        return 404, {"message": "not available"}
    if url.endswith("/actions/permissions"):
        return 200, {"enabled": True}
    raise AssertionError(url)

event = {
    "repository": {"id": 1, "full_name": "acme/demo"},
    "sender": {"login": "alice"},
    "issue": {"number": 7, "node_id": "NODE7"},
    "number": 7,
    "unexpected": {"alpha": 1, "beta": [2, 3]},
}
env = {
    "GITHUB_EVENT_NAME": "issues",
    "GITHUB_REPOSITORY": "acme/demo",
    "GITHUB_ACTOR": "alice",
    "GITHUB_RUN_ID": "99",
    "GITHUB_RUN_ATTEMPT": "1",
    "GITHUB_API_URL": "https://api.github.com",
    "RUNNER_OS": "Linux",
}
capture = build_capture(event, env, request_fn=fake_request, observed_at="2026-10-06T00:00:00+00:00")
assert capture["github_event"]["unexpected"] == {"alpha": 1, "beta": [2, 3]}
assert capture["environment"]["RUNNER_OS"] == "Linux"
assert capture["subject"]["issue_number"] == 7
assert len(capture["api_attempts"]) == 7
assert capture["mutation_authority_granted"] is False
assert capture["interpretation_applied"] is False
print("FIRST_TOUCH_CAPTURE_BASIC_TEST_PASS")


first_touch_event = {
    "repository": {"id": 1, "full_name": "acme/demo"},
    "sender": {"login": "alice"},
    "issue": {"number": 7},
    "number": 7,
    "comment": {
        "id": 7001,
        "body": '/gscc-first-touch {"connection":{"connection_ref":"conn_ft_12345678"},"client":{"client_instance_id":"client_ft_12345678"},"session":{"conversation_ref":"UNAVAILABLE","provider_conversation_ref":"UNAVAILABLE"}}'
    },
}
ft_env = dict(env)
ft_env["GITHUB_EVENT_NAME"] = "issue_comment"
ft_capture = build_capture(first_touch_event, ft_env, request_fn=fake_request, observed_at="2026-10-06T00:01:00+00:00")
assert ft_capture["github_event"]["comment"]["body"]["_capture_status"] == "REDACTED_VALUE"
assert ft_capture["safe_ingress"]["status"] == "VALID"
assert ft_capture["safe_ingress"]["connection_ref"] == "conn_ft_12345678"
assert ft_capture["safe_ingress"]["client_instance_id"] == "client_ft_12345678"
assert ft_capture["safe_ingress"]["conversation_ref_status"] == "UNAVAILABLE"
assert ft_capture["safe_ingress"]["freeform_body_persisted"] is False
