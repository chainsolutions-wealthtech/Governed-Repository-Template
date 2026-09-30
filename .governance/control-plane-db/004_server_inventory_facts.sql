CREATE TABLE IF NOT EXISTS server_inventory_facts (
  fact_id TEXT PRIMARY KEY,
  server_id TEXT NOT NULL CHECK(server_id IN ('S1','S2')),
  domain_id TEXT NOT NULL,
  slot TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('KNOWN_CURRENT','KNOWN_STALE','UNKNOWN_DISCOVERABLE')),
  value_json TEXT,
  freshness_class TEXT NOT NULL,
  observed_at TEXT,
  known_from_json TEXT,
  last_attempt_json TEXT NOT NULL,
  source_revision INTEGER NOT NULL CHECK(source_revision > 0),
  UNIQUE(server_id, domain_id, slot)
);

CREATE INDEX IF NOT EXISTS idx_server_inventory_server_domain
  ON server_inventory_facts(server_id, domain_id);
