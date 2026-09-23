-- CAT OutcomeIQ — schema.sql
-- Written for SQLite (hackathon speed) using types/constraints that also work on Postgres
-- with minimal changes (TEXT ids instead of UUID type, no SERIAL — ids are generated in app code).
-- Every table maps to an entity in Architecture.md §3. Columns marked (extended) go beyond
-- the two sample CSVs CAT provided — kept because they're needed for the causal reasoning
-- the six modules do, not added for their own sake.

PRAGMA foreign_keys = ON;

-- ============================================================
-- Reference entities
-- ============================================================

CREATE TABLE project (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    deadline        TEXT NOT NULL,              -- ISO datetime
    target_quantity REAL,
    quality_criteria TEXT                        -- json: {"tolerance_cm": 5}
);

CREATE TABLE zone (                               -- (extended) needed for jobsite memory / site stability
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES project(id),
    name            TEXT NOT NULL,
    soil_type       TEXT NOT NULL,                -- e.g. clay, sand, loam
    notes           TEXT
);

CREATE TABLE operator (
    id                TEXT PRIMARY KEY,
    name              TEXT NOT NULL,
    experience_years  REAL NOT NULL,
    certifications    TEXT                        -- json list
);

CREATE TABLE machine (
    id            TEXT PRIMARY KEY,
    model         TEXT NOT NULL,
    machine_family TEXT NOT NULL,                 -- e.g. excavator, dozer, loader (extended)
    age_years     REAL NOT NULL,
    install_date  TEXT NOT NULL
);

-- ============================================================
-- Operator Passport — evidence, not a score (see Architecture.md §6)
-- ============================================================

CREATE TABLE operator_capability_evidence (
    id                    TEXT PRIMARY KEY,
    operator_id           TEXT NOT NULL REFERENCES operator(id),
    task_type             TEXT NOT NULL,
    weather_bucket        TEXT NOT NULL,          -- 'normal' | 'adverse'
    material              TEXT,                   -- (extended) soil_type, nullable
    sample_count          INTEGER NOT NULL DEFAULT 0,
    success_count         INTEGER NOT NULL DEFAULT 0,
    avg_time_delta_pct    REAL,                    -- actual vs predicted, running avg
    avg_quality_success_pct REAL,
    confidence            REAL NOT NULL,           -- 0-1, derived from sample_count + success rate
    last_verified_at      TEXT,
    UNIQUE(operator_id, task_type, weather_bucket, material)
);

-- ============================================================
-- Machine Memory
-- ============================================================

CREATE TABLE machine_health (
    id                  TEXT PRIMARY KEY,
    machine_id          TEXT NOT NULL REFERENCES machine(id),
    engine_hours        REAL NOT NULL,
    health_pct          REAL NOT NULL,
    hydraulic_health_pct REAL NOT NULL,
    recent_fault_count  INTEGER NOT NULL DEFAULT 0,
    recorded_at         TEXT NOT NULL
);

-- ============================================================
-- Mission (Mission Contract output lives here)
-- ============================================================

CREATE TABLE mission (
    id                       TEXT PRIMARY KEY,
    project_id               TEXT NOT NULL REFERENCES project(id),
    zone_id                  TEXT NOT NULL REFERENCES zone(id),
    task_type                TEXT NOT NULL,        -- matches sample CSV: Earth Excavation, Trenching, Material Loading, Grading, Demolition
    objective_quantity       REAL NOT NULL,
    objective_unit           TEXT NOT NULL DEFAULT 'm3',
    quality_tolerance_cm     REAL,
    deadline                 TEXT NOT NULL,
    safety_constraints       TEXT,                 -- json list, e.g. ["no_entry_zone_c"]
    assigned_machine_id      TEXT REFERENCES machine(id),
    assigned_operator_id     TEXT REFERENCES operator(id),
    resources                TEXT,                  -- json, e.g. {"trucks_required": 2}
    naive_estimated_time_min REAL,                 -- (extended) simple lookup-table baseline, kept so the demo
                                                     -- can show "old estimate vs our P10/P50/P90" side by side
    start_time               TEXT NOT NULL,
    status                    TEXT NOT NULL DEFAULT 'planned',  -- planned | in_progress | complete
    scenario_tag              TEXT                  -- (extended) FALSE_IDLE / ON_TIME_LOW_QUALITY / etc, nullable,
                                                      -- used only to make the demo reproducible — never read by any model
);

-- ============================================================
-- Environment (per mission)
-- ============================================================

CREATE TABLE environment (
    id            TEXT PRIMARY KEY,
    mission_id    TEXT NOT NULL REFERENCES mission(id),
    weather       TEXT NOT NULL,                  -- Sunny | Rainy | Cloudy | Windy (matches sample CSV)
    soil_moisture REAL NOT NULL,                   -- 0-1, derived causally from weather
    visibility    TEXT NOT NULL,                   -- good | reduced | poor
    temperature_c REAL,
    wind_kph      REAL
);

-- ============================================================
-- WorkflowEvent — the "hidden variable" layer (truck/queue/material)
-- ============================================================

