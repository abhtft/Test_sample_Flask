# 11 — DynamoDB CRUD via Flask API

> **Table used in this guide:** `ABCD`  
> **Partition key:** `partition` (String)  
> **AWS Region:** `eu-north-1` (Stockholm)

---

## 1. What Is DynamoDB?

Amazon DynamoDB is a fully-managed, serverless **NoSQL key-value and document database**.
Unlike Aurora/PostgreSQL (relational, SQL, schema-first), DynamoDB is:

| Feature | DynamoDB | PostgreSQL (Aurora) |
|---|---|---|
| Schema | Flexible / schema-less | Fixed columns, strict types |
| Scaling | Auto-scales (serverless) | Vertical + read-replicas |
| Query | Key-based / scan | Full SQL |
| Best for | High-throughput, simple lookups | Complex queries, relations |
| Pricing | Pay per read/write unit | Pay per instance hour |

---

## 2. DynamoDB Table — `ABCD`

The table was created in the AWS Console with:

| Property | Value |
|---|---|
| Table name | `ABCD` |
| Partition key | `partition` (type: **String**) |
| Sort key | *(none)* |
| Billing mode | On-demand (pay-per-request) |
| Deletion protection | Off |

> **Key concept:** Every item **must** contain the `partition` attribute. All other attributes are optional and can differ per item (schema-less).

---

## 3. How Authentication Works

### On ECS (in production)
The ECS task authenticates to DynamoDB through its **IAM Task Role** — no credentials are stored anywhere. The task definition already declares a `taskRoleArn`.

### Locally (development)
boto3 reads credentials from `~/.aws/credentials` or environment variables:
```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=eu-north-1
```
Run `aws configure` to set these up once.

---

## 4. Required IAM Permissions

Attach the following inline policy to your **ECS Task Role** (or local IAM user):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:eu-north-1:<ACCOUNT_ID>:table/ABCD"
    }
  ]
}
```

Replace `<ACCOUNT_ID>` with your 12-digit AWS account number.

---

## 5. Environment Variables

Add these to your `.env` locally and to the ECS task definition for production:

```bash
AWS_REGION=eu-north-1
DYNAMODB_TABLE=ABCD
```

In `console-task-definition.json`, add inside `"environment"`:
```json
{ "name": "AWS_REGION",      "value": "eu-north-1" },
{ "name": "DYNAMODB_TABLE",  "value": "ABCD"       }
```

> When running on ECS, **no `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` are needed** — the task role handles it automatically.

---

## 6. How the Code Works (`app.py`)

### SDK setup
```python
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

AWS_REGION     = os.environ.get('AWS_REGION', 'eu-north-1')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ABCD')

def get_dynamo_table():
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    return dynamodb.Table(DYNAMODB_TABLE)
```

- `boto3.resource('dynamodb')` creates a high-level resource client.
- `.Table(name)` returns a Table object bound to `ABCD`.
- boto3 auto-discovers credentials from the environment / IAM role.

---

## 7. API Endpoints — Full Reference

Base URL (local): `http://localhost:8000`  
Base URL (ECS):   `http://<ECS_TASK_PUBLIC_IP>:8000`

### 7.1 Create Item — `POST /dynamo/items`

Inserts a new item (or **overwrites** if the same `partition` key already exists).

**Request body** — JSON, must include `partition`:
```json
{
  "partition": "user#001",
  "name": "Abhishek",
  "email": "abhi@example.com",
  "role": "admin"
}
```

**curl:**
```bash
curl -X POST http://localhost:8000/dynamo/items \
  -H "Content-Type: application/json" \
  -d '{"partition":"user#001","name":"Abhishek","email":"abhi@example.com","role":"admin"}'
```

**Success response (201):**
```json
{
  "message": "Item created/updated",
  "item": {
    "partition": "user#001",
    "name": "Abhishek",
    "email": "abhi@example.com",
    "role": "admin"
  }
}
```

**Error (400)** — missing `partition` key:
```json
{ "error": "'partition' key is required" }
```

---

### 7.2 List All Items — `GET /dynamo/items`

Performs a **table scan** and returns all items. Accepts optional `?limit=N` (max 1000, default 100).

> ⚠️ **Scan reads every item in the table.** Use sparingly on large tables.

**curl:**
```bash
curl http://localhost:8000/dynamo/items
curl "http://localhost:8000/dynamo/items?limit=10"
```

**Success response (200):**
```json
{
  "items": [
    { "partition": "user#001", "name": "Abhishek", "role": "admin" }
  ],
  "count": 1,
  "scanned": 1
}
```

---

### 7.3 Get Single Item — `GET /dynamo/items/<partition>`

Fetches one item by its exact partition key value.

