CREATE TABLE IF NOT EXISTS migrations (
    migration_id VARCHAR(17) PRIMARY KEY,
    migration_name VARCHAR(1000),
    up_hash VARCHAR(32),
    down_hash VARCHAR(32)
);
