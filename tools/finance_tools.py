from datetime import date
from decimal import Decimal

from langchain_core.tools import tool
from database import get_connection


@tool
def add_transaction(
    transaction_type: str,
    category: str,
    amount: float,
    notes: str = "",
    transaction_date: str = "",
) -> str:
    """Record an income or expense transaction."""

    transaction_type = transaction_type.strip().lower()
    category = category.strip()

    if transaction_type not in {"income", "expense"}:
        return "Transaction type must be income or expense."

    if not category:
        return "Category cannot be empty."

    if amount <= 0:
        return "Amount must be greater than zero."

    if not transaction_date:
        transaction_date = date.today().isoformat()

    try:
        date.fromisoformat(transaction_date)
    except ValueError:
        return "Invalid date. Use YYYY-MM-DD format."

    with get_connection() as connection:
        transaction = connection.execute(
            """
            INSERT INTO finance_transactions (
                transaction_type,
                category,
                amount,
                notes,
                transaction_date
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                transaction_type,
                category,
                amount,
                notes,
                transaction_date,
            ),
        ).fetchone()

    return (
        "Transaction saved successfully. "
        f"Transaction ID: {transaction['id']}"
    )


@tool
def show_transactions(
    month: str = "",
    transaction_type: str = "",
) -> str:
    """
    Show transactions for a month, optionally filtered by type.
    Month format: YYYY-MM.
    """

    if month:
        try:
            date.fromisoformat(f"{month}-01")
        except ValueError:
            return "Invalid month. Use YYYY-MM format."

    transaction_type = transaction_type.strip().lower()

    if transaction_type not in {"", "income", "expense"}:
        return "Type must be income, expense, or empty for all."

    query = """
        SELECT
            id,
            transaction_type,
            category,
            amount,
            notes,
            transaction_date
        FROM finance_transactions
        WHERE 1 = 1
    """

    params = []

    if month:
        query += " AND LEFT(transaction_date, 7) = %s"
        params.append(month)

    if transaction_type:
        query += " AND transaction_type = %s"
        params.append(transaction_type)

    query += " ORDER BY transaction_date DESC, id DESC"

    with get_connection() as connection:
        rows = connection.execute(
            query,
            params,
        ).fetchall()

    if not rows:
        return "No matching transactions found."

    results = []

    for row in rows:
        results.append(
            f"ID: {row['id']} | "
            f"Type: {row['transaction_type']} | "
            f"Category: {row['category']} | "
            f"Amount: ₹{row['amount']:.2f} | "
            f"Date: {row['transaction_date']} | "
            f"Notes: {row['notes'] or ''}"
        )

    return "\n".join(results)


@tool
def get_monthly_summary(month: str = "") -> str:
    """
    Calculate total income, expenses, and balance for a month.
    Month format: YYYY-MM.
    """

    if not month:
        month = date.today().strftime("%Y-%m")

    try:
        date.fromisoformat(f"{month}-01")
    except ValueError:
        return "Invalid month. Use YYYY-MM format."

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                transaction_type,
                COALESCE(SUM(amount), 0) AS total
            FROM finance_transactions
            WHERE LEFT(transaction_date, 7) = %s
            GROUP BY transaction_type
            """,
            (month,),
        ).fetchall()

    totals = {
        "income": Decimal("0.00"),
        "expense": Decimal("0.00"),
    }

    for row in rows:
        totals[row["transaction_type"]] = Decimal(
            str(row["total"])
        )

    balance = totals["income"] - totals["expense"]

    return (
        f"Month: {month}\n"
        f"Total Income: ₹{totals['income']:.2f}\n"
        f"Total Expenses: ₹{totals['expense']:.2f}\n"
        f"Remaining Balance: ₹{balance:.2f}"
    )


@tool
def set_monthly_budget(
    category: str,
    monthly_limit: float,
) -> str:
    """Create or update a monthly spending limit for a category."""

    category = category.strip()

    if not category:
        return "Category cannot be empty."

    if monthly_limit < 0:
        return "Budget cannot be negative."

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO finance_budgets (
                category,
                monthly_limit
            )
            VALUES (%s, %s)
            ON CONFLICT (category)
            DO UPDATE SET
                monthly_limit = EXCLUDED.monthly_limit
            """,
            (category, monthly_limit),
        )

    return (
        f"Monthly budget for {category} set to "
        f"₹{monthly_limit:.2f}."
    )


@tool
def check_monthly_budget(month: str = "") -> str:
    """
    Compare monthly category budgets with actual expenses.
    Month format: YYYY-MM.
    """

    if not month:
        month = date.today().strftime("%Y-%m")

    try:
        date.fromisoformat(f"{month}-01")
    except ValueError:
        return "Invalid month. Use YYYY-MM format."

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                b.category,
                b.monthly_limit,
                COALESCE(SUM(t.amount), 0) AS spent
            FROM finance_budgets AS b
            LEFT JOIN finance_transactions AS t
                ON LOWER(t.category) = LOWER(b.category)
                AND t.transaction_type = 'expense'
                AND LEFT(t.transaction_date, 7) = %s
            GROUP BY
                b.category,
                b.monthly_limit
            ORDER BY b.category
            """,
            (month,),
        ).fetchall()

    if not rows:
        return "No monthly budgets found. Create a budget first."

    results = []

    for row in rows:
        category = row["category"]
        budget = Decimal(str(row["monthly_limit"]))
        spent = Decimal(str(row["spent"]))
        remaining = budget - spent

        status = (
            "Within budget"
            if remaining >= 0
            else "Over budget"
        )

        results.append(
            f"Category: {category} | "
            f"Budget: ₹{budget:.2f} | "
            f"Spent: ₹{spent:.2f} | "
            f"Remaining: ₹{remaining:.2f} | "
            f"Status: {status}"
        )

    return "\n".join(results)