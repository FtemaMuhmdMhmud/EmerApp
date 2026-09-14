DROP TABLE IF EXISTS patient_cases;

CREATE TABLE patient_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    triage_color TEXT NOT NULL CHECK (triage_color IN ('RED', 'YELLOW', 'GREEN')),
    shock_index REAL,
    step_reached TEXT NOT NULL,
    action_plan TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_created_at ON patient_cases(created_at DESC);

CREATE INDEX idx_triage_color ON patient_cases(triage_color);
