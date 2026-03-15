"""
Local web app for Course Manager. Run with: python3 app.py
Then open http://127.0.0.1:5000 in your browser.
"""
from pathlib import Path
from flask import Flask, send_file, request, jsonify
from init_db import get_connection, init_db
from urgency_engine import compute_urgency, get_buffer_hours
from date_parser import normalize_date

app = Flask(__name__, static_folder=None)
BASE = Path(__file__).parent


def row_to_dict(row):
    if not row:
        return None
    return {k: row[k] for k in row.keys()}


@app.route("/")
def index():
    return send_file(BASE / "index.html")


@app.route("/api/now")
def api_now():
    """Return server current date/time so UI can show what date urgency is based on."""
    from datetime import datetime
    return jsonify({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "datetime": datetime.now().isoformat(),
    })


@app.route("/api/parse-date")
def parse_date():
    """Return normalized YYYY-MM-DD for flexible date input (for UI hint/validation)."""
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"normalized": None})
    out = normalize_date(q)
    return jsonify({"normalized": out} if out else {"error": "Unrecognized date format"})


@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    sort = (request.args.get("sort") or "deadline").strip().lower()
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM tasks")
        rows = cur.fetchall()
    tasks = [row_to_dict(r) for r in rows]

    # Recompute urgency for each task (handles "March 17", "Mar 20" and 3-day + 6h rule)
    for t in tasks:
        dl = t.get("deadline") or ""
        eh = float(t.get("est_hours") or 0)
        t["urgency_score"] = compute_urgency(dl, eh)

    if sort == "urgency":
        # Order: HIGH first, then MEDIUM, then LOW (by urgency_score); within same level, tightest buffer first
        for t in tasks:
            t["_buffer_hours"] = get_buffer_hours(t.get("deadline") or "", float(t.get("est_hours") or 0))
        tasks.sort(key=lambda t: (t["urgency_score"], t["_buffer_hours"]))
        for t in tasks:
            t.pop("_buffer_hours", None)
    else:
        # By date: closest to today first (earliest deadline first); empty dates last
        for t in tasks:
            t["_sort_date"] = normalize_date(t.get("deadline") or "") or ""
        tasks.sort(key=lambda t: (0 if t["_sort_date"] else 1, t["_sort_date"]))
        for t in tasks:
            t.pop("_sort_date", None)

    from datetime import datetime
    return jsonify({
        "tasks": tasks,
        "server_date": datetime.now().strftime("%Y-%m-%d"),
    })


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json() or {}
    course_name = (data.get("course_name") or "").strip()
    deadline_raw = (data.get("deadline") or "").strip()
    deadline = normalize_date(deadline_raw)
    if not deadline:
        return jsonify({"error": "Invalid date. Use e.g. 2025-03-15, Mar 15, March 15, 03/15, or 3"}), 400
    try:
        est_hours = float(data.get("est_hours", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "est_hours must be a number"}), 400
    if not course_name:
        return jsonify({"error": "course_name is required"}), 400
    urgency_score = compute_urgency(deadline, est_hours)
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (course_name, deadline, est_hours, urgency_score) VALUES (?, ?, ?, ?)",
            (course_name, deadline, est_hours, urgency_score),
        )
        conn.commit()
        task_id = cur.lastrowid
    return jsonify({"id": task_id, "course_name": course_name, "deadline": deadline, "est_hours": est_hours, "urgency_score": urgency_score}), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json() or {}
    try:
        new_hours = float(data.get("est_hours", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "est_hours must be a number"}), 400
    with get_connection() as conn:
        cur = conn.execute("SELECT deadline FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
    if not row:
        return jsonify({"error": "Task not found"}), 404
    deadline = row["deadline"]
    urgency_score = compute_urgency(deadline, new_hours)
    with get_connection() as conn:
        conn.execute(
            "UPDATE tasks SET est_hours = ?, urgency_score = ? WHERE id = ?",
            (new_hours, urgency_score, task_id),
        )
        conn.commit()
    return jsonify({"id": task_id, "est_hours": new_hours, "urgency_score": urgency_score})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        n = cur.rowcount
    if n == 0:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    print("Open in browser: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
