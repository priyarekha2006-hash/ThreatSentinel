import json
import sqlite3

from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "threatsentinel.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_utc TEXT NOT NULL,
                user_goal TEXT NOT NULL,
                proposed_action TEXT NOT NULL,
                findings_json TEXT NOT NULL,
                assessment_json TEXT NOT NULL
            )
            """
        )

        connection.commit()


def save_audit(
    user_goal: str,
    proposed_action: str,
    findings: dict,
    assessment: dict,
) -> int:

    timestamp = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO audit_logs (
                timestamp_utc,
                user_goal,
                proposed_action,
                findings_json,
                assessment_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                user_goal,
                proposed_action,
                json.dumps(findings),
                json.dumps(assessment),
            ),
        )

        connection.commit()

        return cursor.lastrowid


def get_audit_history(limit: int = 100) -> list[dict]:
    limit = max(1, min(limit, 500))

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM audit_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    history = []

    for row in rows:
        history.append({
            "id": row["id"],
            "timestamp_utc": row["timestamp_utc"],
            "user_goal": row["user_goal"],
            "proposed_action": row["proposed_action"],
            "findings": json.loads(row["findings_json"]),
            "assessment": json.loads(row["assessment_json"]),
        })

    return history