# Part 9: Connecting to Aurora RDS (PostgreSQL) from ECS Fargate

This guide walks you through every step needed to store relational data in **Amazon Aurora (PostgreSQL-compatible)** from the Flask app running on ECS Fargate.

---

## Why Aurora RDS instead of DynamoDB?

| | DynamoDB | Aurora RDS (PostgreSQL) |
|---|---|---|
| Data model | Key-value / document (NoSQL) | Tables with rows, columns, joins (SQL) |
| Schema | Schema-less | Enforced schema |
| Queries | Limited (PK + GSI) | Full SQL — `JOIN`, `GROUP BY`, aggregates, … |
| Best for | Simple lookups, high scale | Structured relational data |

Use Aurora when your data is **relational** (users, orders, inventory, etc.).

---

## What Changed in the Code

### `requirements.txt`
Added `psycopg2-binary` — the PostgreSQL driver for Python.

```
psycopg2-binary==2.9.9
```

### `app.py`
Three things were added:

1. **Config block** — reads 5 env vars at startup:

```python
DB_HOST     = os.environ.get('DB_HOST', '')
DB_PORT     = int(os.environ.get('DB_PORT', 5432))
DB_NAME     = os.environ.get('DB_NAME', 'appdb')
DB_USER     = os.environ.get('DB_USER', '')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
```

2. **`get_db_conn()`** — opens a fresh connection per request (simple, no pool):

```python
def get_db_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        connect_timeout=5,
    )
```

3. **5 new API routes** under `/rds/`:

| Method | Path | What it does |
|--------|------|---|
| `GET` | `/rds/init` | Creates the `users` table (run once) |
| `POST` | `/rds/users` | Insert a user `{"name":"..","email":".."}` |
| `GET` | `/rds/users` | List all users |
| `GET` | `/rds/users/<id>` | Fetch one user by PK |
| `DELETE` | `/rds/users/<id>` | Delete a user |

---

## Step-by-Step Setup

### Step 1 — Create an Aurora PostgreSQL Cluster

1. Open **AWS Console → RDS → Create database**.
2. Choose **Standard create**.
3. Engine: **Amazon Aurora** → Edition: **PostgreSQL-compatible**.
4. Template: **Dev/Test** (cheapest, no Multi-AZ).
5. DB cluster identifier: `my-aurora-cluster`.
6. Master username: `appuser` (note it down).
7. Master password: set a strong password (note it down).
8. Instance class: `db.t3.medium` (smallest Aurora-compatible tier).
9. **VPC**: same VPC as your ECS cluster.
10. **Public access**: **No** (the app connects privately).
11. Click **Create database** — takes ~5 minutes.

> **After creation** → go to the cluster → copy the **Writer endpoint**  
> It looks like: `my-aurora-cluster.cluster-xxxx.eu-north-1.rds.amazonaws.com`

---

### Step 2 — Create the Database Inside the Cluster

Aurora creates a default DB named `postgres`. Create a dedicated DB for your app:

```sql
-- Connect via psql or the RDS Query Editor
CREATE DATABASE appdb;
```

Or pass `--db-name appdb` when creating the cluster in the CLI.

---

### Step 3 — Configure Security Groups

The ECS task must be able to reach Aurora on **port 5432**.

1. Go to **EC2 → Security Groups**.
2. Find the security group attached to **your Aurora cluster**.
3. Add an **Inbound rule**:
   - Type: `PostgreSQL`
   - Port: `5432`
   - Source: the **Security Group ID** of your ECS tasks (or the VPC CIDR `10.0.0.0/8`)

This means: *"allow traffic on port 5432 from my ECS containers"*.

---

### Step 4 — Store DB_PASSWORD in AWS Secrets Manager

**Never put passwords in source code or the task definition `environment` block.**

```bash
aws secretsmanager create-secret \
  --name aurora-db-password \
  --secret-string "your-strong-password" \
  --region eu-north-1
```

Note down the **ARN** returned, e.g.:  
`arn:aws:secretsmanager:eu-north-1:740994137443:secret:aurora-db-password`

Update `console-task-definition.json` — the `secrets` block already has:

```json
{
  "name": "DB_PASSWORD",
  "valueFrom": "arn:aws:secretsmanager:eu-north-1:740994137443:secret:aurora-db-password"
}
```

Replace the ARN with the one you just copied.

---

### Step 5 — Grant the ECS Task Role Permission

The ECS **Task Role** needs permission to read the secret and (optionally) connect to RDS.

#### 5a — Allow reading the secret

Go to **IAM → Roles** → find the role in `executionRoleArn` inside `console-task-definition.json`  
(e.g. `ecsTaskExecutionRole`).

