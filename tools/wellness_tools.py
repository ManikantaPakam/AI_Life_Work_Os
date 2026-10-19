from datetime import date, timedelta

from langchain_core.tools import tool
from database import get_connection


@tool
def log_wellness_activity(
    activity: str,
    duration_minutes: int = 0,
    notes: str = "",
    activity_date: str = "",
) -> str:
    """Save a user's wellness activity in the database."""

    activity = activity.strip()

    if not activity:
        return "Activity name cannot be empty."

    if duration_minutes < 0:
        return "Duration cannot be negative."

    if not activity_date:
        activity_date = date.today().isoformat()

    try:
        date.fromisoformat(activity_date)
    except ValueError:
        return "Invalid date. Use YYYY-MM-DD format."

    with get_connection() as connection:
        log = connection.execute(
            """
            INSERT INTO wellness_logs (
                activity,
                duration_minutes,
                notes,
                activity_date
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                activity,
                duration_minutes,
                notes,
                activity_date,
            ),
        ).fetchone()

    return (
        "Activity saved successfully. "
        f"Log ID: {log['id']}"
    )


@tool
def show_wellness_activities() -> str:
    """Show the user's recent wellness activities."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                activity,
                duration_minutes,
                notes,
                activity_date
            FROM wellness_logs
            ORDER BY activity_date DESC, id DESC
            LIMIT 50
            """
        ).fetchall()

    if not rows:
        return "No wellness activities found."

    return "\n".join(
        f"ID: {row['id']} | "
        f"Activity: {row['activity']} | "
        f"Duration: {row['duration_minutes']} minutes | "
        f"Date: {row['activity_date']} | "
        f"Notes: {row['notes'] or ''}"
        for row in rows
    )


@tool
def get_weekly_wellness_summary() -> str:
    """Summarize wellness activities from the last seven days."""

    today = date.today()
    start_date = today - timedelta(days=6)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                activity,
                COUNT(*) AS total_sessions,
                COALESCE(SUM(duration_minutes), 0)
                    AS total_minutes
            FROM wellness_logs
            WHERE activity_date >= %s
              AND activity_date <= %s
            GROUP BY activity
            ORDER BY total_minutes DESC
            """,
            (
                start_date.isoformat(),
                today.isoformat(),
            ),
        ).fetchall()

    if not rows:
        return (
            "No wellness activities recorded "
            "in the last seven days."
        )

    return "\n".join(
        f"Activity: {row['activity']} | "
        f"Sessions: {row['total_sessions']} | "
        f"Total duration: {row['total_minutes']} minutes"
        for row in rows
    )