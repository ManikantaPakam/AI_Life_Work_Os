from langchain_core.tools import tool
from database import get_connection


@tool
def save_memory(category: str, content: str) -> str:
    """Save important user preferences, goals, or project information."""

    if not category.strip() or not content.strip():
        return "Category and content cannot be empty."

    with get_connection() as connection:
        memory = connection.execute(
            """
            INSERT INTO memories (category, content)
            VALUES (%s, %s)
            RETURNING id
            """,
            (category.strip().lower(), content.strip()),
        ).fetchone()

    return (
        f"Memory saved successfully. "
        f"Memory ID: {memory['id']}"
    )


@tool
def search_memories(query: str) -> str:
    """Search saved memories using keywords."""

    if not query.strip():
        return "Please provide a search query."

    search_term = f"%{query.strip()}%"

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, category, content
            FROM memories
            WHERE category ILIKE %s
               OR content ILIKE %s
            ORDER BY updated_at DESC
            LIMIT 10
            """,
            (search_term, search_term),
        ).fetchall()

    if not rows:
        return "No matching memories found."

    results = []

    for row in rows:
        results.append(
            f"ID: {row['id']}\n"
            f"Category: {row['category']}\n"
            f"Memory: {row['content']}"
        )

    return "\n\n".join(results)


@tool
def delete_memory(memory_id: int) -> str:
    """Delete a saved memory using its ID."""

    with get_connection() as connection:
        deleted_memory = connection.execute(
            """
            DELETE FROM memories
            WHERE id = %s
            RETURNING id
            """,
            (memory_id,),
        ).fetchone()

    if deleted_memory is None:
        return f"No memory found with ID {memory_id}."

    return f"Memory {memory_id} deleted successfully."