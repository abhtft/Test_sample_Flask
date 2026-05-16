# Part 10: `psql` & PostgreSQL Command Reference

A hands-on cheat-sheet for interacting with your **Amazon Aurora (PostgreSQL)** cluster.  
Everything here works in the standard `psql` CLI, and most SQL commands also work inside the  
**AWS RDS Query Editor** or any GUI client (DBeaver, TablePlus, pgAdmin).

---

## 1. Connecting to Aurora with `psql`

### From your local machine (Aurora must have public access OR you use an SSH tunnel)

```bash
psql \
  --host=database1.cb0080sgecg7.eu-north-1.rds.amazonaws.com \
  --port=5432 \
  --username=postgres \
  --dbname=postgres
```

**Short form (DSN-style):**
```bash
psql "host=my-aurora-cluster.cluster-xxxx.eu-north-1.rds.amazonaws.com \
      port=5432 dbname=appdb user=appuser password=yourpassword sslmode=require"
```

**Using environment variables (avoid typing password each time):**
```bash
export PGHOST=my-aurora-cluster.cluster-xxxx.eu-north-1.rds.amazonaws.com
export PGPORT=5432
export PGDATABASE=appdb
export PGUSER=appuser
export PGPASSWORD=yourpassword   # or use ~/.pgpass file for safety

psql   # uses the env vars automatically
```

### From inside the ECS container (exec into a running task)

```bash
# 1. Find your cluster and task ARN
aws ecs list-tasks --cluster my-ecs-cluster

# 2. Open an interactive shell inside the container
aws ecs execute-command \
  --cluster my-ecs-cluster \
  --task <task-arn> \
  --container flask-app \
  --interactive \
  --command "/bin/sh"

# 3. Once inside, connect to Aurora
psql -h $DB_HOST -U $DB_USER -d $DB_NAME
```

> **Prerequisite:** `enableExecuteCommand` must be `true` in the task definition, and the task role needs the `ssmmessages:*` permissions.

---

## 2. `psql` Meta-Commands (backslash commands)

These are `psql`-specific shortcuts — they are NOT SQL and don't need a semicolon.

| Command | What it does |
|---------|-------------|
| `\l` or `\list` | List all databases |
| `\c dbname` | Switch to a different database |
| `\dt` | List all tables in the current schema |
| `\dt schema.*` | List tables in a specific schema |
| `\d tablename` | Describe a table (columns, types, constraints) |
| `\d+ tablename` | Describe with extra detail (indexes, storage) |
| `\di` | List all indexes |
| `\ds` | List all sequences |
| `\dv` | List all views |
| `\df` | List all functions |
| `\dn` | List all schemas |
| `\du` | List all roles/users |
| `\dp tablename` | Show table permissions |
| `\timing` | Toggle query execution time display |
| `\x` | Toggle expanded/pretty output mode |
| `\e` | Open last query in a text editor |
| `\i file.sql` | Execute SQL from a file |
| `\o file.txt` | Send query output to a file |
| `\copy` | Import/export CSV (client-side, no superuser needed) |
| `\q` | Quit `psql` |
| `\?` | Help for all meta-commands |
| `\h SELECT` | SQL syntax help for a specific command |

---

## 3. Database Management

```sql
-- List databases
\l

-- Create a new database
CREATE DATABASE appdb;
CREATE DATABASE staging_db OWNER appuser;

-- Drop a database (cannot be done while connected to it)
DROP DATABASE staging_db;

-- Rename a database
ALTER DATABASE old_name RENAME TO new_name;

-- Connect to a database
\c appdb

-- Show current database
SELECT current_database();

-- Show current user
SELECT current_user;

-- Show server version
SELECT version();
```

---

## 4. Schema Management

```sql
-- List schemas
\dn

-- Create a schema (namespace for tables)
CREATE SCHEMA analytics;

-- Set default search path (which schema psql looks in first)
SET search_path TO analytics, public;

-- Show current search path
SHOW search_path;

-- Drop a schema
DROP SCHEMA analytics CASCADE;  -- CASCADE drops all objects inside it
```

---

## 5. Table Operations

### Create