CREATE TABLE workflow_event (
    id                   TEXT PRIMARY KEY,
    mission_id           TEXT NOT NULL REFERENCES mission(id),
    timestamp            TEXT NOT NULL,
    truck_present        INTEGER NOT NULL,          -- 0/1
    truck_eta_min        REAL,
    queue_length         INTEGER NOT NULL DEFAULT 0,
    material_available   INTEGER NOT NULL DEFAULT 1,
    nearby_machine_count INTEGER NOT NULL DEFAULT 0
);

-- ============================================================
-- Telemetry (time-series; drives Reality Engine + Live Operation)
-- ============================================================

CREATE TABLE telemetry (
    id                       TEXT PRIMARY KEY,
    mission_id               TEXT NOT NULL REFERENCES mission(id),
    machine_id                TEXT NOT NULL REFERENCES machine(id),
    operator_id                TEXT NOT NULL REFERENCES operator(id),
    timestamp                 TEXT NOT NULL,
    engine_hours               REAL NOT NULL,
    fuel_used_l                 REAL NOT NULL,        -- matches sample CSV "Fuel Used (L)"
    load_cycles                 INTEGER NOT NULL,      -- matches sample CSV "Load Cycles"
    idle_minutes                REAL NOT NULL,          -- matches sample CSV "Idling Time (min)"
    seatbelt_status              TEXT NOT NULL,          -- Fastened | Unfastened, matches sample CSV
    occupancy_signal              INTEGER NOT NULL DEFAULT 1,  -- (extended) seat-occupancy sensor, 0/1
    machine_speed_kph              REAL NOT NULL DEFAULT 0,     -- (extended)
    machine_moving                  INTEGER NOT NULL DEFAULT 0,  -- (extended) 0/1
    control_smoothness_score         REAL,                        -- (extended) 0-1, proxy used by Reality Engine
                                                                    -- instead of camera/wearable fatigue detection
    safety_alert_triggered            INTEGER NOT NULL DEFAULT 0,  -- matches sample CSV "Safety Alert Triggered"
    safety_signal_pattern              TEXT DEFAULT 'normal'        -- (extended) normal | suspicious — feeds signal fusion
);

-- ============================================================
-- Quality
-- ============================================================

CREATE TABLE quality_observation (
    id                  TEXT PRIMARY KEY,
    mission_id          TEXT NOT NULL REFERENCES mission(id),
    timestamp           TEXT NOT NULL,
    elevation_error_cm  REAL NOT NULL,
    pass_count          INTEGER NOT NULL,
    surface_variance    REAL NOT NULL
);

-- ============================================================
-- Outcome — ground truth, used for evaluation and passport updates ONLY.
-- Never joined into a feature vector at prediction time (see Architecture.md §5 leakage rule).
-- ============================================================

CREATE TABLE outcome (
    id                    TEXT PRIMARY KEY,
    mission_id            TEXT NOT NULL UNIQUE REFERENCES mission(id),
    actual_duration_min   REAL NOT NULL,             -- matches sample CSV "Actual Time (min)"
    actual_fuel_l         REAL NOT NULL,
    quantity_completed    REAL NOT NULL,
    quality_score         REAL NOT NULL,             -- 0-1
    rework_flag           INTEGER NOT NULL DEFAULT 0,
    safety_event_count    INTEGER NOT NULL DEFAULT 0,
    delay_reason          TEXT                        -- eval/label only: truck | weather | operator | machine | none
);

-- ============================================================
-- Module outputs — uniform envelope written by every module (Architecture.md §4)
-- ============================================================

CREATE TABLE prediction (
    id            TEXT PRIMARY KEY,
    mission_id    TEXT NOT NULL REFERENCES mission(id),
    module_name   TEXT NOT NULL,               -- mission_contract | reality_engine | time_model | outcome_guardian
    generated_at  TEXT NOT NULL,
    value         TEXT NOT NULL,               -- json
    confidence    REAL NOT NULL,
    evidence      TEXT NOT NULL                -- json list
);

CREATE TABLE root_cause_attribution (
    id             TEXT PRIMARY KEY,
    mission_id     TEXT NOT NULL REFERENCES mission(id),
    generated_at   TEXT NOT NULL,
    deviation_min  REAL NOT NULL,
    contributors   TEXT NOT NULL               -- json list: [{cause, probability, evidence}]
);

CREATE TABLE what_if_scenario (
    id                  TEXT PRIMARY KEY,
    mission_id          TEXT NOT NULL REFERENCES mission(id),
    generated_at        TEXT NOT NULL,
    assumption_changed  TEXT NOT NULL,          -- json
    predicted_before     TEXT NOT NULL,          -- json
    predicted_after       TEXT NOT NULL           -- json
);

-- ============================================================
-- Indexes for the queries the modules actually run
-- ============================================================

CREATE INDEX idx_telemetry_mission_ts ON telemetry(mission_id, timestamp);
CREATE INDEX idx_workflow_mission_ts ON workflow_event(mission_id, timestamp);
CREATE INDEX idx_quality_mission_ts ON quality_observation(mission_id, timestamp);
CREATE INDEX idx_evidence_operator ON operator_capability_evidence(operator_id, task_type, weather_bucket);
CREATE INDEX idx_mission_status ON mission(status);
CREATE INDEX idx_prediction_mission_module ON prediction(mission_id, module_name);
