CREATE TABLE IF NOT EXISTS server_identity_secret_facts (
  fact_id TEXT PRIMARY KEY,
  server_id TEXT NOT NULL CHECK(server_id IN ('S1','S2')),
  fact_kind TEXT NOT NULL CHECK(fact_kind IN ('MECHANISM','PROBE')),
  subject_id TEXT NOT NULL,
  status TEXT NOT NULL,
  metadata_json TEXT NOT NULL,
  freshness_class TEXT NOT NULL CHECK(freshness_class IN ('EVENT_AND_NEED_BASED','LIVE_OR_BOUNDED_TTL')),
  observed_at TEXT NOT NULL,
  known_from_json TEXT NOT NULL,
  last_attempt_json TEXT NOT NULL,
  source_revision INTEGER NOT NULL CHECK(source_revision > 0),
  UNIQUE(server_id, fact_kind, subject_id)
);

CREATE INDEX IF NOT EXISTS idx_server_identity_secret_server_kind
  ON server_identity_secret_facts(server_id, fact_kind);
