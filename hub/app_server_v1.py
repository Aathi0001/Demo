import base64
import gc
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# --- DB Configurations ---
dbs = {
    'db1': {
        'host': 'localhost',
        'user': 'root',
        'password': 'your_mysql_password',
        'database': 'db1_default'
    },
    'db2': {
        'host': 'localhost',
        'user': 'root',
        'password': 'your_mysql_password',
        'database': 'db2_default'
    },
    'db3': {
        'host': 'localhost',
        'user': 'root',
        'password': 'your_mysql_password',
        'database': 'db3_default'
    },
    'db4': {
        'host': 'localhost',
        'user': 'root',
        'password': 'your_mysql_password',
        'database': 'db4_default'
    },
    'db5': {
        'host': 'localhost',
        'user': 'root',
        'password': 'your_mysql_password',
        'database': 'db5_default'
    },
    'db6': {
        'host': 'localhost',
        'user': 'root',
        'password': 'your_mysql_password',
        'database': 'db6_default'
    }
}

# --- Tables and Primary Keys ---
primary_keys = {
    'anime': 'anime_id',
    'episodes': 'id',
    'arcs_seasons_sagas': 'no',
    'movies': 'id',
    'specials_ovas': 'id',
    'characters': 'id',
    'character_images': 'id',
    'genres': 'genre_id',
    'anime_genres': 'id',
    'thumbnails': 'id',
    'arc_season_saga_images': 'id',
    'change_log': 'id'
}

tables_by_db = {
    'db1': ['anime', 'episodes', 'arcs_seasons_sagas', 'movies', 'specials_ovas', 'characters',
            'character_images', 'genres', 'anime_genres', 'thumbnails', 'arc_season_saga_images', 'change_log'],
    'db2': ['arc_season_saga_images'],
    'db3': ['arc_season_saga_images'],
    'db4': ['arc_season_saga_images'],
    'db5': ['arc_season_saga_images'],
    'db6': ['arc_season_saga_images']
}


@app.route('/get_all_sync', methods=['POST'])
def get_all_sync():
    """Fetches new inserted records across all DBs with an 8 MB RAM safeguard."""
    request_data = request.json or {}
    client_latest_ids = request_data.get('last_ids', {})
    insert_limit = request_data.get('insert_limit', 500)
    max_payload_bytes = request_data.get('max_payload_mb', 8) * 1024 * 1024

    response_data = []
    current_payload_bytes = 0
    payload_limit_reached = False

    for db_key, config in dbs.items():
        if payload_limit_reached:
            break

        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor(dictionary=True)

            for table in tables_by_db.get(db_key, []):
                if payload_limit_reached:
                    break
                if table in ('user', 'change_log'):
                    continue

                pk = primary_keys[table]
                key = f"{db_key}:{table}"
                client_last_id = int(client_latest_ids.get(key, 0))

                cursor.execute(
                    f"SELECT * FROM {table} WHERE {pk} > %s ORDER BY {pk} ASC LIMIT %s",
                    (client_last_id, insert_limit)
                )
                rows = cursor.fetchall()

                MAX_SINGLE_BLOB_BYTES = 20 * 1024 * 1024

                # 1x1 Pure White PNG Placeholder Bytes
                WHITE_SCREEN_BYTES = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x00\x05\xfe\x02\xfe\xa7\x35\x81\x84\x00\x00\x00\x00IEND\xaeB`\x82'

                for row in rows:
                    clean_row = {}
                    row_byte_size = 0

                    for k, v in row.items():
                        if isinstance(v, bytes):
                            if len(v) > MAX_SINGLE_BLOB_BYTES:
                                v = WHITE_SCREEN_BYTES

                            encoded_str = "__base64__" + base64.b64encode(v).decode('utf-8')
                            clean_row[k] = encoded_str
                            row_byte_size += len(encoded_str)
                        else:
                            clean_row[k] = v
                            row_byte_size += len(str(v)) if v is not None else 0

                    clean_row['table'] = table
                    clean_row['source_db'] = db_key

                    if current_payload_bytes + row_byte_size > max_payload_bytes and len(response_data) > 0:
                        payload_limit_reached = True
                        break

                    response_data.append(clean_row)
                    current_payload_bytes += row_byte_size

                    if current_payload_bytes >= max_payload_bytes:
                        payload_limit_reached = True
                        break

            cursor.close()
            conn.close()
        except Exception as e:
            response_data.append({'error': str(e), 'db': db_key})

    gc.collect()
    return jsonify(response_data)


@app.route('/get_change_log_sync', methods=['POST'])
def get_change_log_sync():
    """Fetches change_logs and automatically embeds updated rows in a single pass."""
    request_data = request.json or {}
    last_change_log_id = int(request_data.get('last_change_log_id', 0))
    change_log_limit = request_data.get('change_log_limit', 500)
    max_payload_bytes = request_data.get('max_payload_mb', 8) * 1024 * 1024

    response_data = []
    current_payload_bytes = 0

    try:
        config = dbs['db1']
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM change_log WHERE id > %s ORDER BY id ASC LIMIT %s",
            (last_change_log_id, change_log_limit)
        )
        change_log_entries = cursor.fetchall()

        for entry in change_log_entries:
            if current_payload_bytes >= max_payload_bytes:
                break

            response_data.append({'change_log': entry})
            current_payload_bytes += len(str(entry))

            operation_type = entry.get('operation_type')
            table = entry.get('table_name')
            record_id = entry.get('record_id')
            stored_in_db = entry.get('stored_in_db')

            if not all([operation_type, table, record_id, stored_in_db]):
                continue

            if str(operation_type).lower() != 'updated':
                continue

            if table not in primary_keys or stored_in_db not in dbs:
                continue

            pk = 'imgid' if table == 'arc_season_saga_images' else primary_keys[table]

            try:
                inner_conn = mysql.connector.connect(**dbs[stored_in_db])
                inner_cursor = inner_conn.cursor(dictionary=True)
                inner_cursor.execute(f"SELECT * FROM {table} WHERE {pk} = %s", (record_id,))
                row = inner_cursor.fetchone()
                
                MAX_SINGLE_BLOB_BYTES = 20 * 1024 * 1024

                # 1x1 Pure White PNG Placeholder Bytes
                WHITE_SCREEN_BYTES = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x00\x05\xfe\x02\xfe\xa7\x35\x81\x84\x00\x00\x00\x00IEND\xaeB`\x82'

                if row:
                    clean_row = {}
                    row_byte_size = 0
                    for k, v in row.items():
                        if isinstance(v, bytes):

                            if len(v) > MAX_SINGLE_BLOB_BYTES:
                                v = WHITE_SCREEN_BYTES

                            encoded_str = "__base64__" + base64.b64encode(v).decode('utf-8')
                            clean_row[k] = encoded_str
                            row_byte_size += len(encoded_str)
                        else:
                            clean_row[k] = v
                            row_byte_size += len(str(v)) if v is not None else 0

                    clean_row['table'] = table
                    clean_row['source_db'] = stored_in_db

                    if current_payload_bytes + row_byte_size > max_payload_bytes and len(response_data) > 0:
                        payload_limit_reached = True
                        break

                    response_data.append(clean_row)
                    current_payload_bytes += row_byte_size

                inner_cursor.close()
                inner_conn.close()
            except Exception as inner_e:
                response_data.append({'error': f"Inner fetch error: {inner_e}", 'db': stored_in_db})

        cursor.close()
        conn.close()
    except Exception as e:
        response_data.append({'error': str(e), 'db': 'db1'})

    gc.collect()
    return jsonify(response_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
