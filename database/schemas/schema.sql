-- =============================================================
-- CivicLens Database Schema
-- =============================================================

-- Datasets table: tracks each uploaded file
CREATE TABLE IF NOT EXISTS datasets (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    filename    VARCHAR(255) NOT NULL,
    row_count   INTEGER,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    status      VARCHAR(50) DEFAULT 'pending'  -- pending | cleaned | error
);

-- Operational records table: cleaned data rows
CREATE TABLE IF NOT EXISTS operational_records (
    id                  SERIAL PRIMARY KEY,
    dataset_id          INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
    record_date         DATE,
    location            VARCHAR(255),
    program_type        VARCHAR(255),
    clients_served      INTEGER,
    meals_distributed   INTEGER,
    inventory_lbs       NUMERIC(10, 2),
    volunteer_hours     NUMERIC(8, 2),
    zip_code            VARCHAR(20),
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- Claude query log: tracks all AI queries
CREATE TABLE IF NOT EXISTS claude_queries (
    id              SERIAL PRIMARY KEY,
    dataset_id      INTEGER REFERENCES datasets(id),
    query_type      VARCHAR(50),  -- qa | summary | report
    user_prompt     TEXT,
    claude_response TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Data quality log: validation issues per dataset
CREATE TABLE IF NOT EXISTS data_quality_log (
    id          SERIAL PRIMARY KEY,
    dataset_id  INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
    issue_type  VARCHAR(100),   -- duplicate | null | type_error | outlier
    column_name VARCHAR(100),
    row_index   INTEGER,
    detail      TEXT,
    flagged_at  TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_records_dataset ON operational_records(dataset_id);
CREATE INDEX IF NOT EXISTS idx_records_date ON operational_records(record_date);
CREATE INDEX IF NOT EXISTS idx_queries_dataset ON claude_queries(dataset_id);
