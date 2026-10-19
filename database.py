import psycopg
from psycopg.rows import dict_row
from config import DATABASE_URL


def get_connection():
    """Create and return a PostgreSQL connection."""
    connection = psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
    )
    return connection


def initialize_database():
    """Create application database tables."""

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                event_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS emails (
                id SERIAL PRIMARY KEY,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id SERIAL PRIMARY KEY,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_plans (
                id SERIAL PRIMARY KEY,
                goal TEXT NOT NULL,
                duration_days INTEGER NOT NULL,
                plan TEXT NOT NULL,
                progress TEXT DEFAULT 'Not Started',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS wellness_logs (
                id SERIAL PRIMARY KEY,
                activity TEXT NOT NULL,
                duration_minutes INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                activity_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS travel_plans (
                id SERIAL PRIMARY KEY,
                destination TEXT NOT NULL,
                duration_days INTEGER NOT NULL,
                budget NUMERIC(12, 2) NOT NULL,
                itinerary TEXT NOT NULL,
                status TEXT DEFAULT 'Planned',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS finance_transactions (
                id SERIAL PRIMARY KEY,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount NUMERIC(12, 2) NOT NULL,
                notes TEXT DEFAULT '',
                transaction_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS finance_budgets (
                id SERIAL PRIMARY KEY,
                category TEXT NOT NULL UNIQUE,
                monthly_limit NUMERIC(12, 2) NOT NULL
            )
            """
        )

    print("PostgreSQL database initialized successfully.")