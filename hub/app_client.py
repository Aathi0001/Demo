import base64
import gc
import sqlite3
import requests
from flask import flash, redirect, render_template, request, url_for

# Local server endpoint (Laptop IP)
LAPTOP_SERVER_URL = "http://192.168.1.100:5000"

# Mapping to local SQLite files matching server DB keys
sqlite_paths = {
    'db1': 'db1.db',
    'db2': 'db2.db',
    'db3': 'db3.db',
    'db4': 'db4.db',
    'db5': 'db5.db',
    'db6': 'db6.db'
}

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


def get_last_change_log_id():
    try:
        conn = sqlite3.connect(sqlite_paths['db1'])
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM change_log")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else 0
    except Exception:
        return 0


def get_last_ids():
    last_ids = {}
    for db_key, db_path in sqlite_paths.items():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            for table, pk in primary_keys.items():
                if table == 'user':
                    continue
                try:
                    cursor.execute(f"SELECT MAX({pk}) FROM {table}")
                    max_id = cursor.fetchone()[0]
                    if max_id is not None:
                        last_ids[f"{db_key}:{table}"] = max_id
                except Exception:
                    continue
            conn.close()
        except Exception:
            continue
    return last_ids


def apply_sync(data):
    conns = {k: sqlite3.connect(v) for k, v in sqlite_paths.items()}
    cursors = {k: conn.cursor() for k, conn in conns.items()}
    max_synced_log_id = 0

    for row in data:
        if 'error' in row:
            continue

        if 'change_log' in row:
            log = row['change_log']
            max_synced_log_id = max(max_synced_log_id, log['id'])
            try:
                cursors['db1'].execute("""
                    DELETE FROM change_log
                    WHERE table_name = ? AND record_id = ? AND stored_in_db = ?
                """, (log['table_name'], log['record_id'], log['stored_in_db']))

                cursors['db1'].execute("""
                    INSERT INTO change_log (id, table_name, record_id, operation_type, stored_in_db)
                    VALUES (?, ?, ?, ?, ?)
                """, (log['id'], log['table_name'], log['record_id'], log['operation_type'], log['stored_in_db']))
            except Exception:
                pass

            if str(log.get('operation_type')).lower() == 'deleted':
                pk = 'imgid' if log['table_name'] == 'arc_season_saga_images' else primary_keys.get(log['table_name'], 'id')
                try:
                    cursors[log['stored_in_db']].execute(
                        f"DELETE FROM {log['table_name']} WHERE {pk} = ?",
                        (log['record_id'],))
                except Exception:
                    pass

            continue

        # Normal insert/update row
        table = row.pop('table', None)
        db_key = row.pop('source_db', None)

        if not table or not db_key or db_key not in cursors:
            continue

        cursor = cursors[db_key]
        conflict_key = 'imgid' if table == 'arc_season_saga_images' else primary_keys.get(table, 'id')

        # Decode base64 blobs
        for col in list(row.keys()):
            if isinstance(row[col], str) and row[col].startswith("__base64__"):
                try:
                    row[col] = base64.b64decode(row[col][len("__base64__"):])
                except Exception:
                    row[col] = None

        try:
            if table == 'arc_season_saga_images' and db_key in ['db2', 'db3', 'db4', 'db5', 'db6']:
                imgid = row.get('imgid')
                order_index = row.get('order_index')
                arc_id = row.get('arc_season_saga_id')
                image_data = row.get('image')
                id_val = row.get('id')

                cursor.execute("SELECT 1 FROM arc_season_saga_images WHERE imgid = ?", (imgid,))
                exists = cursor.fetchone()

                if exists:
                    cursor.execute("""
                        UPDATE arc_season_saga_images
                        SET image = ?, order_index = ?, arc_season_saga_id = ?
                        WHERE imgid = ?
                    """, (image_data, order_index, arc_id, imgid))
                else:
                    cursor.execute("""
                        INSERT INTO arc_season_saga_images (id, imgid, arc_season_saga_id, order_index, image)
                        VALUES (?, ?, ?, ?, ?)
                    """, (id_val, imgid, arc_id, order_index, image_data))
            else:
                columns = ', '.join(row.keys())
                placeholders = ', '.join(['?'] * len(row))
                update_clause = ', '.join([f"{col}=excluded.{col}" for col in row])
                values = list(row.values())

                cursor.execute(f"""
                    INSERT INTO {table} ({columns})
                    VALUES ({placeholders})
                    ON CONFLICT({conflict_key}) DO UPDATE SET {update_clause}
                """, values)

        except Exception:
            pass

    for k in conns:
        conns[k].commit()
        conns[k].close()

    gc.collect()
    return max_synced_log_id


def sync_data():
    while True:
        last_ids = get_last_ids()

        payload = {
            "last_ids": last_ids,
            "insert_limit": 500,
            "max_payload_mb": 8
        }

        try:
            r = requests.post(f"{LAPTOP_SERVER_URL}/get_all_sync", json=payload, timeout=60)
            if r.status_code == 200:
                data = r.json()

                if not data:
                    break

                valid_rows = [row for row in data if 'error' not in row]
                if len(valid_rows) == 0:
                    break

                apply_sync(data)

            else:
                break
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to local laptop server. Check Wi-Fi.")
        except Exception:
            break


def sync_change():
    last_change_log_id = get_last_change_log_id()

    while True:
        payload = {
            "last_change_log_id": last_change_log_id,
            "change_log_limit": 500,
            "max_payload_mb": 8
        }

        try:
            r = requests.post(f"{LAPTOP_SERVER_URL}/get_change_log_sync", json=payload, timeout=60)

            if r.status_code != 200:
                break

            data = r.json()
            if not data:
                break

            valid_rows = [row for row in data if 'error' not in row]
            if len(valid_rows) == 0:
                break

            applied_max_id = apply_sync(data)

            if applied_max_id <= last_change_log_id:
                break

            last_change_log_id = applied_max_id

        except Exception:
            break


def run_anime_app_sync():
    sync_data()
    sync_change()
