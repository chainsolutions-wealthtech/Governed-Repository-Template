CREATE TABLE IF NOT EXISTS first_touch_capture_records (
  capture_id TEXT PRIMARY KEY,
  schema_id TEXT NOT NULL,
  observed_at TEXT,
  repository TEXT,
  actor TEXT,
  capture_digest TEXT,
  source_path TEXT,
  raw_json TEXT NOT NULL,
  raw_json_sha256 TEXT NOT NULL,
  path_count INTEGER NOT NULL CHECK(path_count >= 0),
  terminal_value_count INTEGER NOT NULL CHECK(terminal_value_count >= 0),
  api_attempt_count INTEGER NOT NULL CHECK(api_attempt_count >= 0),
  mutation_authority_granted INTEGER NOT NULL CHECK(mutation_authority_granted IN (0,1)),
  interpretation_applied INTEGER NOT NULL CHECK(interpretation_applied IN (0,1))
);

CREATE TABLE IF NOT EXISTS first_touch_capture_nodes (
  capture_id TEXT NOT NULL,
  node_ordinal INTEGER NOT NULL CHECK(node_ordinal > 0),
  json_path TEXT NOT NULL,
  parent_path TEXT,
  key_name TEXT,
  array_index INTEGER,
  value_type TEXT NOT NULL CHECK(value_type IN (
    'null','boolean','number','string','array','object'
  )),
  is_terminal INTEGER NOT NULL CHECK(is_terminal IN (0,1)),
  value_json TEXT NOT NULL,
  PRIMARY KEY(capture_id, node_ordinal),
  UNIQUE(capture_id, json_path),
  FOREIGN KEY(capture_id) REFERENCES first_touch_capture_records(capture_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS first_touch_capture_api_attempts (
  capture_id TEXT NOT NULL,
  attempt_ordinal INTEGER NOT NULL CHECK(attempt_ordinal > 0),
  name TEXT,
  url TEXT,
  http_status INTEGER,
  response_json TEXT NOT NULL,
  PRIMARY KEY(capture_id, attempt_ordinal),
  FOREIGN KEY(capture_id) REFERENCES first_touch_capture_records(capture_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_first_touch_capture_nodes_path
  ON first_touch_capture_nodes(json_path);

CREATE INDEX IF NOT EXISTS idx_first_touch_capture_nodes_key
  ON first_touch_capture_nodes(key_name);

CREATE INDEX IF NOT EXISTS idx_first_touch_capture_nodes_type
  ON first_touch_capture_nodes(value_type);

CREATE INDEX IF NOT EXISTS idx_first_touch_capture_api_name
  ON first_touch_capture_api_attempts(name);
