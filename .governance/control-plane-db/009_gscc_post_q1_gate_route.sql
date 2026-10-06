CREATE TABLE IF NOT EXISTS gscc_gate_route_runs (
  route_run_id TEXT PRIMARY KEY,
  entry_run_id TEXT,
  identity_id TEXT,
  current_gate TEXT NOT NULL,
  owner_layer TEXT NOT NULL,
  action TEXT NOT NULL,
  implementation TEXT NOT NULL,
  observed_outcome TEXT,
  route_status TEXT NOT NULL CHECK(route_status IN ('PENDING','ADVANCED','BLOCKED','RELEASED')),
  next_gate TEXT,
  evidence_json TEXT NOT NULL,
  started_at TEXT,
  completed_at TEXT,
  authority_granted INTEGER NOT NULL DEFAULT 0 CHECK(authority_granted IN (0,1))
);

CREATE INDEX IF NOT EXISTS idx_gscc_gate_route_entry_run
  ON gscc_gate_route_runs(entry_run_id);

CREATE INDEX IF NOT EXISTS idx_gscc_gate_route_identity
  ON gscc_gate_route_runs(identity_id);

CREATE INDEX IF NOT EXISTS idx_gscc_gate_route_current_gate
  ON gscc_gate_route_runs(current_gate);
