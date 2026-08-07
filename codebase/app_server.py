import base64
import gc
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# --- GLOBAL CONSTANTS ---
MAX_SINGLE_BLOB_BYTES = 20 * 1024 * 1024  # 20 MB Cutoff
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


@app.route('/get_project_details', methods=['POST'])
def get_project_details():
    data = request.get_json() or {}
    last_project_id = int(data.get('last_project_id', 0))
    limit = int(data.get('limit', 500))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, root_path, created_at FROM projects WHERE id > %s ORDER BY id ASC LIMIT %s", 
        (last_project_id, limit)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    for r in rows:
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])

    return jsonify({"rows": rows}), 200


@app.route('/get_node_details', methods=['POST'])
def get_node_details():
    data = request.get_json() or {}
    last_node_id = int(data.get('last_node_id', 0))
    limit = int(data.get('limit', 500))
    max_bytes = int(data.get('max_payload_mb', 8)) * 1024 * 1024

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, project_id, name, full_path, parent_path, node_type, extension, encrypted_content, created_at
        FROM nodes WHERE id > %s ORDER BY id ASC LIMIT %s
    """, (last_node_id, limit))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    formatted_rows = []
    current_bytes = 0

    for row in rows:
        r_dict = dict(row)
        if r_dict.get('created_at'):
            r_dict['created_at'] = str(r_dict['created_at'])

        content = r_dict.get('encrypted_content')
        if content is not None:
            if isinstance(content, str):
                content = content.encode('utf-8')

            # STAGE 1: Replace file content over 20 MB with placeholder bytes
            if len(content) > MAX_SINGLE_BLOB_BYTES:
                content = WHITE_SCREEN_BYTES

            encoded_str = base64.b64encode(content).decode('utf-8')
            r_dict['encrypted_content'] = encoded_str
            row_byte_size = len(encoded_str)
        else:
            r_dict['encrypted_content'] = ""
            row_byte_size = 0

        # STAGE 2: If adding this row exceeds 8 MB and we already have rows, stop and send existing batch first
        if current_bytes + row_byte_size > max_bytes and len(formatted_rows) > 0:
            break

        formatted_rows.append(r_dict)
        current_bytes += row_byte_size

        # If this single row brought us near/over limit, stop loop to send it isolated
        if current_bytes >= max_bytes:
            break

    gc.collect()
    return jsonify({"rows": formatted_rows}), 200


@app.route('/get_change_log_details', methods=['POST'])
def get_change_log_details():
    """Fetches change_logs AND auto-fetches updated node data safely."""
    data = request.get_json() or {}
    last_change_log_id = int(data.get('last_change_log_id', 0))
    limit = int(data.get('limit', 500))
    max_bytes = int(data.get('max_payload_mb', 8)) * 1024 * 1024

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, node_id, operation_type, created_at
        FROM change_log WHERE id > %s ORDER BY id ASC LIMIT %s
    """, (last_change_log_id, limit))
    entries = cursor.fetchall()

    response_data = []
    current_bytes = 0
    payload_limit_reached = False

    for entry in entries:
        if payload_limit_reached:
            break

        entry_dict = dict(entry)
        if entry_dict.get('created_at'):
            entry_dict['created_at'] = str(entry_dict['created_at'])
        
        log_item = {'change_log': entry_dict}
        log_bytes = len(str(entry_dict))

        # Check overflow before adding change log
        if current_bytes + log_bytes > max_bytes and len(response_data) > 0:
            break

        response_data.append(log_item)
        current_bytes += log_bytes

        op_type = str(entry_dict.get('operation_type')).upper()
        node_id = entry_dict.get('node_id')

        # Auto-fetch replaced node row immediately
        if op_type in ('REPLACE', 'UPDATE', 'UPDATED') and node_id:
            try:
                node_cursor = conn.cursor(dictionary=True)
                node_cursor.execute("""
                    SELECT id, project_id, name, full_path, parent_path, node_type, extension, encrypted_content, created_at
                    FROM nodes WHERE id = %s
                """, (node_id,))
                row = node_cursor.fetchone()
                node_cursor.close()

                if row:
                    clean_row = dict(row)
                    if clean_row.get('created_at'):
                        clean_row['created_at'] = str(clean_row['created_at'])

                    content = clean_row.get('encrypted_content')
                    if content is not None:
                        if isinstance(content, str):
                            content = content.encode('utf-8')

                        # STAGE 1: Replace file content over 20 MB
                        if len(content) > MAX_SINGLE_BLOB_BYTES:
                            content = WHITE_SCREEN_BYTES

                        encoded_str = base64.b64encode(content).decode('utf-8')
                        clean_row['encrypted_content'] = encoded_str
                        row_byte_size = len(encoded_str)
                    else:
                        clean_row['encrypted_content'] = ""
                        row_byte_size = 0

                    clean_row['table'] = 'nodes'

                    # STAGE 2: Pre-overflow check for attached node
                    if current_bytes + row_byte_size > max_bytes and len(response_data) > 1:
                        payload_limit_reached = True
                        break

                    response_data.append(clean_row)
                    current_bytes += row_byte_size

                    if current_bytes >= max_bytes:
                        payload_limit_reached = True
                        break

            except Exception as inner_e:
                response_data.append({'error': f"Node fetch error: {inner_e}"})

    cursor.close()
    conn.close()
    gc.collect()
    return jsonify({"rows": response_data}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
