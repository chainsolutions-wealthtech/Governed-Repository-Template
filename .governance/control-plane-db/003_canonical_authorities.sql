CREATE TABLE IF NOT EXISTS canonical_authorities (
  authority_id TEXT PRIMARY KEY,
  authority_type TEXT NOT NULL,
  canonical_path TEXT NOT NULL UNIQUE,
  scope TEXT NOT NULL,
  status TEXT NOT NULL,
  current_revision INTEGER NOT NULL CHECK(current_revision >= 1),
  source_decision_id TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS canonical_authority_revisions (
  revision_id TEXT PRIMARY KEY,
  authority_id TEXT NOT NULL REFERENCES canonical_authorities(authority_id) ON DELETE CASCADE,
  revision_number INTEGER NOT NULL CHECK(revision_number >= 1),
  subject_head_sha TEXT,
  content_sha TEXT,
  supersedes_revision_id TEXT REFERENCES canonical_authority_revisions(revision_id),
  reason TEXT NOT NULL,
  source_decision_id TEXT,
  source_ref TEXT,
  created_at TEXT,
  UNIQUE(authority_id, revision_number)
);

CREATE TABLE IF NOT EXISTS canonical_memory_events (
  event_id TEXT PRIMARY KEY,
  event_type TEXT NOT NULL,
  scope_type TEXT NOT NULL,
  scope_id TEXT NOT NULL,
  payload_json TEXT,
  source_ref TEXT,
  occurred_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_authority_revisions_authority
  ON canonical_authority_revisions(authority_id, revision_number);

CREATE INDEX IF NOT EXISTS idx_canonical_events_scope
  ON canonical_memory_events(scope_type, scope_id, occurred_at);
