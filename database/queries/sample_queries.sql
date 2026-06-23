-- =============================================================
-- CivicLens Sample Analytical Queries
-- =============================================================

-- Total clients served by month
SELECT
    DATE_TRUNC('month', record_date) AS month,
    SUM(clients_served) AS total_clients,
    SUM(meals_distributed) AS total_meals
FROM operational_records
GROUP BY month
ORDER BY month;

-- Breakdown by program type
SELECT
    program_type,
    COUNT(*) AS events,
    SUM(clients_served) AS total_clients,
    SUM(meals_distributed) AS total_meals,
    ROUND(AVG(volunteer_hours), 1) AS avg_volunteer_hours
FROM operational_records
GROUP BY program_type
ORDER BY total_clients DESC;

-- Top locations by clients served
SELECT
    location,
    zip_code,
    SUM(clients_served) AS total_clients
FROM operational_records
GROUP BY location, zip_code
ORDER BY total_clients DESC
LIMIT 10;

-- Weekly trend for clients served
SELECT
    DATE_TRUNC('week', record_date) AS week,
    SUM(clients_served) AS clients_this_week
FROM operational_records
GROUP BY week
ORDER BY week;

-- Data quality: rows with missing meals data
SELECT *
FROM operational_records
WHERE meals_distributed IS NULL OR meals_distributed = 0
  AND program_type != 'Health Screening'
ORDER BY record_date;
