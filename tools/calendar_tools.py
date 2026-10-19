from langchain_core.tools import tool

from database import get_connection


@tool
def create_event(
    title: str,
    event_date: str,
    start_time: str,
    end_time: str = "",
    description: str = "",
) -> str:
    """
    Create a calendar event.

    event_date format: YYYY-MM-DD
    time format: HH:MM
    """

    with get_connection() as connection:
        event = connection.execute(
            """
            INSERT INTO events (
                title,
                event_date,
                start_time,
                end_time,
                description
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                title,
                event_date,
                start_time,
                end_time or None,
                description,
            ),
        ).fetchone()

        event_id = event["id"]

    return (
        f"Event created successfully.\n"
        f"Event ID: {event_id}\n"
        f"Title: {title}\n"
        f"Date: {event_date}\n"
        f"Time: {start_time}"
    )


@tool
def list_events(
    event_date: str = "",
) -> str:
    """
    List calendar events.

    If event_date is supplied,
    return events for that date.
    """

    with get_connection() as connection:

        if event_date:
            events = connection.execute(
                """
                SELECT *
                FROM events
                WHERE event_date = %s
                ORDER BY start_time
                """,
                (event_date,),
            ).fetchall()

        else:
            events = connection.execute(
                """
                SELECT *
                FROM events
                ORDER BY event_date, start_time
                """
            ).fetchall()

        if not events:
            return "No calendar events found."

        result = []

        for event in events:
            result.append(
                (
                    f"ID: {event['id']}\n"
                    f"Title: {event['title']}\n"
                    f"Date: {event['event_date']}\n"
                    f"Start: {event['start_time']}\n"
                    f"End: {event['end_time'] or 'None'}\n"
                    f"Description: "
                    f"{event['description'] or 'None'}"
                )
            )

    return "\n\n".join(result)


@tool
def delete_event(
    event_id: int,
) -> str:
    """
    Delete a calendar event.
    """

    with get_connection() as connection:
        result = connection.execute(
            """
            DELETE FROM events
            WHERE id = %s
            RETURNING id
            """,
            (event_id,),
        ).fetchone()

        if result is None:
            return f"Event {event_id} was not found."

    return f"Event {event_id} deleted successfully."