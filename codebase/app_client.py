import base64
import gc
import sqlite3
import requests

LAPTOP_SERVER_URL = "http://192.168.1.100:5000"  # Replace with Laptop IP
SQLITE_DB_PATH = "code_showcase.db"
CHUNK_LIMIT = 500

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
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        root_path TEXT NOT NULL,
        created_at TEXT
    );""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
        id INTEGER PRIMARY KEY,
        project_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        full_path TEXT NOT NULL UNIQUE,
        parent_path TEXT,
        node_type TEXT NOT NULL,
        extension TEXT,
        encrypted_content BLOB,
        created_at TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS change_log (
        id INTEGER PRIMARY KEY,
        node_id INTEGER NOT NULL,
        operation_type TEXT NOT NULL,
        created_at TEXT
    );""")
    conn.commit()
    conn.close()

def sync_projects():
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM projects")
    curr_p_id = cursor.fetchone()[0] or 0
    conn.close()

    while True:
        try:
            res = requests.post(f"{LAPTOP_SERVER_URL}/get_project_details", 
                                json={"last_project_id": curr_p_id, "limit": 500}, timeout=30)
            if res.status_code != 200: break
            projects = res.json().get('rows', [])
            if not projects: break

            conn = get_sqlite_conn()
            cursor = conn.cursor()
            for p in projects:
                cursor.execute("""
                    INSERT INTO projects (id, name, root_path, created_at) VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET name=excluded.name, root_path=excluded.root_path, created_at=excluded.created_at
                """, (p['id'], p['name'], p['root_path'], p['created_at']))
            conn.commit()
            conn.close()

            curr_p_id = max(p['id'] for p in projects)
            if len(projects) < 500: break
        except Exception as e:
            print(f"Project sync error: {e}")
            break

def process_node_rows(rows):
    if not rows: return
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

def process_change_log_rows(rows):
    if not rows: return
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

def run_app_sync():
    init_sqlite_db()
    sync_projects()

    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM nodes")
    curr_node = cursor.fetchone()[0] or 0
    cursor.execute("SELECT MAX(id) FROM change_log")
    curr_log = cursor.fetchone()[0] or 0
    conn.close()

    while True:
        res = requests.post(f"{LAPTOP_SERVER_URL}/get_node_details", json={"last_node_id": curr_node, "limit": CHUNK_LIMIT, "max_payload_mb": 8}, timeout=60)
        if res.status_code != 200: break
        rows = res.json().get('rows', [])
        if not rows: break
        process_node_rows(rows)
        curr_node = max(r['id'] for r in rows)
        gc.collect()

    while True:
        res = requests.post(f"{LAPTOP_SERVER_URL}/get_change_log_details", json={"last_change_log_id": curr_log, "limit": CHUNK_LIMIT, "max_payload_mb": 8}, timeout=60)
        if res.status_code != 200: break
        rows = res.json().get('rows', [])
        if not rows: break
        process_change_log_rows(rows)
        curr_log = max(r['change_log']['id'] for r in rows if 'change_log' in r)
        gc.collect()

    print("App Sync Complete!")
