import json
import os

CONFIG_FILE = "sync_config.json"

def load_sync_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "base_url": ""
        }

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_sync_config(base_url):
    with open(CONFIG_FILE, "w") as f:
        json.dump({
            "base_url": base_url.strip().rstrip("/")
        }, f, indent=4)



base_url = load_sync_config()["base_url"]

requests.post(
    f"{base_url}/get_all_sync",
    json=payload
)


requests.post(f"{base_url}/get_change_log_sync", ...)
requests.get(f"{base_url}/download/db1")
requests.get(f"{base_url}/download/db2")


@app.route('/setup/sync', methods=['GET', 'POST'])
def sync_page():

    config = load_sync_config()

    if request.method == "POST":

        action = request.form.get("action")

        if action == "save":

            base_url = request.form.get("base_url", "").strip().rstrip("/")

            save_sync_config(base_url)

            flash("✅ Server URL updated successfully.", "success")

            return redirect(url_for("sync_page"))

        elif action == "sync":

            try:
                sync_data()
                sync_change()

                flash("✅ Sync completed successfully!", "success")

            except Exception as e:

                flash(f"❌ Sync failed: {e}", "danger")

            return redirect(url_for("index"))

    return render_template(
        "sync.html",
        base_url=config["base_url"]
    )
