CREATE TABLE IF NOT EXISTS agent_sessions (
  agent_session_id TEXT PRIMARY KEY,
  agent_identity TEXT,
  provider TEXT,
  actor_login TEXT,
  workstream TEXT NOT NULL,
  source_repository_id TEXT REFERENCES repositories(repository_id),
  pilot_repository_id TEXT REFERENCES repositories(repository_id),
  observed_source_head TEXT,
  observed_pilot_head TEXT,
  status TEXT NOT NULL,
  objective TEXT,
  unique_next_action TEXT,
  source_ref TEXT,
  started_at TEXT,
  ended_at TEXT
);

CREATE TABLE IF NOT EXISTS agent_activity_events (
  agent_activity_event_id TEXT PRIMARY KEY,
  agent_session_id TEXT NOT NULL REFERENCES agent_sessions(agent_session_id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  task_id TEXT,
  phase_id TEXT REFERENCES case_phases(phase_id),
  payload_json TEXT,
  evidence_ref TEXT,
  occurred_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_agent_sessions_workstream ON agent_sessions(workstream,status);
CREATE INDEX IF NOT EXISTS idx_agent_activity_session ON agent_activity_events(agent_session_id,occurred_at);
