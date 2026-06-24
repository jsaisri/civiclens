-- =============================================================
-- CivicLens Database Schema (MySQL)
-- Run this inside MySQL after creating the civiclens database
-- =============================================================

-- Datasets table: tracks each uploaded file
CREATE TABLE IF NOT EXISTS datasets (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    filename    VARCHAR(255) NOT NULL,
    row_count   INT,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status      VARCHAR(50) DEFAULT 'pending'
);

-- Operational records table: cleaned data rows
CREATE TABLE IF NOT EXISTS operational_records (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id          INT,
    record_date         DATE,
    location            VARCHAR(255),
    program_type        VARCHAR(255),
    clients_served      INT,
    meals_distributed   INT,
    inventory_lbs       DECIMAL(10, 2),
    volunteer_hours     DECIMAL(8, 2),
    zip_code            VARCHAR(20),
    notes               TEXT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
);

-- Claude query log: tracks all AI queries
CREATE TABLE IF NOT EXISTS claude_queries (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id      INT,
    query_type      VARCHAR(50),
    user_prompt     TEXT,
    claude_response TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);

-- Data quality log: validation issues per dataset
CREATE TABLE IF NOT EXISTS data_quality_log (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id  INT,
    issue_type  VARCHAR(100),
    column_name VARCHAR(100),
    row_index   INT,
    detail      TEXT,
    flagged_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_records_dataset ON operational_records(dataset_id);
CREATE INDEX IF NOT EXISTS idx_records_date    ON operational_records(record_date);
CREATE INDEX IF NOT EXISTS idx_queries_dataset ON claude_queries(dataset_id);
