# Part 8: Integrating S3 and DynamoDB

This guide explains how to add AWS S3 (object storage) and DynamoDB (NoSQL database) to the Flask application so it can persist data in the cloud.

---

## What Was Added

| Component | Purpose |
|-----------|---------|
| **S3** | Store and retrieve arbitrary files / blobs |
| **DynamoDB** | Store structured key-value / document items |
| **boto3** | Official AWS SDK for Python |

---

## Step 1: Create an S3 Bucket

1. Go to **AWS Console → S3 → Create bucket**.
2. Bucket name: e.g. `my-python-app-bucket` *(must be globally unique)*.
3. Region: same as your ECS cluster (`eu-north-1`).
4. Leave **Block all public access** enabled (the app accesses it privately via IAM).
5. Click **Create bucket**.

---

## Step 2: Create a DynamoDB Table

1. Go to **AWS Console → DynamoDB → Create table**.
2. Table name: e.g. `python-app-items`.
3. Partition key: `id` (type **String**).
4. Capacity mode: **On-demand** (pay per request, cheapest for dev).
5. Click **Create table**.

---

## Step 3: Grant the ECS Task IAM Permissions

Your ECS task runs under a **Task Role**. That role needs permission to access S3 and DynamoDB.

### 3a – Create / update the Task Role Policy

Go to **IAM → Roles** → find the role assigned to your ECS task definition (e.g. `ecsTaskExecutionRole` or a custom one).

Attach an **inline policy** (or create a new managed policy):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-python-app-bucket",
        "arn:aws:s3:::my-python-app-bucket/*"
      ]
    },
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:eu-north-1:YOUR_ACCOUNT_ID:table/python-app-items"
    }
  ]
}
```

> Replace `my-python-app-bucket`, `eu-north-1`, `YOUR_ACCOUNT_ID`, and `python-app-items` with your actual values.

---

## Step 4: Set Environment Variables

The app reads two environment variables at startup:

| Variable | Description |
|----------|-------------|
| `S3_BUCKET_NAME` | Name of your S3 bucket |
| `DYNAMODB_TABLE` | Name of your DynamoDB table |

### Local development (`.env` file)

```dotenv
S3_BUCKET_NAME="my-python-app-bucket"
DYNAMODB_TABLE="python-app-items"
```

### ECS / Fargate (Task Definition)

Add environment variables in the **Container configuration** of your task definition:

```json
{
  "environment": [
    { "name": "S3_BUCKET_NAME",  "value": "my-python-app-bucket" },
    { "name": "DYNAMODB_TABLE",  "value": "python-app-items" }
  ]
}
```

### GitHub Actions / Secrets

Add `S3_BUCKET_NAME` and `DYNAMODB_TABLE` to **Repository → Settings → Secrets and variables → Actions** (already wired up in `deploy-ecr_GB_Actions.yml`).

---

## Step 5: API Endpoints Reference

Once deployed, the following endpoints are available:

### Health Check

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Returns `{"status":"ok","region":"..."}` |

### S3 Endpoints

| Method | Path | Body / Params | Description |
|--------|------|---------------|-------------|
| `GET`  | `/s3/list` | — | List all objects in the bucket |
| `PUT`  | `/s3/upload` | `{"key":"path/file.txt","content":"..."}` | Upload text content |
| `GET`  | `/s3/download/<key>` | — | Read object content by key |

#### Example – Upload a file

```bash
curl -X PUT http://YOUR_IP:8000/s3/upload \
  -H "Content-Type: application/json" \
  -d '{"key": "hello.txt", "content": "Hello from Flask!"}'
```

#### Example – Read it back

```bash
curl http://YOUR_IP:8000/s3/download/hello.txt
```

### DynamoDB Endpoints

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `POST` | `/dynamodb/put` | Any JSON with an `id` field | Insert/overwrite item |
| `GET`  | `/dynamodb/get/<id>` | — | Fetch item by `id` |
| `GET`  | `/dynamodb/scan` | — | Return up to 20 items |

#### Example – Store an item

```bash
curl -X POST http://YOUR_IP:8000/dynamodb/put \
  -H "Content-Type: application/json" \
  -d '{"id": "user-1", "name": "Alice", "role": "admin"}'
```

#### Example – Retrieve it

```bash
curl http://YOUR_IP:8000/dynamodb/get/user-1
```

---

## Troubleshooting

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `S3_BUCKET_NAME environment variable is not set` | Env var missing | Set `S3_BUCKET_NAME` in task definition or `.env` |
| `DYNAMODB_TABLE environment variable is not set` | Env var missing | Set `DYNAMODB_TABLE` in task definition or `.env` |
| `AccessDenied` from boto3 | Missing IAM permission | Attach the policy in Step 3 to the Task Role |
| `NoSuchBucket` | Bucket doesn't exist or wrong region | Verify bucket name and region |
| `ResourceNotFoundException` | DynamoDB table doesn't exist | Create the table as shown in Step 2 |
