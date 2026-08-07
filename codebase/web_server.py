import base64
import sqlite3
import gc
from flask import Flask, request, jsonify

app = Flask(__name__)
SQLITE_DB_PATH = "code_showcase.db"

def get_sqlite_conn():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_sqlite_db():
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY, name TEXT NOT NULL, root_path TEXT NOT NULL, created_at TEXT
    );""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
        id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, name TEXT NOT NULL, full_path TEXT NOT NULL UNIQUE,
        parent_path TEXT, node_type TEXT NOT NULL, extension TEXT, encrypted_content BLOB, created_at TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS change_log (
        id INTEGER PRIMARY KEY, node_id INTEGER NOT NULL, operation_type TEXT NOT NULL, created_at TEXT
    );""")
    conn.commit()
    conn.close()

@app.route('/api/website/get_status', methods=['POST'])
def get_website_status():
    init_sqlite_db()
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM projects")
    p_id = cursor.fetchone()[0] or 0
    cursor.execute("SELECT MAX(id) FROM nodes")
    n_id = cursor.fetchone()[0] or 0
    cursor.execute("SELECT MAX(id) FROM change_log")
    l_id = cursor.fetchone()[0] or 0
    conn.close()

    return jsonify({"last_project_id": p_id, "last_node_id": n_id, "last_change_log_id": l_id}), 200

@app.route('/api/website/push_projects', methods=['POST'])
def push_projects():
    data = request.get_json() or {}
    rows = data.get('rows', [])
    if rows:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        for p in rows:
            cursor.execute("""
                INSERT INTO projects (id, name, root_path, created_at) VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name=excluded.name, root_path=excluded.root_path, created_at=excluded.created_at
            """, (p['id'], p['name'], p['root_path'], p['created_at']))
        conn.commit()
        conn.close()
    return jsonify({"status": "success"}), 200

@app.route('/api/website/push_nodes', methods=['POST'])
def push_nodes():
    data = request.get_json() or {}
    rows = data.get('rows', [])
    if rows:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        for row in rows:
            raw_b64 = row.get('encrypted_content', '')
            decoded = base64.b64decode(raw_b64) if raw_b64 else None
            cursor.execute("""
                INSERT INTO nodes (id, project_id, name, full_path, parent_path, node_type, extension, encrypted_content, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET project_id=excluded.project_id, name=excluded.name, full_path=excluded.full_path,
                parent_path=excluded.parent_path, node_type=excluded.node_type, extension=excluded.extension,
                encrypted_content=excluded.encrypted_content, created_at=excluded.created_at
            """, (row['id'], row['project_id'], row['name'], row['full_path'], row['parent_path'], row['node_type'], row['extension'], decoded, row['created_at']))
        conn.commit()
        conn.close()
    gc.collect()
    return jsonify({"status": "success"}), 200

@app.route('/api/website/push_change_log', methods=['POST'])
def push_change_log():
    data = request.get_json() or {}
    rows = data.get('rows', [])
    if rows:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        for item in rows:
            if 'change_log' in item:
                log = item['change_log']
                cursor.execute("""
                    INSERT INTO change_log (id, node_id, operation_type, created_at) VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET node_id=excluded.node_id, operation_type=excluded.operation_type, created_at=excluded.created_at
                """, (log['id'], log['node_id'], log['operation_type'], log['created_at']))

                if str(log['operation_type']).upper() == 'DELETE':
                    cursor.execute("DELETE FROM nodes WHERE id = ?", (log['node_id'],))

            elif item.get('table') == 'nodes' or 'encrypted_content' in item:
                raw_b64 = item.get('encrypted_content', '')
                decoded = base64.b64decode(raw_b64) if raw_b64 else None
                cursor.execute("""
                    INSERT INTO nodes (id, project_id, name, full_path, parent_path, node_type, extension, encrypted_content, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET project_id=excluded.project_id, name=excluded.name, full_path=excluded.full_path,
                    parent_path=excluded.parent_path, node_type=excluded.node_type, extension=excluded.extension,
                    encrypted_content=excluded.encrypted_content, created_at=excluded.created_at
                """, (item['id'], item['project_id'], item['name'], item['full_path'], item['parent_path'], item['node_type'], item['extension'], decoded, item['created_at']))
        conn.commit()
        conn.close()
    gc.collect()
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run()
