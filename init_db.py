"""
Initialize course_manager.db and create the tasks table schema.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "course_manager.db"

# SQL for the tasks table:
# - id: auto-incrementing primary key
# - course_name: required text
# - deadline: ISO8601 text (YYYY-MM-DD)
# - est_hours: float for expected duration
# - urgency_score: text, populated by system logic
CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL,
    deadline TEXT,
    est_hours REAL,
    urgency_score TEXT
);
"""


def get_connection():
    """Connect to the SQLite database course_manager.db."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # optional: access columns by name
    return conn


def init_db():
    """Create the database file and tasks table if they don't exist."""
    with get_connection() as conn:
        conn.execute(CREATE_TASKS_TABLE)
        conn.commit()
    print(f"Database initialized: {DB_PATH}")
    print("Table 'tasks' is ready.")


if __name__ == "__main__":
    init_db()