```sql
-- Basic table (mirrors the 'users' table in app.py)
CREATE TABLE users (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(255) UNIQUE NOT NULL,
    created    TIMESTAMPTZ DEFAULT now()
);

-- Table with more data types
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    price       NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock       INTEGER DEFAULT 0,
    is_active   BOOLEAN DEFAULT TRUE,
    tags        TEXT[],                          -- Array column
    metadata    JSONB,                           -- JSON column
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);

-- Create only if it doesn't exist (safe for re-runs)
CREATE TABLE IF NOT EXISTS users ( ... );
```

### Inspect

```sql
-- List all tables
\dt

-- Describe a table's structure
\d users
\d+ users     -- with indexes and extra info

-- List all columns for a table
SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
```

### Alter

```sql
-- Add a column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Drop a column
ALTER TABLE users DROP COLUMN phone;

-- Rename a column
ALTER TABLE users RENAME COLUMN name TO full_name;

-- Change a column's data type
ALTER TABLE users ALTER COLUMN phone TYPE TEXT;

-- Add a NOT NULL constraint
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;

-- Remove NOT NULL
ALTER TABLE users ALTER COLUMN phone DROP NOT NULL;

-- Add a default value
ALTER TABLE users ALTER COLUMN phone SET DEFAULT 'N/A';

-- Rename a table
ALTER TABLE users RENAME TO app_users;
```

### Drop

```sql
DROP TABLE users;                   -- Error if table has dependent objects
DROP TABLE users CASCADE;           -- Also drops dependent views, FK references
DROP TABLE IF EXISTS users;         -- Safe: no error if table doesn't exist
TRUNCATE TABLE users;               -- Delete all rows, keep structure (fast)
TRUNCATE TABLE users RESTART IDENTITY; -- Also resets SERIAL counter to 1
```

---

## 6. CRUD — Insert, Select, Update, Delete

### INSERT

```sql
-- Insert a single row
INSERT INTO users (name, email)
VALUES ('Alice', 'alice@example.com');

-- Insert and return the generated id
INSERT INTO users (name, email)
VALUES ('Bob', 'bob@example.com')
RETURNING id, created;

-- Insert multiple rows at once
INSERT INTO users (name, email) VALUES
  ('Carol', 'carol@example.com'),
  ('Dave',  'dave@example.com');

-- Insert or do nothing on conflict (upsert — ignore duplicate)
INSERT INTO users (name, email)
VALUES ('Alice', 'alice@example.com')
ON CONFLICT (email) DO NOTHING;

-- Insert or update on conflict (upsert — overwrite)
INSERT INTO users (name, email)
VALUES ('Alice', 'alice@example.com')
ON CONFLICT (email)
DO UPDATE SET name = EXCLUDED.name, updated_at = now();
```

### SELECT

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT id, name, email FROM users;

-- Filter with WHERE
SELECT * FROM users WHERE email = 'alice@example.com';
SELECT * FROM users WHERE id > 5;
SELECT * FROM users WHERE name LIKE 'A%';       -- starts with A
SELECT * FROM users WHERE name ILIKE 'a%';      -- case-insensitive
SELECT * FROM users WHERE name IN ('Alice', 'Bob');
SELECT * FROM users WHERE email IS NOT NULL;
SELECT * FROM users WHERE created > now() - INTERVAL '7 days';

-- Sort
SELECT * FROM users ORDER BY created DESC;
SELECT * FROM users ORDER BY name ASC, email DESC;

-- Limit and offset (pagination)
SELECT * FROM users LIMIT 10 OFFSET 20;  -- page 3 with 10 per page

-- Count
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM users WHERE is_active = TRUE;

-- Distinct
SELECT DISTINCT name FROM users;

-- Alias
SELECT name AS username, email AS contact FROM users;
```

### UPDATE

```sql
-- Update a specific row
UPDATE users SET name = 'Alicia' WHERE id = 1;

-- Update multiple columns
UPDATE users
SET name = 'Alicia', email = 'alicia@example.com'
WHERE id = 1;

-- Update and return the changed row
UPDATE users
SET name = 'Alicia'
WHERE id = 1
RETURNING *;

-- Update all rows (no WHERE — be careful!)
UPDATE users SET is_active = TRUE;
```

### DELETE

```sql
-- Delete a specific row
DELETE FROM users WHERE id = 1;

-- Delete with RETURNING
DELETE FROM users WHERE id = 1 RETURNING *;

-- Delete multiple rows
DELETE FROM users WHERE email LIKE '%@test.com';

