"""
Analytics database for call logging and revenue tracking.
SQLite for persistence, per-client call records.
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("analytics-db")

DB_PATH = Path("./data/analytics.db")


def init_db() -> None:
    """Initialize analytics database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Calls table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            phone_number TEXT,
            timestamp TEXT NOT NULL,
            duration REAL NOT NULL,
            transcript TEXT,
            profession TEXT,
            sentiment TEXT,
            success INTEGER DEFAULT 1,
            revenue_value REAL DEFAULT 0
        )
    """
    )

    # Clients table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            phone_numbers TEXT,
            profession TEXT,
            voice_id TEXT,
            dashboard_url TEXT,
            created_at TEXT,
            monthly_revenue REAL DEFAULT 0,
            total_calls INTEGER DEFAULT 0
        )
    """
    )

    conn.commit()
    conn.close()
    logger.info("Analytics DB initialized")


async def log_call_to_db(
    client_name: str,
    duration: float,
    transcript: str,
    profession: str,
    success: bool = True,
    phone_number: str = None,
    revenue_value: float = 0,
) -> None:
    """
    Log a call to the analytics database.

    Args:
        client_name: Client name
        duration: Call duration in seconds
        transcript: Full call transcript
        profession: Profession type
        success: Whether call was successful
        phone_number: Caller's phone number
        revenue_value: Estimated revenue from this call
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute(
            """
            INSERT INTO calls
            (client_name, phone_number, timestamp, duration, transcript, profession, success, revenue_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                client_name,
                phone_number,
                datetime.utcnow().isoformat(),
                duration,
                transcript,
                profession,
                int(success),
                revenue_value,
            ),
        )

        # Update client stats
        c.execute(
            """
            UPDATE clients
            SET total_calls = total_calls + 1,
                monthly_revenue = monthly_revenue + ?
            WHERE name = ?
        """,
            (revenue_value, client_name),
        )

        conn.commit()
        conn.close()

        logger.info(f"Call logged for {client_name}: {duration:.1f}s")

    except Exception as e:
        logger.error(f"Error logging call: {e}")


def get_client_stats(client_name: str) -> Dict[str, Any]:
    """
    Get stats for a specific client.

    Args:
        client_name: Client name

    Returns:
        Dict with call count, revenue, etc.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute(
            """
            SELECT
                total_calls,
                monthly_revenue,
                AVG(duration) as avg_duration
            FROM clients
            WHERE name = ?
        """,
            (client_name,),
        )

        row = c.fetchone()
        conn.close()

        if row:
            return {
                "total_calls": row[0],
                "monthly_revenue": row[1],
                "avg_duration": row[2],
            }
        return {"total_calls": 0, "monthly_revenue": 0, "avg_duration": 0}

    except Exception as e:
        logger.error(f"Error getting client stats: {e}")
        return {}


def get_recent_calls(client_name: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get recent calls for a client.

    Args:
        client_name: Client name
        limit: Max number of calls to return

    Returns:
        List of call records
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute(
            """
            SELECT
                timestamp, duration, transcript, profession, success, revenue_value
            FROM calls
            WHERE client_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (client_name, limit),
        )

        rows = c.fetchall()
        conn.close()

        return [
            {
                "timestamp": row[0],
                "duration": row[1],
                "transcript": row[2],
                "profession": row[3],
                "success": bool(row[4]),
                "revenue_value": row[5],
            }
            for row in rows
        ]

    except Exception as e:
        logger.error(f"Error getting recent calls: {e}")
        return []


# Initialize on import
init_db()