**curl:**
```bash
curl http://localhost:8000/dynamo/items/user%23001
# URL-encode '#' as %23
```

**Success (200):**
```json
{
  "item": {
    "partition": "user#001",
    "name": "Abhishek",
    "email": "abhi@example.com",
    "role": "admin"
  }
}
```

**Not found (404):**
```json
{ "error": "Item with partition='user#001' not found" }
```

---

### 7.4 Update Item — `PUT /dynamo/items/<partition>`

Updates **specific attributes** of an existing item without replacing the entire record.  
The `partition` key value comes from the URL — do NOT include it in the body.

**Request body** — only the fields to change:
```json
{
  "role": "superadmin",
  "department": "engineering"
}
```

**curl:**
```bash
curl -X PUT http://localhost:8000/dynamo/items/user%23001 \
  -H "Content-Type: application/json" \
  -d '{"role":"superadmin","department":"engineering"}'
```

**Success (200):**
```json
{
  "message": "Item updated",
  "item": {
    "partition": "user#001",
    "name": "Abhishek",
    "email": "abhi@example.com",
    "role": "superadmin",
    "department": "engineering"
  }
}
```

**Not found (404):** returned when the item doesn't exist (uses `ConditionExpression`).

---

### 7.5 Delete Item — `DELETE /dynamo/items/<partition>`

Deletes an item and returns the deleted data.

**curl:**
```bash
curl -X DELETE http://localhost:8000/dynamo/items/user%23001
```

**Success (200):**
```json
{
  "message": "Item 'user#001' deleted",
  "deleted_item": {
    "partition": "user#001",
    "name": "Abhishek",
    "role": "superadmin"
  }
}
```

**Not found (404):** uses `ConditionExpression='attribute_exists(partition)'` to detect missing items before deleting.

---

## 8. Endpoint Summary Table

| Method | URL | Operation | DynamoDB API |
|--------|-----|-----------|--------------|
| `POST` | `/dynamo/items` | Create / upsert item | `put_item` |
| `GET` | `/dynamo/items` | List all items (scan) | `scan` |
| `GET` | `/dynamo/items/<key>` | Get single item | `get_item` |
| `PUT` | `/dynamo/items/<key>` | Update attributes | `update_item` |
| `DELETE` | `/dynamo/items/<key>` | Delete item | `delete_item` |

---

## 9. DynamoDB vs SQL — Mental Model

```
SQL Table    →  DynamoDB Table
SQL Row      →  DynamoDB Item
SQL Column   →  DynamoDB Attribute
Primary Key  →  Partition Key (+ optional Sort Key)
```

Key differences to remember:
- No `ALTER TABLE` needed — just add new attributes to any item.
- No `JOIN` — design your data to avoid cross-table queries.
- Reads are **eventually consistent** by default (use `ConsistentRead=True` for strong consistency).

---

## 10. Testing via ECS

Set your ECS task IP:
```powershell
$ECS_IP = "YOUR_ECS_TASK_PUBLIC_IP"
```

```bash
# Create
curl -X POST http://${ECS_IP}:8000/dynamo/items \
  -H "Content-Type: application/json" \
  -d '{"partition":"test#1","value":"hello from ECS"}'

# List
curl http://${ECS_IP}:8000/dynamo/items

# Get
curl http://${ECS_IP}:8000/dynamo/items/test%231

# Update
curl -X PUT http://${ECS_IP}:8000/dynamo/items/test%231 \
  -H "Content-Type: application/json" \
  -d '{"value":"updated","status":"active"}'

# Delete
curl -X DELETE http://${ECS_IP}:8000/dynamo/items/test%231
```

---

## 11. Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `NoCredentialsError` | boto3 can't find AWS credentials | Run `aws configure` locally; check task role in ECS |
| `AccessDeniedException` | IAM policy missing required action | Add missing `dynamodb:*` actions to the task role policy |
| `ResourceNotFoundException` | Table name wrong or wrong region | Verify `DYNAMODB_TABLE` env var and `AWS_REGION` |
| `ConditionalCheckFailedException` | PUT/DELETE on non-existent item | API returns 404; create the item first with POST |
| `ProvisionedThroughputExceededException` | Too many reads/writes | Switch table to on-demand billing in DynamoDB console |

---

## 12. Local Development Checklist

- [ ] `boto3==1.34.144` in `requirements.txt` ✅
- [ ] `.env` contains `AWS_REGION` and `DYNAMODB_TABLE` ✅
- [ ] AWS credentials configured (`aws configure` or env vars)
- [ ] DynamoDB table `ABCD` exists with partition key `partition` (String) ✅
- [ ] IAM user/role has the 6 DynamoDB actions listed in §4