-- Delete all rows (keeps table structure)
DELETE FROM users;
```

---

## 7. Indexes

Indexes speed up `SELECT` queries with `WHERE`, `JOIN`, and `ORDER BY`.

```sql
-- Create an index
CREATE INDEX idx_users_email ON users (email);

-- Create a unique index
CREATE UNIQUE INDEX idx_users_email_unique ON users (email);

-- Create a composite index (multiple columns)
CREATE INDEX idx_users_name_created ON users (name, created DESC);

-- Partial index (only index active users)
CREATE INDEX idx_active_users ON users (email) WHERE is_active = TRUE;

-- List all indexes on a table
\di users*

-- Or via SQL
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'users';

-- Drop an index
DROP INDEX idx_users_email;

-- Show query plan (does it use the index?)
EXPLAIN SELECT * FROM users WHERE email = 'alice@example.com';
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'alice@example.com';  -- actually runs it
```

---

## 8. Aggregates & Grouping

```sql
-- Count, sum, avg, min, max
SELECT COUNT(*) AS total_users FROM users;
SELECT AVG(price) AS avg_price FROM products;
SELECT MIN(price), MAX(price) FROM products;
SELECT SUM(stock) FROM products WHERE is_active = TRUE;

-- Group by
SELECT name, COUNT(*) AS count
FROM users
GROUP BY name
ORDER BY count DESC;

-- Group with HAVING (filter on aggregated result)
SELECT name, COUNT(*) AS count
FROM users
GROUP BY name
HAVING COUNT(*) > 1;   -- only names that appear more than once
```

---

## 9. JOINs

```sql
-- Setup: orders table referencing users
CREATE TABLE orders (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
    product    TEXT NOT NULL,
    amount     NUMERIC(10, 2),
    ordered_at TIMESTAMPTZ DEFAULT now()
);

-- INNER JOIN — only rows that match in both tables
SELECT u.name, o.product, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN — all users, even those with no orders
SELECT u.name, o.product
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- COUNT orders per user
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name
ORDER BY order_count DESC;
```

---

## 10. Transactions

```sql
-- Begin a transaction
BEGIN;

  INSERT INTO users (name, email) VALUES ('Test', 'test@example.com');
  UPDATE users SET name = 'Test2' WHERE email = 'test@example.com';

COMMIT;    -- save changes

-- Or roll back if something went wrong
BEGIN;
  DELETE FROM users WHERE id = 5;
ROLLBACK;  -- undo — row is NOT deleted

-- Savepoints (partial rollback)
BEGIN;
  INSERT INTO users (name, email) VALUES ('A', 'a@x.com');
  SAVEPOINT sp1;
  INSERT INTO users (name, email) VALUES ('B', 'b@x.com');
  ROLLBACK TO SAVEPOINT sp1;  -- only B is rolled back
COMMIT;                        -- A is saved
```

---

## 11. Views

```sql
-- Create a view (saved query)
CREATE VIEW active_users AS
SELECT id, name, email
FROM users
WHERE is_active = TRUE;

-- Query the view like a table
SELECT * FROM active_users;

-- Replace/update a view
CREATE OR REPLACE VIEW active_users AS
SELECT id, name, email, created
FROM users
WHERE is_active = TRUE;

-- Drop a view
DROP VIEW active_users;
```

---

## 12. Sequences & Serial

`SERIAL` is shorthand for a sequence + integer column.

```sql
-- Check the current value of a sequence
SELECT last_value FROM users_id_seq;

-- Reset the sequence (useful after TRUNCATE)
ALTER SEQUENCE users_id_seq RESTART WITH 1;

-- Advance the sequence manually
SELECT nextval('users_id_seq');

-- Set to a specific value
SELECT setval('users_id_seq', 100);
```

---

## 13. JSON & JSONB Columns

```sql
-- Insert JSON data
INSERT INTO products (name, price, metadata)
VALUES ('Widget', 9.99, '{"color": "red", "weight": 0.5}');

-- Query a JSON field
SELECT name, metadata->>'color' AS color FROM products;

-- Filter by JSON field
SELECT * FROM products WHERE metadata->>'color' = 'red';