Attach this inline policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadAuroraSecret",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:secretsmanager:eu-north-1:740994137443:secret:aurora-db-password"
    }
  ]
}
```

> `kms:Decrypt` is only needed if you used a customer-managed KMS key.

#### 5b — (Optional) IAM Database Authentication

If you later enable **IAM DB Auth**, you also need `rds-db:connect` on the cluster resource.  
For password auth (what we use here) this is **not required**.

---

### Step 6 — Set Non-Secret Env Vars in GitHub Secrets

Go to **Repository → Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret name | Value |
|-------------|-------|
| `DB_HOST` | `my-aurora-cluster.cluster-xxxx.eu-north-1.rds.amazonaws.com` |
| `DB_USER` | `appuser` |
| `DB_NAME` | `appdb` |

> `DB_PASSWORD` is **not** added here — it lives only in AWS Secrets Manager.

The GitHub Actions workflow has a new step that `sed`-patches these values into  
`console-task-definition.json` at CI time before registering the task definition.

---

### Step 7 — Update `console-task-definition.json`

The file already has the placeholders. Fill in the real values:

```json
{ "name": "DB_HOST", "value": "<your-writer-endpoint>" },
{ "name": "DB_PORT", "value": "5432" },
{ "name": "DB_NAME", "value": "appdb" },
{ "name": "DB_USER", "value": "appuser" }
```

And in `secrets`:

```json
{
  "name": "DB_PASSWORD",
  "valueFrom": "arn:aws:secretsmanager:eu-north-1:<ACCOUNT_ID>:secret:aurora-db-password"
}
```

---

### Step 8 — Deploy and Initialise the Table

1. **Push to `master`** → GitHub Actions builds, pushes, and deploys.
2. Once the new task is running, call the init endpoint **once**:

```bash
curl http://13.48.129.172:8000/rds/init
# {"message": "Table 'users' is ready"}

curl http://127.0.0.1:8000/rds/users

curl -X POST http://13.61.180.191:8000/rds/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "[EMAIL_ADDRESS]"}'


```

This runs `CREATE TABLE IF NOT EXISTS users (...)` inside Aurora.

---

## Testing the Endpoints

### Insert a user

```bash
curl -X POST http://YOUR_ECS_IP:8000/rds/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

Expected response (`201`):

```json
{
  "message": "User created",
  "user": {"id": 1, "name": "Alice", "email": "alice@example.com", "created": "2025-01-01 10:00:00+00:00"}
}
```

### List all users

```bash
curl http://YOUR_ECS_IP:8000/rds/users
```

### Fetch user by ID

```bash
curl http://YOUR_ECS_IP:8000/rds/users/1
```

### Delete a user

```bash
curl -X DELETE http://YOUR_ECS_IP:8000/rds/users/1
# {"message": "User id=1 deleted"}
```

---

## How Secrets Flow at Runtime

```
GitHub Actions
  └─ secrets.DB_HOST / DB_USER / DB_NAME
       └─ sed patches into console-task-definition.json
            └─ registered as new ECS task definition revision

ECS Fargate (at container start)
  └─ reads task definition
       ├─ environment[]  → DB_HOST, DB_PORT, DB_NAME, DB_USER  (plain text)
       └─ secrets[]      → DB_PASSWORD  ← pulled from Secrets Manager by the ECS agent
                                           NEVER appears in the task definition file
```

---

## Troubleshooting

| Error message | Cause | Fix |
|---|---|---|
| `Missing RDS env vars: DB_HOST, DB_USER, DB_PASSWORD` | Env vars not set | Check task definition environment/secrets blocks |
| `could not connect to server: Connection refused` | Wrong host or port | Verify `DB_HOST` endpoint; check security group allows port 5432 |
| `FATAL: password authentication failed` | Wrong password | Verify secret in Secrets Manager matches what was set on the DB |
| `FATAL: database "appdb" does not exist` | DB not created | Run `CREATE DATABASE appdb;` via psql |
| `AccessDeniedException` on startup | Task role missing secret permission | Add `secretsmanager:GetSecretValue` to the task execution role |
| `duplicate key value violates unique constraint "users_email_key"` | Email already exists | App returns `409 Conflict` — use a different email |

---

## Local Development

For running the app locally, add to `.env`:

```dotenv
DB_HOST=your-aurora-cluster.cluster-xxxx.eu-north-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=appdb
DB_USER=appuser
DB_PASSWORD=your-password-here
```

> **Tip:** Aurora is not free even in dev mode. For pure local testing, run a local PostgreSQL:  
> `docker run -p 5432:5432 -e POSTGRES_PASSWORD=test postgres:16`  
> and set `DB_HOST=localhost`.
