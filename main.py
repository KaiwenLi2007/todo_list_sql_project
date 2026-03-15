"""
Course Manager: CRUD for tasks with urgency engine.
Rich UI: Console, Table, Panel, Prompt. DB: course_manager.db (init_db).
"""
from init_db import get_connection, init_db
from urgency_engine import compute_urgency
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

console = Console()


def add_task():
    """Add task: prompt course, deadline, est_hours; run urgency engine; INSERT; notify."""
    console.print(Panel("[bold cyan]Add New Assignment[/bold cyan]", expand=False))
    course = Prompt.ask("Course Name")
    deadline = Prompt.ask("Deadline (YYYY-MM-DD)")
    try:
        hours = float(Prompt.ask("Expected Time (Hours)"))
    except ValueError:
        console.print("[bold red]Expected time must be a number.[/bold red]")
        return
    urgency_score = compute_urgency(deadline, hours)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO tasks (course_name, deadline, est_hours, urgency_score) VALUES (?, ?, ?, ?)",
            (course, deadline, hours, urgency_score),
        )
        conn.commit()
    console.print("[bold green]✔ Task saved successfully![/bold green]")
    console.print(f"Assigned urgency level: [bold]{urgency_score}[/bold]")


def display_tasks(sort_by="deadline"):
    """Display tasks in a Rich table. sort_by: 'deadline' or 'urgency'."""
    table = Table(title="Course To-Do List", header_style="bold magenta")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Course", min_width=20)
    table.add_column("Deadline", justify="center")
    table.add_column("Hours", justify="right")
    table.add_column("Urgency", justify="center")

    with get_connection() as conn:
        if sort_by == "urgency":
            cur = conn.execute("SELECT * FROM tasks ORDER BY urgency_score ASC")
        else:
            cur = conn.execute("SELECT * FROM tasks ORDER BY deadline ASC")
        rows = cur.fetchall()

    if not rows:
        console.print("[dim]No tasks yet.[/dim]")
        return

    for row in rows:
        urg_val = row["urgency_score"]
        if "HIGH" in urg_val:
            urg_display = "[bold red]🔥 HIGH[/bold red]"
        elif "MEDIUM" in urg_val:
            urg_display = "[bold yellow]⚠️ MEDIUM[/bold yellow]"
        else:
            urg_display = "[bold green]✅ LOW[/bold green]"
        table.add_row(str(row["id"]), row["course_name"], row["deadline"], f"{row['est_hours']}h", urg_display)
    console.print(table)


def update_task():
    """Show tasks, ask id and new hours; re-run urgency; UPDATE."""
    display_tasks()
    task_id = IntPrompt.ask("\nEnter ID to update")
    try:
        new_hours = float(Prompt.ask("Updated Estimated Hours"))
    except ValueError:
        console.print("[bold red]Hours must be a number.[/bold red]")
        return
    with get_connection() as conn:
        cur = conn.execute("SELECT deadline FROM tasks WHERE id = ?", (task_id,))
        res = cur.fetchone()
    if not res:
        console.print("[bold red]Task ID not found.[/bold red]")
        return
    deadline = res["deadline"]
    new_urgency = compute_urgency(deadline, new_hours)
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE tasks SET est_hours = ?, urgency_score = ? WHERE id = ?",
            (new_hours, new_urgency, task_id),
        )
        conn.commit()
    console.print("[bold blue]ℹ Task updated![/bold blue]")


def delete_task():
    """Show tasks, ask id; DELETE; confirm."""
    display_tasks()
    task_id = IntPrompt.ask("\nEnter ID to delete")
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        n = cur.rowcount
    if n == 0:
        console.print("[bold red]Task ID not found. Nothing removed.[/bold red]")
    else:
        console.print("[bold red]✘ Task deleted.[/bold red]")


def main():
    # START program — INIT Database
    init_db()

    user_choice = ""
    while user_choice != "Exit":
        console.print("\n[bold reverse white]  ACADEMIC PLANNER  [/bold reverse white]")
        console.print("1. [green]Add Task[/green]")
        console.print("2. [blue]View by Date[/blue]")
        console.print("3. [yellow]View by Urgency[/yellow]")
        console.print("4. [cyan]Update Hours[/cyan]")
        console.print("5. [red]Delete Task[/red]")
        console.print("6. Exit")

        choice = Prompt.ask("Action", choices=["1", "2", "3", "4", "5", "6"])

        if choice == "1":
            add_task()
        elif choice == "2":
            display_tasks(sort_by="deadline")
        elif choice == "3":
            display_tasks(sort_by="urgency")
        elif choice == "4":
            update_task()
        elif choice == "5":
            delete_task()
        elif choice == "6":
            user_choice = "Exit"
            console.print("Goodbye.")

    # END program


if __name__ == "__main__":
    main()
