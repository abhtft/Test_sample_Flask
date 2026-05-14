from flask import Flask, jsonify, request
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ─── AWS Config ───────────────────────────────────────────────────────────────
AWS_REGION      = os.environ.get('AWS_REGION', 'eu-north-1')
S3_BUCKET_NAME  = os.environ.get('S3_BUCKET_NAME', '')
DYNAMODB_TABLE  = os.environ.get('DYNAMODB_TABLE', '')

# ─── AWS Clients ──────────────────────────────────────────────────────────────
s3_client       = boto3.client('s3', region_name=AWS_REGION)
dynamodb        = boto3.resource('dynamodb', region_name=AWS_REGION)


# ─────────────────────────────────────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/')
def hello():
    env_var = os.environ.get('MY_CUSTOM_VAR', 'Default Variable Value')
    html = f"""
    <h1>Hello from Python inside Docker v3! 🚀</h1>
    <p>This is a small application deployed via AWS ECS / EC2.</p>
    <p><strong>Environment Variable (MY_CUSTOM_VAR):</strong> {env_var}</p>
    <hr>
    <h2>Available Endpoints</h2>
    <ul>
      <li><a href="/health">GET /health</a> — Health check</li>
      <li><strong>S3</strong>
        <ul>
          <li><a href="/s3/list">GET /s3/list</a> — List objects in the configured S3 bucket</li>
          <li>PUT /s3/upload — Upload a file (JSON body: key, content)</li>
          <li>GET /s3/download/&lt;key&gt; — Download/read an object</li>
        </ul>
      </li>
      <li><strong>DynamoDB</strong>
        <ul>
          <li>POST /dynamodb/put — Put an item (JSON body)</li>
          <li>GET /dynamodb/get/&lt;pk&gt; — Get item by partition key <em>id</em></li>
          <li><a href="/dynamodb/scan">GET /dynamodb/scan</a> — Scan all items (first 20)</li>
        </ul>
      </li>
    </ul>
    """
    return html


# ─────────────────────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/health')
def health():
    return jsonify({"status": "ok", "region": AWS_REGION}), 200


# ─────────────────────────────────────────────────────────────────────────────
# S3 ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/s3/list', methods=['GET'])
def s3_list():
    """List all objects in the configured S3 bucket."""
    if not S3_BUCKET_NAME:
        return jsonify({"error": "S3_BUCKET_NAME environment variable is not set"}), 400
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
        objects = [
            {"key": obj["Key"], "size_bytes": obj["Size"], "last_modified": str(obj["LastModified"])}
            for obj in response.get("Contents", [])
        ]
        return jsonify({"bucket": S3_BUCKET_NAME, "count": len(objects), "objects": objects}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/s3/upload', methods=['PUT'])
def s3_upload():
    """
    Upload text content as an S3 object.
    Body (JSON): { "key": "path/in/bucket.txt", "content": "Hello World" }
    """
    if not S3_BUCKET_NAME:
        return jsonify({"error": "S3_BUCKET_NAME environment variable is not set"}), 400

    data = request.get_json(silent=True) or {}
    key     = data.get("key")
    content = data.get("content", "")

    if not key:
        return jsonify({"error": "Missing required field: 'key'"}), 400

    try:
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=key, Body=content.encode("utf-8"))
        return jsonify({"message": f"Object '{key}' uploaded successfully", "bucket": S3_BUCKET_NAME}), 201
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/s3/download/<path:key>', methods=['GET'])
def s3_download(key):
    """Read the content of an S3 object by key."""
    if not S3_BUCKET_NAME:
        return jsonify({"error": "S3_BUCKET_NAME environment variable is not set"}), 400
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        content  = response["Body"].read().decode("utf-8")
        return jsonify({"key": key, "content": content}), 200
    except ClientError as e:
        code = e.response["Error"]["Code"]
        status = 404 if code == "NoSuchKey" else 500
        return jsonify({"error": str(e)}), status


# ─────────────────────────────────────────────────────────────────────────────
# DYNAMODB ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/dynamodb/put', methods=['POST'])
def dynamodb_put():
    """
    Insert or overwrite an item in DynamoDB.
    Body (JSON): any dict that includes the table's partition key (default: 'id').
    Example: { "id": "user-1", "name": "Alice", "role": "admin" }
    """
    if not DYNAMODB_TABLE:
        return jsonify({"error": "DYNAMODB_TABLE environment variable is not set"}), 400

    item = request.get_json(silent=True)
    if not item:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.put_item(Item=item)
        return jsonify({"message": "Item stored successfully", "item": item}), 201
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/dynamodb/get/<string:pk>', methods=['GET'])
def dynamodb_get(pk):
    """Retrieve a single DynamoDB item by its partition key value (attribute: 'id')."""
    if not DYNAMODB_TABLE:
        return jsonify({"error": "DYNAMODB_TABLE environment variable is not set"}), 400
    try:
        table    = dynamodb.Table(DYNAMODB_TABLE)
        response = table.get_item(Key={"id": pk})
        item     = response.get("Item")
        if item is None:
            return jsonify({"error": f"Item with id='{pk}' not found"}), 404
        return jsonify({"item": item}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/dynamodb/scan', methods=['GET'])
def dynamodb_scan():
    """Scan and return up to 20 items from the DynamoDB table."""
    if not DYNAMODB_TABLE:
        return jsonify({"error": "DYNAMODB_TABLE environment variable is not set"}), 400
    try:
        table    = dynamodb.Table(DYNAMODB_TABLE)
        response = table.scan(Limit=20)
        return jsonify({"table": DYNAMODB_TABLE, "count": response.get("Count", 0), "items": response.get("Items", [])}), 200
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
