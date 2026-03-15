To-Do List Planner — Task Manager

## What the app tracks and why

This app tracks **course assignments and deadlines** with **estimated hours** so you can see what’s due soon and how much work each task needs. It assigns an **urgency level** (HIGH / MEDIUM / LOW) from the time left until the deadline and the estimated hours, so you can focus on the most pressing items first.

---

## Database schema

**Database file:** `course_manager.db` (SQLite)

**Table: `tasks`**

| Column          | Type    | Description                                      |
|-----------------|---------|--------------------------------------------------|
| `id`            | INTEGER | Primary key, auto-incrementing                   |
| `course_name`   | TEXT    | Required. Name of the course or assignment.     |
| `deadline`      | TEXT    | Due date (flexible input, stored as YYYY-MM-DD).|
| `est_hours`     | REAL    | User-entered expected duration in hours.        |
| `urgency_score` | TEXT    | System-computed: `HIGH`, `MEDIUM`, or `LOW`. |

---

## How to run the app

### 1. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

Or install manually:

```bash
python3 -m pip install rich flask
```

### 2. Run the web app (recommended)

```bash
python3 app.py
```

Then open in your browser: **http://127.0.0.1:5000**

### 3. Run the CLI (terminal menu)

```bash
python3 main.py
```

Use the numbered menu (1–6) to add tasks, view by date or urgency, update hours, delete tasks, or exit.

---

## CRUD operations

| Operation | What it does | How the user does it |
|-----------|--------------|----------------------|
| **Create** | Adds a new assignment. You enter course name, deadline (e.g. `Mar 15`, `2025-03-15`), and expected hours. The app computes urgency and saves the task. | **Web:** Fill the “New assignment” form (course, deadline, hours) and click **Add task**. **CLI:** Choose 1 (Add Task), then enter course name, deadline, and hours when prompted. |
| **Read**   | Lists all tasks. You can sort by **date** (closest to today first) or **urgency** (HIGH → MEDIUM → LOW). | **Web:** Use **By date** or **Urgency** above the table. **CLI:** Choose 2 (View by Date) or 3 (View by Urgency). |
| **Update** | Changes the estimated hours for a task. Urgency is recomputed from the same deadline and the new hours. | **Web:** Click **Edit hours** on a row, enter new hours, then **Save**. **CLI:** Choose 4 (Update Hours), enter the task ID and new hours when prompted. |
| **Delete** | Removes a task by ID. | **Web:** Click **Delete** on a row and confirm. **CLI:** Choose 5 (Delete Task), enter the task ID when prompted, then confirm. |

---

## Urgency rules (brief)

- **HIGH:** Due within 3 days and requires 6+ hours, or buffer &lt; 12 hours.
- **MEDIUM:** Buffer between 12 and 48 hours.
- **LOW:** Buffer 48+ hours.

*Buffer* = (hours until deadline) − estimated hours. Dates like “March 17”, “Mar 20”, and “2025-03-15” are all supported.
