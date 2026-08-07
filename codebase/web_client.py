import base64
import gc
import requests
import mysql.connector

# --- GLOBAL CONSTANTS ---
PYTHONANYWHERE_URL = "https://your-username.pythonanywhere.com"
MAX_SINGLE_BLOB_BYTES = 20 * 1024 * 1024  # 20 MB Cutoff
MAX_PAYLOAD_BYTES = 8 * 1024 * 1024       # 8 MB Batch Limit
CHUNK_LIMIT = 500

# 1x1 Pure White PNG Placeholder Bytes
WHITE_SCREEN_BYTES = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x00\x05\xfe\x02\xfe\xa7\x35\x81\x84\x00\x00\x00\x00IEND\xaeB`\x82'

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',
    'database': 'userdbe$default',
    'charset': 'utf8mb4'
}

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
        
        formatted_nodes = []
        bytes_count = 0
        limit_reached = False

        for r in n_rows:
            r_dict = dict(r)
            if r_dict.get('created_at'): r_dict['created_at'] = str(r_dict['created_at'])
            
            content = r_dict.get('encrypted_content')
            if content is not None:
                if isinstance(content, str): content = content.encode('utf-8')
                
                # STAGE 1: Guard against binary files over 20 MB
                if len(content) > MAX_SINGLE_BLOB_BYTES:
                    content = WHITE_SCREEN_BYTES

                encoded = base64.b64encode(content).decode('utf-8')
                r_dict['encrypted_content'] = encoded
                row_bytes = len(encoded)
            else:
                r_dict['encrypted_content'] = ""
                row_bytes = 0

            # STAGE 2: Pre-overflow batch control (stop before exceeding 8 MB)
            if bytes_count + row_bytes > MAX_PAYLOAD_BYTES and len(formatted_nodes) > 0:
                limit_reached = True
                break

            formatted_nodes.append(r_dict)
            bytes_count += row_bytes

            if bytes_count >= MAX_PAYLOAD_BYTES:
                limit_reached = True
                break

        if not formatted_nodes:
            break

        requests.post(f"{PYTHONANYWHERE_URL}/api/website/push_nodes", json={"rows": formatted_nodes}, timeout=60)
        curr_n_id = max(r['id'] for r in formatted_nodes)
        gc.collect()

        if len(n_rows) < CHUNK_LIMIT and not limit_reached: break

    # 3. Change Logs (Anime Pattern - attach replaced nodes)
    while True:
        cursor.execute("SELECT id, node_id, operation_type, created_at FROM change_log WHERE id > %s ORDER BY id ASC LIMIT %s", (curr_l_id, CHUNK_LIMIT))
        l_rows = cursor.fetchall()
        if not l_rows: break
        
        payload_items = []
        bytes_count = 0
        limit_reached = False

        for l in l_rows:
            if limit_reached: break

            entry = dict(l)
            if entry.get('created_at'): entry['created_at'] = str(entry['created_at'])
            log_bytes = len(str(entry))

            if bytes_count + log_bytes > MAX_PAYLOAD_BYTES and len(payload_items) > 0:
                limit_reached = True
                break

            payload_items.append({'change_log': entry})
            bytes_count += log_bytes
            curr_l_id = max(curr_l_id, entry['id'])

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
                        
                        # STAGE 1: Guard against binary files over 20 MB
                        if len(content) > MAX_SINGLE_BLOB_BYTES:
                            content = WHITE_SCREEN_BYTES

                        encoded_str = base64.b64encode(content).decode('utf-8')
                        clean_row['encrypted_content'] = encoded_str
                        row_bytes = len(encoded_str)
                    else:
                        clean_row['encrypted_content'] = ""
                        row_bytes = 0

                    clean_row['table'] = 'nodes'

                    # STAGE 2: Check overflow for attached node
                    if bytes_count + row_bytes > MAX_PAYLOAD_BYTES and len(payload_items) > 1:
                        limit_reached = True
                        break

                    payload_items.append(clean_row)
                    bytes_count += row_bytes

                    if bytes_count >= MAX_PAYLOAD_BYTES:
                        limit_reached = True

        if not payload_items:
            break

        requests.post(f"{PYTHONANYWHERE_URL}/api/website/push_change_log", json={"rows": payload_items}, timeout=30)
        gc.collect()

        if len(l_rows) < CHUNK_LIMIT and not limit_reached: break

    cursor.close()
    conn.close()
    print("Website Push Sync Complete!")
    return True

if __name__ == '__main__':
    push_website_sync()
