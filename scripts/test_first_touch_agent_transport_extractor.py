#!/usr/bin/env python3
from first_touch_agent_transport_extractor import extract
from provider_first_tool_hook import build_envelope

host={
 "provider":"chatgpt",
 "provider_product":"ChatGPT",
 "provider_family":"OpenAI",
 "runtime":"chatgpt-runtime",
 "surface":"text",
 "channel":"text",
 "execution_mode":"direct-tool",
 "model":"GPT-5.6 Sol",
 "transport":"chatgpt-github-direct",
 "connector_name":"GitHub",
 "connector_type":"native",
 "direct_connector":True,
 "github_tool_surface":"mcp__GitHub__get_repo",
 "actor":"Wealthtechinnovations",
 "branch":"main",
 "observed_head":"a"*40,
 "identity":{
   "conversation_id":"UNAVAILABLE",
   "conversation_ref":"UNAVAILABLE",
   "session_id":"UNAVAILABLE",
   "session_ref":"UNAVAILABLE",
   "connection_ref":"UNAVAILABLE"
 },
 "tool":{"name":"mcp__GitHub__get_repo","operation":"read_repository","category":"READ","success":True}
}

github={
 "id":1386478935,
 "repository_full_name":"chainsolutions-wealthtech/Governed-Repository-Template",
 "owner":{"login":"chainsolutions-wealthtech","id":299685687},
 "permissions":{"admin":True,"maintain":True,"pull":True,"push":True,"triage":True},
 "default_branch":"main",
 "visibility":"public"
}

packet=extract(host,github)
assert packet["schema"]=="gscc-first-touch-observable-packet/v1"
assert packet["summary"]["silent_missing_count"]==0
assert packet["summary"]["complete_accounting"] is True
assert packet["observations"]["provider.provider"]["value"]=="chatgpt"
assert packet["observations"]["agent.model"]["value"]=="GPT-5.6 Sol"
assert packet["observations"]["github.repository_full_name"]["status"]=="PRESENT_VALID"
assert packet["observations"]["github.permissions"]["status"]=="PRESENT_VALID"
assert packet["observations"]["session.conversation_ref"]["status"]=="UNAVAILABLE"
assert packet["identity"]["strength"]=="UNRESOLVED"
assert packet["identity"]["classification"]=="UNRESOLVED"
assert packet["mutation_authority_granted"] is False

host2=dict(host)
host2["identity"]=dict(host["identity"])
host2["identity"]["connection_ref"]="conn_visible_12345678"
packet2=extract(host2,github)
assert packet2["identity"]["strength"]=="STRONG"
assert packet2["identity"]["classification"]=="FIRST_TOUCH_CANDIDATE"
assert packet2["identity"]["candidates"][0]["field"]=="connection.connection_ref"
print("FIRST_TOUCH_AGENT_TRANSPORT_EXTRACTOR_TEST_PASS")
print(packet["summary"])


provider_event={
 "provider":"chatgpt",
 "provider_product":"ChatGPT",
 "provider_family":"OpenAI",
 "transport":"chatgpt-github-direct",
 "repository":"chainsolutions-wealthtech/Governed-Repository-Template",
 "runtime":"chatgpt-runtime",
 "surface":"text",
 "channel":"text",
 "execution_mode":"direct-tool",
 "model":"GPT-5.6 Sol",
 "connector_name":"GitHub",
 "connector_type":"native",
 "client_instance_id":"client-visible-1",
 "request_id":"req-visible-1",
 "observed_at":"2026-10-06T22:20:00Z",
 "actor":"Wealthtechinnovations",
 "identity":{
   "conversation_id":"UNAVAILABLE",
   "conversation_ref":"UNAVAILABLE",
   "session_id":"UNAVAILABLE",
   "session_ref":"UNAVAILABLE",
   "connection_ref":"conn-visible-12345678",
   "workspace_id":"UNAVAILABLE",
   "workspace_name":"UNAVAILABLE"
 },
 "tool_name":"mcp__GitHub__get_repo",
 "operation":"read_repository",
 "category":"READ",
 "success":True
}

envelope=build_envelope(provider_event)
packet3=extract(envelope,github)
assert packet3["observations"]["provider.provider"]["value"]=="chatgpt"
assert packet3["observations"]["agent.model"]["value"]=="GPT-5.6 Sol"
assert packet3["observations"]["client.client_instance_id"]["value"]=="client-visible-1"
assert packet3["observations"]["request.request_id"]["value"]=="req-visible-1"
assert packet3["observations"]["connection.connection_ref"]["value"]=="conn-visible-12345678"
assert packet3["identity"]["strength"]=="STRONG"
assert packet3["identity"]["classification"]=="FIRST_TOUCH_CANDIDATE"
print("PROVIDER_ENVELOPE_MERGE_TEST_PASS")
