CREATE TABLE IF NOT EXISTS first_touch_probe_records (
  probe_id TEXT PRIMARY KEY,
  correlation_key TEXT NOT NULL UNIQUE,
  source_path TEXT NOT NULL UNIQUE,
  status TEXT,
  scope TEXT,
  repository TEXT,
  original_issue_number INTEGER,
  original_issue_created_at TEXT,
  document_sha256 TEXT NOT NULL,
  raw_markdown TEXT NOT NULL,
  line_count INTEGER NOT NULL CHECK(line_count >= 0),
  section_count INTEGER NOT NULL CHECK(section_count >= 0),
  observation_count INTEGER NOT NULL CHECK(observation_count >= 0)
);

CREATE TABLE IF NOT EXISTS first_touch_probe_lines (
  probe_id TEXT NOT NULL,
  line_number INTEGER NOT NULL CHECK(line_number > 0),
  section_ordinal INTEGER,
  section_heading TEXT,
  line_text TEXT NOT NULL,
  PRIMARY KEY(probe_id, line_number),
  FOREIGN KEY(probe_id) REFERENCES first_touch_probe_records(probe_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS first_touch_probe_observations (
  probe_id TEXT NOT NULL,
  observation_id TEXT NOT NULL,
  section_ordinal INTEGER,
  section_heading TEXT,
  observation_key TEXT NOT NULL,
  value_text TEXT NOT NULL,
  value_json TEXT NOT NULL,
  value_type TEXT NOT NULL,
  source_line_number INTEGER NOT NULL CHECK(source_line_number > 0),
  source_kind TEXT NOT NULL CHECK(source_kind IN (
    'HEADER_METADATA',
    'BULLET_KEY_VALUE',
    'LABEL_VALUE',
    'RAW_ANCHOR'
  )),
  PRIMARY KEY(probe_id, observation_id),
  FOREIGN KEY(probe_id) REFERENCES first_touch_probe_records(probe_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_first_touch_probe_observation_key
  ON first_touch_probe_observations(observation_key);

CREATE INDEX IF NOT EXISTS idx_first_touch_probe_lines_section
  ON first_touch_probe_lines(probe_id, section_ordinal);
