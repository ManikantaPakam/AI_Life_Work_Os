from langchain_core.tools import tool
from database import get_connection


@tool
def create_learning_plan(
    goal: str,
    duration_days: int,
    plan: str,
) -> str:
    """Save a learning plan with its goal and duration."""

    if not goal.strip():
        return "Learning goal cannot be empty."

    if duration_days <= 0:
        return "Duration must be greater than zero."

    if not plan.strip():
        return "Learning plan cannot be empty."

    with get_connection() as connection:
        result = connection.execute(
            """
            INSERT INTO learning_plans (
                goal,
                duration_days,
                plan
            )
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (goal, duration_days, plan),
        ).fetchone()

    return (
        "Learning plan saved successfully. "
        f"Plan ID: {result['id']}"
    )


@tool
def show_learning_plans() -> str:
    """Show all saved learning plans."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, goal, duration_days, progress
            FROM learning_plans
            ORDER BY id DESC
            """
        ).fetchall()

    if not rows:
        return "No learning plans found."

    return "\n".join(
        f"ID: {row['id']} | "
        f"Goal: {row['goal']} | "
        f"Duration: {row['duration_days']} days | "
        f"Progress: {row['progress']}"
        for row in rows
    )


@tool
def get_learning_plan(plan_id: int) -> str:
    """Get the complete details of a saved learning plan."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT goal, duration_days, plan, progress
            FROM learning_plans
            WHERE id = %s
            """,
            (plan_id,),
        ).fetchone()

    if row is None:
        return f"No learning plan found with ID {plan_id}."

    return (
        f"Goal: {row['goal']}\n"
        f"Duration: {row['duration_days']} days\n"
        f"Progress: {row['progress']}\n"
        f"Learning Plan:\n{row['plan']}"
    )


@tool
def update_learning_progress(
    plan_id: int,
    progress: str,
) -> str:
    """Update progress for a saved learning plan."""

    allowed_statuses = {
        "Not Started",
        "In Progress",
        "Completed",
    }

    progress = progress.strip()

    if progress not in allowed_statuses:
        return (
            "Invalid progress status. Use: "
            "Not Started, In Progress, or Completed."
        )

    with get_connection() as connection:
        result = connection.execute(
            """
            UPDATE learning_plans
            SET progress = %s
            WHERE id = %s
            RETURNING id
            """,
            (progress, plan_id),
        ).fetchone()

    if result is None:
        return f"No learning plan found with ID {plan_id}."

    return (
        f"Learning plan {plan_id} "
        f"updated to: {progress}"
    )