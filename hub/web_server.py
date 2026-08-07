import base64
import gc
import requests
import mysql.connector

# Target PythonAnywhere Website URL
PYTHONANYWHERE_URL = "https://userdba.pythonanywhere.com"

# --- GLOBAL CONSTANTS ---
MAX_SINGLE_BLOB_BYTES = 20 * 1024 * 1024  # 20 MB Cutoff
MAX_PAYLOAD_BYTES = 8 * 1024 * 1024      # 8 MB Batch Limit
INSERT_LIMIT = 500

# 1x1 Pure White PNG Placeholder Bytes
WHITE_SCREEN_BYTES = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x00\x05\xfe\x02\xfe\xa7\x35\x81\x84\x00\x00\x00\x00IEND\xaeB`\x82'

# --- Laptop MySQL DB Configurations ---
dbs = {
    'db1': {'host': 'localhost', 'user': 'root', 'password': 'your_mysql_password', 'database': 'db1_default'},
    'db2': {'host': 'localhost', 'user': 'root', 'password': 'your_mysql_password', 'database': 'db2_default'},
    'db3': {'host': 'localhost', 'user': 'root', 'password': 'your_mysql_password', 'database': 'db3_default'},
    'db4': {'host': 'localhost', 'user': 'root', 'password': 'your_mysql_password', 'database': 'db4_default'},
    'db5': {'host': 'localhost', 'user': 'root', 'password': 'your_mysql_password', 'database': 'db5_default'},
    'db6': {'host': 'localhost', 'user': 'root', 'password': 'your_mysql_password', 'database': 'db6_default'}
}

primary_keys = {
    'anime': 'anime_id', 'episodes': 'id', 'arcs_seasons_sagas': 'no', 'movies': 'id',
    'specials_ovas': 'id', 'characters': 'id', 'character_images': 'id', 'genres': 'genre_id',
    'anime_genres': 'id', 'thumbnails': 'id', 'arc_season_saga_images': 'id', 'change_log': 'id'
}

tables_by_db = {
    'db1': ['anime', 'episodes', 'arcs_seasons_sagas', 'movies', 'specials_ovas', 'characters',
            'character_images', 'genres', 'anime_genres', 'thumbnails', 'arc_season_saga_images', 'change_log'],
    'db2': ['arc_season_saga_images'], 'db3': ['arc_season_saga_images'],
    'db4': ['arc_season_saga_images'], 'db5': ['arc_season_saga_images'], 'db6': ['arc_season_saga_images']
}


def push_anime_to_website():
    # 1. Fetch website status (current max IDs on PythonAnywhere)
    try:
        res = requests.post(f"{PYTHONANYWHERE_URL}/api/website/get_status", timeout=30)
        if res.status_code != 200:
            print(f"Failed to reach website: {res.text}")
            return False

        status = res.json()
        web_last_ids = status.get('last_ids', {})
        web_last_change_log_id = status.get('last_change_log_id', 0)
    except Exception as e:
        print(f"Error connecting to PythonAnywhere: {e}")
        return False

    # 2. Push inserted/new data in 8 MB chunks
    while True:
        payload_data = []
        current_bytes = 0
        limit_reached = False

        for db_key, config in dbs.items():
            if limit_reached:
                break
            try:
                conn = mysql.connector.connect(**config)
                cursor = conn.cursor(dictionary=True)

                for table in tables_by_db.get(db_key, []):
                    if limit_reached:
                        break
                    if table in ('user', 'change_log'):
                        continue

                    pk = primary_keys[table]
                    key = f"{db_key}:{table}"
                    client_last_id = int(web_last_ids.get(key, 0))

                    cursor.execute(
                        f"SELECT * FROM {table} WHERE {pk} > %s ORDER BY {pk} ASC LIMIT %s",
                        (client_last_id, INSERT_LIMIT)
                    )
                    rows = cursor.fetchall()

                    for row in rows:
                        clean_row = {}
                        row_bytes = 0

                        for k, v in row.items():
                            if isinstance(v, bytes):
                                # STAGE 1: Replace blobs >20MB with white screen
                                if len(v) > MAX_SINGLE_BLOB_BYTES:
                                    print(f"[⚠️ WARNING] Image >20MB in {table}. Replaced with white screen.")
                                    v = WHITE_SCREEN_BYTES

                                encoded_str = "__base64__" + base64.b64encode(v).decode('utf-8')
                                clean_row[k] = encoded_str
                                row_bytes += len(encoded_str)
                            else:
                                clean_row[k] = v
                                row_bytes += len(str(v)) if v is not None else 0

                        clean_row['table'] = table
                        clean_row['source_db'] = db_key

                        # STAGE 2: If adding this row exceeds 8MB and we already have data, flush first!
                        if current_bytes + row_bytes > MAX_PAYLOAD_BYTES and len(payload_data) > 0:
                            limit_reached = True
                            break

                        payload_data.append(clean_row)
                        current_bytes += row_bytes

                        # Update in-memory tracking ID
                        row_id = row.get(pk)
                        if row_id is not None and row_id > client_last_id:
                            web_last_ids[key] = row_id

                        # Send large row isolated
                        if current_bytes >= MAX_PAYLOAD_BYTES:
                            limit_reached = True
                            break

                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error querying {db_key}: {e}")

        if not payload_data:
            print("No new table rows to push.")
            break

        # Push batch to PythonAnywhere
        push_res = requests.post(
            f"{PYTHONANYWHERE_URL}/api/website/push_data",
            json={"data": payload_data},
            timeout=60
        )
        if push_res.status_code != 200:
            print(f"Push data failed: {push_res.text}")
            break

        gc.collect()

    # 3. Push Change Logs (Anime Pattern - auto-embedding updated rows)
    curr_log_id = web_last_change_log_id
    while True:
        log_payload = []
        current_bytes = 0
        limit_reached = False

        try:
            conn = mysql.connector.connect(**dbs['db1'])
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM change_log WHERE id > %s ORDER BY id ASC LIMIT %s",
                (curr_log_id, INSERT_LIMIT)
            )
            entries = cursor.fetchall()

            for entry in entries:
                if limit_reached:
                    break

                log_bytes = len(str(entry))
                if current_bytes + log_bytes > MAX_PAYLOAD_BYTES and len(log_payload) > 0:
                    limit_reached = True
                    break

                log_payload.append({'change_log': entry})
                current_bytes += log_bytes
                curr_log_id = max(curr_log_id, entry['id'])

                op_type = entry.get('operation_type')
                table = entry.get('table_name')
                record_id = entry.get('record_id')
                stored_in_db = entry.get('stored_in_db')

                if not all([op_type, table, record_id, stored_in_db]):
                    continue
                if str(op_type).lower() != 'updated':
                    continue
                if table not in primary_keys or stored_in_db not in dbs:
                    continue

                pk = 'imgid' if table == 'arc_season_saga_images' else primary_keys[table]

                # Fetch updated record from correct DB
                try:
                    inner_conn = mysql.connector.connect(**dbs[stored_in_db])
                    inner_cursor = inner_conn.cursor(dictionary=True)
                    inner_cursor.execute(f"SELECT * FROM {table} WHERE {pk} = %s", (record_id,))
                    row = inner_cursor.fetchone()

                    if row:
                        clean_row = {}
                        row_bytes = 0
                        for k, v in row.items():
                            if isinstance(v, bytes):
                                # STAGE 1: Replace blobs >20MB with white screen
                                if len(v) > MAX_SINGLE_BLOB_BYTES:
                                    v = WHITE_SCREEN_BYTES

                                encoded_str = "__base64__" + base64.b64encode(v).decode('utf-8')
                                clean_row[k] = encoded_str
                                row_bytes += len(encoded_str)
                            else:
                                clean_row[k] = v
                                row_bytes += len(str(v)) if v is not None else 0

                        clean_row['table'] = table
                        clean_row['source_db'] = stored_in_db

                        # STAGE 2: Pre-overflow check
                        if current_bytes + row_bytes > MAX_PAYLOAD_BYTES and len(log_payload) > 1:
                            limit_reached = True
                            inner_cursor.close()
                            inner_conn.close()
                            break

                        log_payload.append(clean_row)
                        current_bytes += row_bytes

                        if current_bytes >= MAX_PAYLOAD_BYTES:
                            limit_reached = True

                    inner_cursor.close()
                    inner_conn.close()
                except Exception as inner_e:
                    print(f"Error fetching inner updated row: {inner_e}")

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching change_log from db1: {e}")
            break

        if not log_payload:
            print("No new change log entries to push.")
            break

        # Push change logs to PythonAnywhere
        log_res = requests.post(
            f"{PYTHONANYWHERE_URL}/api/website/push_change_log",
            json={"data": log_payload},
            timeout=60
        )
        if log_res.status_code != 200:
            print(f"Push change log failed: {log_res.text}")
            break

        gc.collect()

    print("✅ Anime Website Push Sync Complete!")
    return True


if __name__ == '__main__':
    push_anime_to_website()
