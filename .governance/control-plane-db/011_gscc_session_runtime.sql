CREATE TABLE IF NOT EXISTS gscc_session_runtime (
  runtime_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL UNIQUE,
  arrival_ref TEXT NOT NULL,
  identity_id TEXT NOT NULL,
  capture_id TEXT NOT NULL,
  issue_number INTEGER,
  connection_ref TEXT NOT NULL,
  state TEXT NOT NULL,
  admission_json TEXT,
  capability_evidence_json TEXT,
  control_evidence_json TEXT,
  gse_state_json TEXT,
  access_grant_json TEXT,
  last_gate TEXT,
  next_gate TEXT,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY(arrival_ref) REFERENCES gscc_arrival_instances(arrival_ref) ON DELETE CASCADE,
  FOREIGN KEY(identity_id) REFERENCES gscc_conversation_identities(identity_id)
);

CREATE TABLE IF NOT EXISTS gscc_pre_gse_control_challenges (
  challenge_row_id TEXT PRIMARY KEY,
  runtime_id TEXT NOT NULL,
  issue_number INTEGER NOT NULL,
  dispatch_json TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY(runtime_id) REFERENCES gscc_session_runtime(runtime_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_gscc_session_runtime_arrival ON gscc_session_runtime(arrival_ref);
CREATE INDEX IF NOT EXISTS idx_gscc_session_runtime_state ON gscc_session_runtime(state);
