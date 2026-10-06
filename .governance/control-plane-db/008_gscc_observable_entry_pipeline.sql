CREATE TABLE IF NOT EXISTS gscc_observable_packets (
  packet_id TEXT PRIMARY KEY,
  capture_id TEXT NOT NULL UNIQUE,
  schema_id TEXT NOT NULL,
  repository TEXT,
  observed_at TEXT,
  identity_strength TEXT NOT NULL,
  classification TEXT NOT NULL,
  packet_json TEXT NOT NULL,
  packet_sha256 TEXT NOT NULL,
  created_at TEXT,
  FOREIGN KEY(capture_id) REFERENCES first_touch_capture_records(capture_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS gscc_entry_pipeline_runs (
  run_id TEXT PRIMARY KEY,
  packet_id TEXT NOT NULL,
  capture_id TEXT NOT NULL,
  identity_id TEXT,
  classification TEXT NOT NULL,
  entry_status TEXT NOT NULL,
  handoff_status TEXT,
  next_gate TEXT,
  blocked_reason_json TEXT NOT NULL,
  started_at TEXT,
  completed_at TEXT,
  authority_granted INTEGER NOT NULL DEFAULT 0 CHECK(authority_granted IN (0,1)),
  FOREIGN KEY(packet_id) REFERENCES gscc_observable_packets(packet_id) ON DELETE CASCADE,
  FOREIGN KEY(capture_id) REFERENCES first_touch_capture_records(capture_id) ON DELETE CASCADE,
  FOREIGN KEY(identity_id) REFERENCES gscc_conversation_identities(identity_id)
);

CREATE INDEX IF NOT EXISTS idx_gscc_observable_packet_capture
  ON gscc_observable_packets(capture_id);

CREATE INDEX IF NOT EXISTS idx_gscc_entry_pipeline_identity
  ON gscc_entry_pipeline_runs(identity_id);

CREATE INDEX IF NOT EXISTS idx_gscc_entry_pipeline_next_gate
  ON gscc_entry_pipeline_runs(next_gate);
