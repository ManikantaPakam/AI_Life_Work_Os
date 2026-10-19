from langchain_core.tools import tool
from database import get_connection


@tool
def create_travel_plan(
    destination: str,
    duration_days: int,
    budget: float,
    itinerary: str,
) -> str:
    """Save a travel plan in the database."""

    destination = destination.strip()

    if not destination:
        return "Destination cannot be empty."

    if duration_days <= 0:
        return "Duration must be greater than zero."

    if budget < 0:
        return "Budget cannot be negative."

    if not itinerary.strip():
        return "Itinerary cannot be empty."

    with get_connection() as connection:
        plan = connection.execute(
            """
            INSERT INTO travel_plans (
                destination,
                duration_days,
                budget,
                itinerary
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                destination,
                duration_days,
                budget,
                itinerary,
            ),
        ).fetchone()

    return (
        "Travel plan saved successfully. "
        f"Plan ID: {plan['id']}"
    )


@tool
def show_travel_plans() -> str:
    """Show all saved travel plans."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                destination,
                duration_days,
                budget,
                status
            FROM travel_plans
            ORDER BY id DESC
            """
        ).fetchall()

    if not rows:
        return "No travel plans found."

    results = []

    for row in rows:
        results.append(
            f"ID: {row['id']} | "
            f"Destination: {row['destination']} | "
            f"Duration: {row['duration_days']} days | "
            f"Budget: ₹{row['budget']:.2f} | "
            f"Status: {row['status']}"
        )

    return "\n".join(results)


@tool
def get_travel_plan(plan_id: int) -> str:
    """Get the complete details of a saved travel plan."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                destination,
                duration_days,
                budget,
                itinerary,
                status
            FROM travel_plans
            WHERE id = %s
            """,
            (plan_id,),
        ).fetchone()

    if row is None:
        return f"No travel plan found with ID {plan_id}."

    return (
        f"Destination: {row['destination']}\n"
        f"Duration: {row['duration_days']} days\n"
        f"Budget: ₹{row['budget']:.2f}\n"
        f"Status: {row['status']}\n"
        f"Itinerary:\n{row['itinerary']}"
    )


@tool
def update_travel_status(
    plan_id: int,
    status: str,
) -> str:
    """Update the status of a saved travel plan."""

    allowed_statuses = {
        "Planned",
        "In Progress",
        "Completed",
        "Cancelled",
    }

    status = status.strip()

    if status not in allowed_statuses:
        return (
            "Invalid status. Use Planned, In Progress, "
            "Completed, or Cancelled."
        )

    with get_connection() as connection:
        plan = connection.execute(
            """
            UPDATE travel_plans
            SET status = %s
            WHERE id = %s
            RETURNING id
            """,
            (status, plan_id),
        ).fetchone()

    if plan is None:
        return f"No travel plan found with ID {plan_id}."

    return f"Travel plan {plan_id} updated to {status}."