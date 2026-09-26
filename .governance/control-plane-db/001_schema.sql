PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS framework_cases (
  case_id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  ordinal INTEGER NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('STRUCTURING_CASE','POST_CASE_MODE')),
  status TEXT NOT NULL,
  source_authority TEXT,
  created_at TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS modes (
  mode_id TEXT PRIMARY KEY,
  case_id TEXT REFERENCES framework_cases(case_id),
  label TEXT NOT NULL,
  description TEXT,
  is_default INTEGER NOT NULL DEFAULT 0 CHECK(is_default IN (0,1))
);

CREATE TABLE IF NOT EXISTS case_phases (
  phase_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES framework_cases(case_id) ON DELETE CASCADE,
  ordinal INTEGER NOT NULL,
  label TEXT NOT NULL,
  status TEXT NOT NULL,
  entry_gate TEXT,
  exit_gate TEXT,
  owner_feedback_hook TEXT,
  source_authority TEXT,
  UNIQUE(case_id, ordinal)
);

CREATE TABLE IF NOT EXISTS phase_dependencies (
  phase_id TEXT NOT NULL REFERENCES case_phases(phase_id) ON DELETE CASCADE,
  depends_on_phase_id TEXT NOT NULL REFERENCES case_phases(phase_id) ON DELETE CASCADE,
  PRIMARY KEY(phase_id, depends_on_phase_id)
);

CREATE TABLE IF NOT EXISTS questions (
  question_id TEXT PRIMARY KEY,
  case_id TEXT REFERENCES framework_cases(case_id) ON DELETE CASCADE,
  phase_id TEXT REFERENCES case_phases(phase_id) ON DELETE CASCADE,
  field_key TEXT NOT NULL,
  prompt TEXT NOT NULL,
  response_type TEXT NOT NULL,
  required INTEGER NOT NULL DEFAULT 1 CHECK(required IN (0,1)),
  required_when_json TEXT,
  validation_rule TEXT,
  source_authority TEXT
);

CREATE TABLE IF NOT EXISTS question_options (
  option_id TEXT PRIMARY KEY,
  question_id TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
  value_json TEXT NOT NULL,
  label TEXT,
  ordinal INTEGER NOT NULL,
  UNIQUE(question_id, ordinal)
);

CREATE TABLE IF NOT EXISTS activities (
  activity_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES framework_cases(case_id) ON DELETE CASCADE,
  phase_id TEXT REFERENCES case_phases(phase_id) ON DELETE CASCADE,
  kind TEXT NOT NULL,
  label TEXT NOT NULL,
  mutation_class TEXT NOT NULL,
  required_authority TEXT,
  required_evidence_json TEXT,
  source_authority TEXT
);

CREATE TABLE IF NOT EXISTS repositories (
  repository_id TEXT PRIMARY KEY,
  full_name TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL,
  canonical_branch TEXT,
  current_head_sha TEXT,
  source_ref TEXT
);

CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES framework_cases(case_id),
  repository_id TEXT REFERENCES repositories(repository_id),
  status TEXT NOT NULL,
  current_phase_id TEXT REFERENCES case_phases(phase_id),
  source_issue TEXT,
  started_at TEXT,
  completed_at TEXT,
  parent_run_id TEXT REFERENCES runs(run_id)
);

CREATE TABLE IF NOT EXISTS run_answers (
  run_answer_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
  question_id TEXT REFERENCES questions(question_id),
  field_key TEXT NOT NULL,
  value_json TEXT NOT NULL,
  revision INTEGER NOT NULL,
  source_ref TEXT,
  answered_at TEXT,
  supersedes_run_answer_id TEXT REFERENCES run_answers(run_answer_id)
);

CREATE TABLE IF NOT EXISTS decisions (
  decision_id TEXT PRIMARY KEY,
  scope_type TEXT NOT NULL,
  scope_id TEXT NOT NULL,
  decision_key TEXT NOT NULL,
  value_json TEXT NOT NULL,
  status TEXT NOT NULL,
  source_ref TEXT,
  decided_at TEXT,
  supersedes_decision_id TEXT REFERENCES decisions(decision_id)
);

CREATE TABLE IF NOT EXISTS run_events (
  event_id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES runs(run_id) ON DELETE CASCADE,
  phase_id TEXT REFERENCES case_phases(phase_id),
  event_type TEXT NOT NULL,
  payload_json TEXT,
  source_ref TEXT,
  occurred_at TEXT
);

CREATE TABLE IF NOT EXISTS evidence (
  evidence_id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES runs(run_id) ON DELETE CASCADE,
  phase_id TEXT REFERENCES case_phases(phase_id),
  evidence_type TEXT NOT NULL,
  status TEXT NOT NULL,
  payload_json TEXT,
  source_ref TEXT,
  observed_at TEXT
);

CREATE TABLE IF NOT EXISTS checkpoints (
  checkpoint_id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES runs(run_id) ON DELETE CASCADE,
  phase_id TEXT REFERENCES case_phases(phase_id),
  subject_head_sha TEXT,
  state TEXT NOT NULL,
  next_action TEXT,
  payload_json TEXT,
  source_ref TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS handoffs (
  handoff_id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES runs(run_id) ON DELETE CASCADE,
  checkpoint_id TEXT REFERENCES checkpoints(checkpoint_id),
  status TEXT NOT NULL,
  next_action TEXT,
  payload_json TEXT,
  source_ref TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS owner_feedback (
  feedback_id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES runs(run_id) ON DELETE CASCADE,
  phase_id TEXT REFERENCES case_phases(phase_id),
  feedback_class TEXT NOT NULL,
  content TEXT NOT NULL,
  effect TEXT NOT NULL,
  earliest_affected_phase_id TEXT REFERENCES case_phases(phase_id),
  dependent_revalidation_json TEXT,
  source_ref TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS intakes (
  intake_id TEXT PRIMARY KEY,
  originating_case_id TEXT REFERENCES framework_cases(case_id),
  originating_run_id TEXT REFERENCES runs(run_id),
  target_system TEXT NOT NULL,
  status TEXT NOT NULL,
  summary TEXT NOT NULL,
  source_ref TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES runs(run_id),
  phase_id TEXT REFERENCES case_phases(phase_id),
  artifact_type TEXT NOT NULL,
  path_or_ref TEXT NOT NULL,
  sha TEXT,
  source_ref TEXT,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_phases_case ON case_phases(case_id, ordinal);
CREATE INDEX IF NOT EXISTS idx_questions_phase ON questions(phase_id);
CREATE INDEX IF NOT EXISTS idx_activities_phase ON activities(phase_id);
CREATE INDEX IF NOT EXISTS idx_runs_case ON runs(case_id, status);
CREATE INDEX IF NOT EXISTS idx_answers_run ON run_answers(run_id, field_key, revision);
CREATE INDEX IF NOT EXISTS idx_evidence_run_phase ON evidence(run_id, phase_id);
CREATE INDEX IF NOT EXISTS idx_feedback_run_phase ON owner_feedback(run_id, phase_id);