-- Update a JSON field
UPDATE products
SET metadata = jsonb_set(metadata, '{color}', '"blue"')
WHERE name = 'Widget';
```

---

## 14. Common Utility Queries

```sql
-- Show all running queries
SELECT pid, query, state, now() - query_start AS duration
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Kill a slow query
SELECT pg_terminate_backend(<pid>);

-- Show table sizes
SELECT
  relname AS table_name,
  pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Show table row counts (approximate, fast)
SELECT relname, n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

-- Show lock conflicts
SELECT pid, locktype, relation::regclass, mode, granted
FROM pg_locks
WHERE NOT granted;

-- Force VACUUM to reclaim space after many deletes
VACUUM ANALYZE users;
```

---

## 15. User & Permission Management

```sql
-- List all users/roles
\du

-- Create a new user
CREATE USER readonly_user WITH PASSWORD 'secret';

-- Grant SELECT only on a table
GRANT SELECT ON users TO readonly_user;

-- Grant all privileges on all tables in a schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO appuser;

-- Grant usage on sequences (needed for INSERT with SERIAL)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO appuser;

-- Revoke permissions
REVOKE INSERT ON users FROM readonly_user;

-- Drop a user
DROP USER readonly_user;

-- Change a password
ALTER USER appuser WITH PASSWORD 'new-strong-password';
```

---

## 16. Backup & Restore (outside `psql`)

```bash
# Dump a single database to a file
pg_dump -h <host> -U appuser -d appdb -F c -f appdb_backup.dump

# Restore from a dump
pg_restore -h <host> -U appuser -d appdb -F c appdb_backup.dump

# Plain SQL dump (human-readable)
pg_dump -h <host> -U appuser -d appdb > appdb_backup.sql

# Restore plain SQL dump
psql -h <host> -U appuser -d appdb < appdb_backup.sql
```

---

## 17. Aurora-Specific Tips

| Topic | Notes |
|-------|-------|
| **Endpoints** | Use the **Writer endpoint** for reads+writes; use **Reader endpoint** for read-only replicas |
| **Failover** | Aurora automatically promotes a reader on writer failure |
| **SSL** | Always use `sslmode=require` when connecting to Aurora from outside a VPC |
| **Parameter Groups** | Tune `shared_buffers`, `max_connections` via RDS Parameter Groups — not `postgresql.conf` |
| **Logs** | Enable **PostgreSQL logs** in the RDS console → go to CloudWatch Logs |
| **Slow query log** | Set `log_min_duration_statement = 1000` (ms) in the parameter group |
| **`pg_sleep`** | `SELECT pg_sleep(5);` — useful for testing connection timeouts |
| **Autovacuum** | Aurora runs autovacuum automatically; you rarely need to run `VACUUM` manually |
| **IAM Auth** | Can replace password auth; requires `rds-db:connect` IAM permission + token generation |

---

## 18. Quick Reference Card

```
┌──────────────────────────────────────────────────────────────────┐
│  CONNECT    psql -h HOST -U USER -d DBNAME                       │
│  LIST DBS   \l                                                    │
│  USE DB     \c appdb                                              │
│  LIST TABLES\dt                                                   │
│  DESC TABLE \d users                                              │
│  QUIT       \q                                                    │
├──────────────────────────────────────────────────────────────────┤
│  CREATE     CREATE TABLE t (id SERIAL PRIMARY KEY, ...);         │
│  INSERT     INSERT INTO t (col) VALUES ('val') RETURNING id;     │
│  SELECT     SELECT * FROM t WHERE col = 'x' LIMIT 10;            │
│  UPDATE     UPDATE t SET col='y' WHERE id=1 RETURNING *;         │
│  DELETE     DELETE FROM t WHERE id=1;                            │
├──────────────────────────────────────────────────────────────────┤
│  INDEX      CREATE INDEX idx ON t (col);                          │
│  EXPLAIN    EXPLAIN ANALYZE SELECT ...;                           │
│  VACUUM     VACUUM ANALYZE t;                                     │
│  TXNS       BEGIN; ...; COMMIT; / ROLLBACK;                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Related Docs

- [09-aurora-rds.md](./09-aurora-rds.md) — Aurora cluster setup, ECS integration, secrets management
- [psql documentation](https://www.postgresql.org/docs/current/app-psql.html)
- [PostgreSQL SQL syntax reference](https://www.postgresql.org/docs/current/sql-commands.html)
