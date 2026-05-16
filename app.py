from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import psycopg2
import psycopg2.extras
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

load_dotenv()   # loads .env when running locally (no-op in ECS where env vars are injected)

app = Flask(__name__)

# ── DB config (read from environment / .env) ───────────────────────────────
DB_HOST     = os.environ.get('DB_HOST', '')
DB_PORT     = int(os.environ.get('DB_PORT', 5432))
DB_NAME     = os.environ.get('DB_NAME', 'postgres')
DB_USER     = os.environ.get('DB_USER', '')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')


def get_db_conn():
    """Open a fresh PostgreSQL connection per request."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=5,
    )


# ── Root route ─────────────────────────────────────────────────────────────
@app.route('/')
def hello():
    env_var = os.environ.get('MY_CUSTOM_VAR', 'Default Variable Value')
    html = f"""
    <h1>Hello from Python inside Docker v3! 🚀</h1>
    <p>This is a small application deployed via AWS ECS / EC2.</p>
    <p><strong>Environment Variable (MY_CUSTOM_VAR):</strong> {env_var}</p>
    """
    return html


# ── RDS / Aurora routes ────────────────────────────────────────────────────

@app.route('/rds/init')
def rds_init():
    """Create the users table (idempotent — safe to call multiple times)."""
    missing = [v for v in ('DB_HOST', 'DB_USER', 'DB_PASSWORD') if not os.environ.get(v)]
    if missing:
        return jsonify({"error": f"Missing RDS env vars: {', '.join(missing)}"}), 500

    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         SERIAL PRIMARY KEY,
                name       VARCHAR(120)  NOT NULL,
                email      VARCHAR(254)  NOT NULL UNIQUE,
                created_at TIMESTAMPTZ   NOT NULL DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Table 'users' is ready"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/rds/users', methods=['POST'])
def rds_create_user():
    """Insert a user. Body: {"name": "...", "email": "..."}"""
    data = request.get_json(silent=True) or {}
    name  = data.get('name', '').strip()
    email = data.get('email', '').strip()

    if not name or not email:
        return jsonify({"error": "Both 'name' and 'email' are required"}), 400

    try:
        conn = get_db_conn()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) "
            "RETURNING id, name, email, created_at AS created;",
            (name, email),
        )
        user = dict(cur.fetchone())
        user['created'] = str(user['created'])
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "User created", "user": user}), 201
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": f"Email '{email}' already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/rds/users', methods=['GET'])
def rds_list_users():
    """Return all users."""
    try:
        conn = get_db_conn()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, email, created_at AS created FROM users ORDER BY id;")
        rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            r['created'] = str(r['created'])
        cur.close()
        conn.close()
        return jsonify({"users": rows, "count": len(rows)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/rds/users/<int:user_id>', methods=['GET'])
def rds_get_user(user_id):
    """Fetch a single user by ID."""
    try:
        conn = get_db_conn()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT id, name, email, created_at AS created FROM users WHERE id = %s;",
            (user_id,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row is None:
            return jsonify({"error": f"User id={user_id} not found"}), 404
        user = dict(row)
        user['created'] = str(user['created'])
        return jsonify({"user": user})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/rds/users/<int:user_id>', methods=['DELETE'])
def rds_delete_user(user_id):
    """Delete a user by ID."""
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if deleted is None:
            return jsonify({"error": f"User id={user_id} not found"}), 404
        return jsonify({"message": f"User id={user_id} deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── DynamoDB config ────────────────────────────────────────────────────────
AWS_REGION      = os.environ.get('AWS_REGION', 'eu-north-1')
DYNAMODB_TABLE  = os.environ.get('DYNAMODB_TABLE', 'ABCD')


def get_dynamo_table():
    """Return a boto3 DynamoDB Table resource."""
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    return dynamodb.Table(DYNAMODB_TABLE)


# ── DynamoDB routes ────────────────────────────────────────────────────────

@app.route('/dynamo/items', methods=['POST'])
def dynamo_create_item():
    """
    Create / overwrite an item.
    Body: { "partition": "<key>", ...extra fields... }
    'partition' maps to the DynamoDB partition key.
    """
    data = request.get_json(silent=True) or {}
    partition = data.get('partition', '').strip()
    if not partition:
        return jsonify({"error": "'partition' key is required"}), 400

    try:
        table = get_dynamo_table()
        table.put_item(Item=data)
        return jsonify({"message": "Item created/updated", "item": data}), 201
    except ClientError as e:
        return jsonify({"error": e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/dynamo/items', methods=['GET'])
def dynamo_list_items():
    """
    Scan and return ALL items in the table.
    Optional query param: ?limit=N (default 100).
    WARNING: scan reads the entire table — avoid on large datasets.
    """
    limit = min(int(request.args.get('limit', 100)), 1000)
    try:
        table = get_dynamo_table()
        resp  = table.scan(Limit=limit)
        items = resp.get('Items', [])
        return jsonify({"items": items, "count": len(items),
                        "scanned": resp.get('ScannedCount', len(items))})
    except ClientError as e:
        return jsonify({"error": e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/dynamo/items/<string:partition_key>', methods=['GET'])
def dynamo_get_item(partition_key):
    """
    Fetch a single item by its partition key value.
    GET /dynamo/items/<partition_key_value>
    """
    try:
        table = get_dynamo_table()
        resp  = table.get_item(Key={'partition': partition_key})
        item  = resp.get('Item')
        if item is None:
            return jsonify({"error": f"Item with partition='{partition_key}' not found"}), 404
        return jsonify({"item": item})
    except ClientError as e:
        return jsonify({"error": e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/dynamo/items/<string:partition_key>', methods=['PUT'])
def dynamo_update_item(partition_key):
    """
    Update specific attributes of an existing item.
    Body: { "<attr>": "<value>", ... }  — do NOT include 'partition' in body.
    PUT /dynamo/items/<partition_key_value>
    """
    data = request.get_json(silent=True) or {}
    # Remove key from update payload to avoid overwriting the key itself
    data.pop('partition', None)

    if not data:
        return jsonify({"error": "No attributes to update provided"}), 400

    # Build UpdateExpression dynamically
    expr_names  = {}
    expr_values = {}
    set_parts   = []
    for i, (attr, val) in enumerate(data.items()):
        name_ph  = f'#a{i}'
        value_ph = f':v{i}'
        expr_names[name_ph]  = attr
        expr_values[value_ph] = val
        set_parts.append(f'{name_ph} = {value_ph}')

    update_expr = 'SET ' + ', '.join(set_parts)

    try:
        table = get_dynamo_table()
        resp  = table.update_item(
            Key={'partition': partition_key},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ConditionExpression='attribute_exists(#pk)',
            ExpressionAttributeNames={**expr_names, '#pk': 'partition'},
            ReturnValues='ALL_NEW',
        )
        return jsonify({"message": "Item updated", "item": resp.get('Attributes', {})})
    except ClientError as e:
        code = e.response['Error']['Code']
        if code == 'ConditionalCheckFailedException':
            return jsonify({"error": f"Item with partition='{partition_key}' not found"}), 404
        return jsonify({"error": e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/dynamo/items/<string:partition_key>', methods=['DELETE'])
def dynamo_delete_item(partition_key):
    """
    Delete an item by partition key.
    DELETE /dynamo/items/<partition_key_value>
    """
    try:
        table = get_dynamo_table()
        resp  = table.delete_item(
            Key={'partition': partition_key},
            ConditionExpression='attribute_exists(partition)',
            ReturnValues='ALL_OLD',
        )
        old = resp.get('Attributes')
        if not old:
            return jsonify({"error": f"Item with partition='{partition_key}' not found"}), 404
        return jsonify({"message": f"Item '{partition_key}' deleted", "deleted_item": old})
    except ClientError as e:
        code = e.response['Error']['Code']
        if code == 'ConditionalCheckFailedException':
            return jsonify({"error": f"Item with partition='{partition_key}' not found"}), 404
        return jsonify({"error": e.response['Error']['Message']}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
