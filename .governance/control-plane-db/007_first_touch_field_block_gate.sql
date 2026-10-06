CREATE TABLE IF NOT EXISTS first_touch_capture_records (
  capture_id TEXT PRIMARY KEY,
  schema_id TEXT NOT NULL,
  observed_at TEXT,
  repository TEXT,
  actor TEXT,
  capture_digest TEXT,
  raw_json TEXT NOT NULL,
  raw_json_sha256 TEXT NOT NULL,
  node_count INTEGER NOT NULL CHECK(node_count >= 1),
  terminal_value_count INTEGER NOT NULL CHECK(terminal_value_count >= 0),
  api_attempt_count INTEGER NOT NULL CHECK(api_attempt_count >= 0),
  source_ref TEXT
);

CREATE TABLE IF NOT EXISTS first_touch_capture_nodes (
  capture_id TEXT NOT NULL,
  node_ordinal INTEGER NOT NULL CHECK(node_ordinal >= 1),
  json_path TEXT NOT NULL,
  parent_path TEXT,
  key_name TEXT,
  array_index INTEGER,
  value_type TEXT NOT NULL,
  is_terminal INTEGER NOT NULL CHECK(is_terminal IN (0,1)),
  value_json TEXT NOT NULL,
  PRIMARY KEY(capture_id,node_ordinal),
  UNIQUE(capture_id,json_path),
  FOREIGN KEY(capture_id) REFERENCES first_touch_capture_records(capture_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS first_touch_capture_api_attempts (
  capture_id TEXT NOT NULL,
  attempt_ordinal INTEGER NOT NULL CHECK(attempt_ordinal >= 1),
  name TEXT,
  url TEXT,
  http_status INTEGER,
  response_json TEXT NOT NULL,
  PRIMARY KEY(capture_id,attempt_ordinal),
  FOREIGN KEY(capture_id) REFERENCES first_touch_capture_records(capture_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS first_touch_evidence_blocks (
  block_id TEXT PRIMARY KEY,
  ordinal INTEGER NOT NULL UNIQUE,
  label TEXT NOT NULL,
  owner_layer TEXT NOT NULL,
  purpose TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS first_touch_process_gates (
  gate_id TEXT PRIMARY KEY,
  ordinal INTEGER NOT NULL UNIQUE,
  phase TEXT NOT NULL,
  owner_layer TEXT NOT NULL,
  label TEXT NOT NULL,
  unlock_effect TEXT NOT NULL,
  authority_effect TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS first_touch_gate_requirements (
  gate_id TEXT NOT NULL,
  block_id TEXT NOT NULL,
  requirement TEXT NOT NULL CHECK(requirement IN ('REQUIRED','SUPPORTING','CORROBORATING')),
  minimum_status TEXT NOT NULL CHECK(minimum_status IN ('PRESENT','SUFFICIENT','VERIFIED')),
  PRIMARY KEY(gate_id,block_id),
  FOREIGN KEY(gate_id) REFERENCES first_touch_process_gates(gate_id) ON DELETE CASCADE,
  FOREIGN KEY(block_id) REFERENCES first_touch_evidence_blocks(block_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS first_touch_field_assignment_rules (
  rule_id TEXT PRIMARY KEY,
  priority INTEGER NOT NULL,
  match_kind TEXT NOT NULL CHECK(match_kind IN ('PREFIX','CONTAINS','REGEX','FALLBACK')),
  pattern TEXT NOT NULL,
  block_id TEXT NOT NULL,
  usage_purpose TEXT NOT NULL,
  stage_hint TEXT,
  FOREIGN KEY(block_id) REFERENCES first_touch_evidence_blocks(block_id)
);

CREATE TABLE IF NOT EXISTS first_touch_field_block_membership (
  capture_id TEXT NOT NULL,
  json_path TEXT NOT NULL,
  block_id TEXT NOT NULL,
  rule_id TEXT NOT NULL,
  usage_purpose TEXT NOT NULL,
  PRIMARY KEY(capture_id,json_path,block_id,rule_id),
  FOREIGN KEY(capture_id,json_path) REFERENCES first_touch_capture_nodes(capture_id,json_path) ON DELETE CASCADE,
  FOREIGN KEY(block_id) REFERENCES first_touch_evidence_blocks(block_id),
  FOREIGN KEY(rule_id) REFERENCES first_touch_field_assignment_rules(rule_id)
);

CREATE TABLE IF NOT EXISTS first_touch_capture_block_status (
  capture_id TEXT NOT NULL,
  block_id TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('EMPTY','PARTIAL','PRESENT','SUFFICIENT','VERIFIED','CONFLICTING','STALE','UNAVAILABLE')),
  field_count INTEGER NOT NULL CHECK(field_count >= 0),
  terminal_field_count INTEGER NOT NULL CHECK(terminal_field_count >= 0),
  evidence_json TEXT NOT NULL,
  PRIMARY KEY(capture_id,block_id),
  FOREIGN KEY(capture_id) REFERENCES first_touch_capture_records(capture_id) ON DELETE CASCADE,
  FOREIGN KEY(block_id) REFERENCES first_touch_evidence_blocks(block_id)
);

CREATE TABLE IF NOT EXISTS first_touch_gate_evaluations (
  capture_id TEXT NOT NULL,
  gate_id TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('BLOCKED','EVIDENCE_PARTIAL','EVIDENCE_READY_FOR_CANONICAL_VALIDATION')),
  missing_blocks_json TEXT NOT NULL,
  satisfied_blocks_json TEXT NOT NULL,
  evaluated_at TEXT,
  PRIMARY KEY(capture_id,gate_id),
  FOREIGN KEY(capture_id) REFERENCES first_touch_capture_records(capture_id) ON DELETE CASCADE,
  FOREIGN KEY(gate_id) REFERENCES first_touch_process_gates(gate_id)
);

CREATE INDEX IF NOT EXISTS idx_ft_capture_nodes_path ON first_touch_capture_nodes(json_path);
CREATE INDEX IF NOT EXISTS idx_ft_capture_nodes_key ON first_touch_capture_nodes(key_name);
CREATE INDEX IF NOT EXISTS idx_ft_membership_block ON first_touch_field_block_membership(block_id);
CREATE INDEX IF NOT EXISTS idx_ft_gate_requirements_block ON first_touch_gate_requirements(block_id);


-- GSCC-owned logical conversation identity and immutable First Touch snapshot.
CREATE TABLE IF NOT EXISTS gscc_conversation_identities (
  identity_id TEXT PRIMARY KEY,
  anchor_sha256 TEXT NOT NULL UNIQUE,
  identity_strength TEXT NOT NULL CHECK(identity_strength IN ('EXACT','STRONG')),
  first_capture_id TEXT NOT NULL UNIQUE,
  first_observed_at TEXT,
  last_capture_id TEXT NOT NULL,
  last_seen_at TEXT,
  status TEXT NOT NULL CHECK(status IN ('FIRST_TOUCH_CONSUMED','ACTIVE')),
  FOREIGN KEY(first_capture_id) REFERENCES first_touch_capture_records(capture_id),
  FOREIGN KEY(last_capture_id) REFERENCES first_touch_capture_records(capture_id)
);

CREATE TABLE IF NOT EXISTS gscc_first_touch_snapshots (
  identity_id TEXT PRIMARY KEY,
  capture_id TEXT NOT NULL UNIQUE,
  snapshot_json TEXT NOT NULL,
  snapshot_sha256 TEXT NOT NULL,
  created_at TEXT,
  FOREIGN KEY(identity_id) REFERENCES gscc_conversation_identities(identity_id) ON DELETE CASCADE,
  FOREIGN KEY(capture_id) REFERENCES first_touch_capture_records(capture_id)
);

-- GSE-owned projection of the logical conversation state. GACR durable
-- continuity is intentionally not required to create or update this twin.
CREATE TABLE IF NOT EXISTS gse_session_twins (
  identity_id TEXT PRIMARY KEY,
  session_twin_json TEXT NOT NULL,
  revision INTEGER NOT NULL CHECK(revision >= 1),
  last_event_type TEXT NOT NULL CHECK(last_event_type IN ('SESSION_ATTACH','SESSION_RESUME')),
  updated_at TEXT,
  FOREIGN KEY(identity_id) REFERENCES gscc_conversation_identities(identity_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_gscc_identity_anchor ON gscc_conversation_identities(anchor_sha256);
CREATE INDEX IF NOT EXISTS idx_gscc_identity_last_seen ON gscc_conversation_identities(last_seen_at);
