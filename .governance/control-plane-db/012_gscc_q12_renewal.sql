-- GSCC same-arrival Q12: append-only history of superseded, never deleted grants.
-- The runtime's current access_grant_json is a mutable projection; history is evidence.
CREATE TABLE IF NOT EXISTS gscc_q12_renewal_history (
  renewal_id INTEGER PRIMARY KEY AUTOINCREMENT,
  runtime_id TEXT NOT NULL,
  arrival_ref TEXT NOT NULL,
  identity_id TEXT NOT NULL,
  gacr_session_id TEXT NOT NULL,
  old_grant_id TEXT NOT NULL,
  new_grant_id TEXT NOT NULL,
  old_grant_json TEXT NOT NULL,
  new_grant_json TEXT NOT NULL,
  qualification_evidence_json TEXT NOT NULL,
  control_evidence_ref TEXT NOT NULL,
  old_head TEXT NOT NULL,
  new_head TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(runtime_id, old_grant_id),
  UNIQUE(runtime_id, new_grant_id),
  FOREIGN KEY(runtime_id) REFERENCES gscc_session_runtime(runtime_id)
);
CREATE INDEX IF NOT EXISTS idx_gscc_q12_renewal_arrival
  ON gscc_q12_renewal_history(arrival_ref, created_at);
