from langchain_core.tools import tool
from database import get_connection


@tool
def create_task(
    title: str,
    description: str = "",
    due_date: str = "",
    priority: str = "medium",
) -> str:
    """
    Create a new personal task.

    Use this tool when the user wants to
    create or add a task.
    """

    title = title.strip()
    priority = priority.strip().lower()

    if not title:
        return "Task title cannot be empty."

    if priority not in {"low", "medium", "high"}:
        return "Priority must be low, medium, or high."

    with get_connection() as connection:
        task = connection.execute(
            """
            INSERT INTO tasks (
                title,
                description,
                due_date,
                priority
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                title,
                description,
                due_date or None,
                priority,
            ),
        ).fetchone()

    return (
        f"Task created successfully.\n"
        f"Task ID: {task['id']}\n"
        f"Title: {title}\n"
        f"Priority: {priority}\n"
        f"Due date: {due_date or 'Not specified'}"
    )


@tool
def list_tasks(
    status: str = "pending",
) -> str:
    """
    List user tasks.

    status can be:
    pending
    completed
    all
    """

    status = status.strip().lower()

    if status not in {"pending", "completed", "all"}:
        return "Status must be pending, completed, or all."

    with get_connection() as connection:
        if status == "all":
            tasks = connection.execute(
                """
                SELECT *
                FROM tasks
                ORDER BY id DESC
                """
            ).fetchall()
        else:
            tasks = connection.execute(
                """
                SELECT *
                FROM tasks
                WHERE status = %s
                ORDER BY id DESC
                """,
                (status,),
            ).fetchall()

    if not tasks:
        return "No tasks found."

    results = []

    for task in tasks:
        results.append(
            f"ID: {task['id']}\n"
            f"Title: {task['title']}\n"
            f"Priority: {task['priority']}\n"
            f"Due: {task['due_date'] or 'None'}\n"
            f"Status: {task['status']}"
        )

    return "\n\n".join(results)


@tool
def complete_task(
    task_id: int,
) -> str:
    """
    Mark a task as completed.
    """

    with get_connection() as connection:
        task = connection.execute(
            """
            UPDATE tasks
            SET status = 'completed'
            WHERE id = %s
            RETURNING id
            """,
            (task_id,),
        ).fetchone()

    if task is None:
        return f"Task {task_id} was not found."

    return f"Task {task_id} marked as completed."


@tool
def delete_task(
    task_id: int,
) -> str:
    """
    Delete a task.
    """

    with get_connection() as connection:
        task = connection.execute(
            """
            DELETE FROM tasks
            WHERE id = %s
            RETURNING id
            """,
            (task_id,),
        ).fetchone()

    if task is None:
        return f"Task {task_id} was not found."

    return f"Task {task_id} deleted successfully."