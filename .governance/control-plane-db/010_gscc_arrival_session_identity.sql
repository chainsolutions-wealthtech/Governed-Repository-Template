CREATE TABLE IF NOT EXISTS gscc_arrival_instances (
  arrival_ref TEXT PRIMARY KEY,
  connection_ref TEXT NOT NULL UNIQUE,
  connection_ref_origin TEXT NOT NULL,
  transport_subject_ref TEXT,
  repository TEXT NOT NULL,
  resumable INTEGER NOT NULL CHECK(resumable IN (0,1)),
  identity_id TEXT,
  first_run_id TEXT,
  last_run_id TEXT,
  first_seen_at TEXT,
  last_seen_at TEXT,
  status TEXT NOT NULL,
  provider_private_identity_inferred INTEGER NOT NULL DEFAULT 0 CHECK(provider_private_identity_inferred IN (0,1)),
  FOREIGN KEY(identity_id) REFERENCES gscc_conversation_identities(identity_id)
);

CREATE TABLE IF NOT EXISTS gscc_arrival_events (
  event_id TEXT PRIMARY KEY,
  arrival_ref TEXT NOT NULL,
  run_id TEXT,
  event_type TEXT NOT NULL,
  gate_id TEXT,
  status TEXT NOT NULL,
  evidence_json TEXT NOT NULL,
  observed_at TEXT,
  FOREIGN KEY(arrival_ref) REFERENCES gscc_arrival_instances(arrival_ref) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS gscc_session_bindings (
  binding_id TEXT PRIMARY KEY,
  arrival_ref TEXT NOT NULL UNIQUE,
  identity_id TEXT NOT NULL,
  gse_identity_id TEXT,
  gacr_session_id TEXT,
  connection_ref TEXT NOT NULL,
  binding_status TEXT NOT NULL,
  binding_level TEXT,
  evidence_ref TEXT,
  created_at TEXT,
  updated_at TEXT,
  FOREIGN KEY(arrival_ref) REFERENCES gscc_arrival_instances(arrival_ref) ON DELETE CASCADE,
  FOREIGN KEY(identity_id) REFERENCES gscc_conversation_identities(identity_id)
);

CREATE INDEX IF NOT EXISTS idx_gscc_arrival_identity ON gscc_arrival_instances(identity_id);
CREATE INDEX IF NOT EXISTS idx_gscc_arrival_event_ref ON gscc_arrival_events(arrival_ref);
CREATE INDEX IF NOT EXISTS idx_gscc_session_gacr ON gscc_session_bindings(gacr_session_id);
