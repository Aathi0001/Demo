import base64
import gc
import requests
import mysql.connector

PYTHONANYWHERE_URL = "https://your-username.pythonanywhere.com"
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',
    'database': 'userdbe$default',
    'charset': 'utf8mb4'
}
CHUNK_LIMIT = 500
MAX_PAYLOAD_BYTES = 8 * 1024 * 1024

def get_db_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

def push_website_sync():
    try:
        res = requests.post(f"{PYTHONANYWHERE_URL}/api/website/get_status", timeout=30)
        if res.status_code != 200: return False
        ids = res.json()
        curr_p_id, curr_n_id, curr_l_id = ids.get("last_project_id", 0), ids.get("last_node_id", 0), ids.get("last_change_log_id", 0)
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Projects
    while True:
        cursor.execute("SELECT id, name, root_path, created_at FROM projects WHERE id > %s ORDER BY id ASC LIMIT %s", (curr_p_id, CHUNK_LIMIT))
        p_rows = cursor.fetchall()
        if not p_rows: break
        for p in p_rows:
            if p.get('created_at'): p['created_at'] = str(p['created_at'])
        requests.post(f"{PYTHONANYWHERE_URL}/api/website/push_projects", json={"rows": p_rows}, timeout=30)
        curr_p_id = max(p['id'] for p in p_rows)
        if len(p_rows) < CHUNK_LIMIT: break

    # 2. Nodes
    while True:
        cursor.execute("SELECT id, project_id, name, full_path, parent_path, node_type, extension, encrypted_content, created_at FROM nodes WHERE id > %s ORDER BY id ASC LIMIT %s", (curr_n_id, CHUNK_LIMIT))
        n_rows = cursor.fetchall()
        if not n_rows: break
        formatted_nodes, bytes_count = [], 0
        for r in n_rows:
            r_dict = dict(r)
            if r_dict.get('created_at'): r_dict['created_at'] = str(r_dict['created_at'])
            content = r_dict.get('encrypted_content')
            if content is not None:
                if isinstance(content, str): content = content.encode('utf-8')
                encoded = base64.b64encode(content).decode('utf-8')
                r_dict['encrypted_content'] = encoded
                bytes_count += len(encoded)
            else:
                r_dict['encrypted_content'] = ""
            formatted_nodes.append(r_dict)
            if bytes_count >= MAX_PAYLOAD_BYTES: break

        requests.post(f"{PYTHONANYWHERE_URL}/api/website/push_nodes", json={"rows": formatted_nodes}, timeout=60)
        curr_n_id = max(r['id'] for r in formatted_nodes)
        gc.collect()
        if len(n_rows) < CHUNK_LIMIT and bytes_count < MAX_PAYLOAD_BYTES: break

    # 3. Change Logs (Anime Pattern - attach replaced nodes)
    while True:
        cursor.execute("SELECT id, node_id, operation_type, created_at FROM change_log WHERE id > %s ORDER BY id ASC LIMIT %s", (curr_l_id, CHUNK_LIMIT))
        l_rows = cursor.fetchall()
        if not l_rows: break
        
        payload_items = []
        for l in l_rows:
            entry = dict(l)
            if entry.get('created_at'): entry['created_at'] = str(entry['created_at'])
            payload_items.append({'change_log': entry})

            op_type = str(entry.get('operation_type')).upper()
            if op_type in ('REPLACE', 'UPDATE', 'UPDATED') and entry.get('node_id'):
                cursor.execute("SELECT id, project_id, name, full_path, parent_path, node_type, extension, encrypted_content, created_at FROM nodes WHERE id = %s", (entry['node_id'],))
                node_row = cursor.fetchone()
                if node_row:
                    clean_row = dict(node_row)
                    if clean_row.get('created_at'): clean_row['created_at'] = str(clean_row['created_at'])
                    content = clean_row.get('encrypted_content')
                    if content is not None:
                        if isinstance(content, str): content = content.encode('utf-8')
                        clean_row['encrypted_content'] = base64.b64encode(content).decode('utf-8')
                    else:
                        clean_row['encrypted_content'] = ""
                    clean_row['table'] = 'nodes'
                    payload_items.append(clean_row)

        requests.post(f"{PYTHONANYWHERE_URL}/api/website/push_change_log", json={"rows": payload_items}, timeout=30)
        curr_l_id = max(l['id'] for l in l_rows)
        gc.collect()
        if len(l_rows) < CHUNK_LIMIT: break

    cursor.close()
    conn.close()
    print("Website Push Sync Complete!")
    return True
