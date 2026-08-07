import base64
import gc
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Paths to PythonAnywhere SQLite files
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


def get_sqlite_conns():
    """Returns connections and cursors for all SQLite databases."""
    conns = {k: sqlite3.connect(v) for k, v in sqlite_paths.items()}
    cursors = {k: conn.cursor() for k, conn in conns.items()}
    return conns, cursors


@app.route('/api/website/get_status', methods=['POST'])
def get_website_status():
    """Returns current MAX IDs across all local SQLite tables so Laptop knows what to push."""
    status_data = {}
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
                        status_data[f"{db_key}:{table}"] = max_id
                except Exception:
                    continue
            conn.close()
        except Exception:
            continue

    # Also fetch max change_log ID
    last_change_log_id = 0
    try:
        conn = sqlite3.connect(sqlite_paths['db1'])
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM change_log")
        res = cursor.fetchone()
        if res and res[0]:
            last_change_log_id = res[0]
        conn.close()
    except Exception:
        pass

    return jsonify({
        "last_ids": status_data,
        "last_change_log_id": last_change_log_id
    }), 200


@app.route('/api/website/push_data', methods=['POST'])
def push_data():
    """Receives new/updated database records pushed from Laptop and writes to SQLite."""
    payload = request.get_json() or {}
    data = payload.get('data', [])

    if not data:
        return jsonify({"status": "empty"}), 200

    conns, cursors = get_sqlite_conns()

    for row in data:
        if 'error' in row:
            continue

        table = row.pop('table', None)
        db_key = row.pop('source_db', None)

        if not table or not db_key or db_key not in cursors:
            continue

        cursor = cursors[db_key]
        conflict_key = 'imgid' if table == 'arc_season_saga_images' else primary_keys.get(table, 'id')

        # Decode base64 blobs back to binary
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
    return jsonify({"status": "success"}), 200


@app.route('/api/website/push_change_log', methods=['POST'])
def push_change_log():
    """Receives change logs and attached updated rows pushed from Laptop."""
    payload = request.get_json() or {}
    data = payload.get('data', [])

    if not data:
        return jsonify({"status": "empty"}), 200

    conns, cursors = get_sqlite_conns()

    for row in data:
        if 'error' in row:
            continue

        if 'change_log' in row:
            log = row['change_log']
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

        # Process updated rows sent right alongside logs
        table = row.pop('table', None)
        db_key = row.pop('source_db', None)

        if not table or not db_key or db_key not in cursors:
            continue

        cursor = cursors[db_key]
        conflict_key = 'imgid' if table == 'arc_season_saga_images' else primary_keys.get(table, 'id')

        for col in list(row.keys()):
            if isinstance(row[col], str) and row[col].startswith("__base64__"):
                try:
                    row[col] = base64.b64decode(row[col][len("__base64__"):])
                except Exception:
                    row[col] = None

        try:
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
    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    app.run()
