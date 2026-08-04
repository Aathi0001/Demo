CREATE TABLE change_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_id INT NOT NULL,
    operation_type ENUM('delete','replace') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


# =======================
# REPLACE FILE
# =======================
@app.route("/replace_file", methods=["POST"])
def replace_file():
    path = request.form["path"]
    password = request.form["action_password"]
    file = request.files["file"]

    if not verify_action_password(password):
        return "Invalid action password", 403

    encrypted = cipher.encrypt(file.read())

    conn = get_db()
    cur = conn.cursor()

    try:
        # Update file content
        cur.execute("""
            UPDATE nodes
            SET encrypted_content = %s
            WHERE full_path = %s
              AND node_type = 'file'
        """, (encrypted, path))

        # Add change log
        cur.execute("""
            INSERT INTO change_log (node_id, operation_type)
            SELECT id, 'replace'
            FROM nodes
            WHERE full_path = %s
              AND node_type = 'file'
        """, (path,))

        conn.commit()

    except Exception as e:
        conn.rollback()
        conn.close()
        return f"Error: {str(e)}", 500

    conn.close()
    return "File replaced"



# =======================
# DELETE NODE
# =======================
@app.route("/delete_node", methods=["POST"])
def delete_node():
    path = request.form["path"]
    password = request.form["action_password"]

    if not verify_action_password(password):
        return "Invalid action password", 403

    conn = get_db()
    cur = conn.cursor()

    try:
        # Get all nodes that will be deleted
        cur.execute("""
            SELECT id
            FROM nodes
            WHERE full_path = %s
               OR full_path LIKE CONCAT(%s, '/%%')
        """, (path, path))

        rows = cur.fetchall()

        # Add delete logs
        for row in rows:
            node_id = row[0]

            cur.execute("""
                INSERT INTO change_log (node_id, operation_type)
                VALUES (%s, 'delete')
            """, (node_id,))

        # Delete files/folders
        cur.execute("""
            DELETE FROM nodes
            WHERE full_path = %s
               OR full_path LIKE CONCAT(%s, '/%%')
        """, (path, path))

        conn.commit()

    except Exception as e:
        conn.rollback()
        conn.close()
        return f"Error: {str(e)}", 500

    conn.close()
    return "Deleted"


app.py
-------



from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# ============================
# MYSQL CONNECTION
# ============================

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",
        database="codeshowcase"
    )


# ============================
# GET LAST IDS
# ============================

@app.route("/get_last_ids", methods=["POST"])
def get_last_ids():

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Last Node ID
    cur.execute("SELECT COALESCE(MAX(id),0) AS id FROM nodes")
    last_node_id = cur.fetchone()["id"]

    # Last Change Log ID
    cur.execute("SELECT COALESCE(MAX(id),0) AS id FROM change_log")
    last_change_log_id = cur.fetchone()["id"]

    conn.close()

    return jsonify({
        "last_node_id": last_node_id,
        "last_change_log_id": last_change_log_id
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)







app.py 
-------
import base64




@app.route("/sync", methods=["POST"])
def sync():

    request_data = request.json

    last_node_id = int(request_data.get("last_node_id", 0))
    last_change_log_id = int(request_data.get("last_change_log_id", 0))
    limit = int(request_data.get("limit", 500))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    response = []

    # ====================================
    # STEP 1
    # Send newly inserted nodes
    # ====================================

    cur.execute("""
        SELECT *
        FROM nodes
        WHERE id > %s
        ORDER BY id
        LIMIT %s
    """, (last_node_id, limit))

    rows = cur.fetchall()

    for row in rows:

        clean = {}

        for k, v in row.items():

            if isinstance(v, bytes):
                clean[k] = "__base64__" + base64.b64encode(v).decode()
            else:
                clean[k] = v

        clean["table"] = "nodes"

        response.append(clean)

    # ====================================
    # STEP 2
    # Send change logs
    # ====================================

    cur.execute("""
        SELECT *
        FROM change_log
        WHERE id > %s
        ORDER BY id
        LIMIT %s
    """, (last_change_log_id, limit))

    logs = cur.fetchall()

    for log in logs:

        response.append({
            "change_log": log
        })

        operation = log["operation_type"]

        if operation != "replace":
            continue

        node_id = log["record_id"]

        cur.execute("""
            SELECT *
            FROM nodes
            WHERE id=%s
        """, (node_id,))

        row = cur.fetchone()

        if row:

            clean = {}

            for k, v in row.items():

                if isinstance(v, bytes):
                    clean[k] = "__base64__" + base64.b64encode(v).decode()
                else:
                    clean[k] = v

            clean["table"] = "nodes"

            response.append(clean)

    conn.close()

    return jsonify(response)








import sqlite3
import requests
import base64

SYNC_SERVER = "http://YOUR-LAPTOP-IP:5000"
DATABASE = "codeshowcase.db"

def get_sync_db():
    return sqlite3.connect(DATABASE)

def get_last_ids():

    conn = get_sync_db()
    cur = conn.cursor()

    cur.execute("SELECT COALESCE(MAX(id),0) FROM nodes")
    last_node_id = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(MAX(id),0) FROM change_log")
    last_change_log_id = cur.fetchone()[0]

    conn.close()

    return {
        "last_node_id": last_node_id,
        "last_change_log_id": last_change_log_id
    }

def sync_data():

    while True:

        local = get_last_ids()

        r = requests.post(
            f"{SYNC_SERVER}/sync",
            json={
                "last_node_id": local["last_node_id"],
                "last_change_log_id": local["last_change_log_id"],
                "limit":500
            },
            timeout=60
        )

        if r.status_code != 200:
            raise Exception("Laptop sync failed.")

        rows = r.json()

        if not rows:
            break

        apply_sync(rows)

        if len(rows) < 500:
            break





def apply_sync(data):

    conn = sqlite3.connect("codeshowcase.db")
    cursor = conn.cursor()

    max_change_log_id = 0

    for row in data:

        # -----------------------------
        # CHANGE LOG
        # -----------------------------
        if "change_log" in row:

            log = row["change_log"]

            max_change_log_id = max(max_change_log_id, log["id"])

            cursor.execute("""
                DELETE FROM change_log
                WHERE record_id=?
            """, (log["record_id"],))

            cursor.execute("""
                INSERT INTO change_log
                (
                    id,
                    record_id,
                    operation_type,
                    created_at
                )
                VALUES (?,?,?,?)
            """, (
                log["id"],
                log["record_id"],
                log["operation_type"],
                log["created_at"]
            ))

            if log["operation_type"] == "delete":

                cursor.execute("""
                    DELETE FROM nodes
                    WHERE id=?
                """, (log["record_id"],))

            continue

        # -----------------------------
        # NODE
        # -----------------------------
        table = row.pop("table")

        # decode blob
        if row.get("encrypted_content"):

            if isinstance(row["encrypted_content"], str):

                if row["encrypted_content"].startswith("__base64__"):

                    row["encrypted_content"] = base64.b64decode(
                        row["encrypted_content"][11:]
                    )

        columns = ",".join(row.keys())

        placeholders = ",".join(["?"] * len(row))

        updates = ",".join([
            f"{c}=excluded.{c}"
            for c in row.keys()
        ])

        cursor.execute(f"""
            INSERT INTO nodes
            ({columns})
            VALUES ({placeholders})

            ON CONFLICT(id)

            DO UPDATE SET
            {updates}
        """, list(row.values()))

    conn.commit()
    conn.close()

    return max_change_log_id


