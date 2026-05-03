from __future__ import annotations

import sqlite3
from typing import Any

from app.config import settings


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_content TEXT NOT NULL,
                normalized_content TEXT NOT NULL,
                symbols TEXT NOT NULL,
                trace TEXT NOT NULL,
                final_state TEXT NOT NULL,
                label TEXT NOT NULL,
                matched_keywords TEXT,
                user_id TEXT,
                user_name TEXT,
                channel_id TEXT,
                channel_name TEXT,
                guild_id TEXT,
                guild_name TEXT,
                violation_points_added INTEGER NOT NULL DEFAULT 0,
                total_violation_points INTEGER NOT NULL DEFAULT 0,
                action_taken TEXT NOT NULL DEFAULT '',
                message_deleted INTEGER NOT NULL DEFAULT 0,
                user_kicked INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                user_name TEXT,
                violation_points INTEGER NOT NULL DEFAULT 0,
                violation_count INTEGER NOT NULL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()


def save_analysis_result(**payload: Any) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analysis_logs (
                raw_content,
                normalized_content,
                symbols,
                trace,
                final_state,
                label,
                matched_keywords,
                user_id,
                user_name,
                channel_id,
                channel_name,
                guild_id,
                guild_name,
                violation_points_added,
                total_violation_points,
                action_taken,
                message_deleted,
                user_kicked
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("raw_content", ""),
                payload.get("normalized_content", ""),
                payload.get("symbols", ""),
                payload.get("trace", ""),
                payload.get("final_state", ""),
                payload.get("label", ""),
                payload.get("matched_keywords", ""),
                payload.get("user_id", ""),
                payload.get("user_name", ""),
                payload.get("channel_id", ""),
                payload.get("channel_name", ""),
                payload.get("guild_id", ""),
                payload.get("guild_name", ""),
                int(payload.get("violation_points_added", 0)),
                int(payload.get("total_violation_points", 0)),
                payload.get("action_taken", ""),
                1 if payload.get("message_deleted", False) else 0,
                1 if payload.get("user_kicked", False) else 0,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def add_violation_points(user_id: str, user_name: str, points: int) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT violation_points, violation_count FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        if row is None:
            total_points = max(points, 0)
            violation_count = 1 if points > 0 else 0
            conn.execute(
                """
                INSERT INTO users (user_id, user_name, violation_points, violation_count)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, user_name, total_points, violation_count),
            )
        else:
            total_points = int(row["violation_points"]) + max(points, 0)
            violation_count = int(row["violation_count"]) + (1 if points > 0 else 0)
            conn.execute(
                """
                UPDATE users
                SET user_name = ?,
                    violation_points = ?,
                    violation_count = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                (user_name, total_points, violation_count, user_id),
            )

        conn.commit()
        return total_points


def get_violation_points(user_id: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT violation_points FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return int(row["violation_points"]) if row else 0


def fetch_recent_logs(limit: int = 50) -> list[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT
                id,
                raw_content,
                normalized_content,
                symbols,
                trace,
                final_state,
                label,
                matched_keywords,
                user_id,
                user_name,
                channel_id,
                channel_name,
                guild_id,
                guild_name,
                violation_points_added,
                total_violation_points,
                action_taken,
                message_deleted,
                user_kicked,
                created_at
            FROM analysis_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()


def fetch_top_users(limit: int = 10) -> list[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT user_id, user_name, violation_points, violation_count, updated_at
            FROM users
            ORDER BY violation_points DESC, updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()


def fetch_counts() -> dict[str, int]:
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) AS count FROM analysis_logs").fetchone()["count"]
        aman = conn.execute(
            "SELECT COUNT(*) AS count FROM analysis_logs WHERE label = 'Aman'"
        ).fetchone()["count"]
        waspada = conn.execute(
            "SELECT COUNT(*) AS count FROM analysis_logs WHERE label = 'Waspada'"
        ).fetchone()["count"]
        bullying = conn.execute(
            "SELECT COUNT(*) AS count FROM analysis_logs WHERE label = 'Indikasi Bullying'"
        ).fetchone()["count"]
        bullying_berat = conn.execute(
            "SELECT COUNT(*) AS count FROM analysis_logs WHERE label = 'Indikasi Bullying Berat'"
        ).fetchone()["count"]
        deleted = conn.execute(
            "SELECT COUNT(*) AS count FROM analysis_logs WHERE message_deleted = 1"
        ).fetchone()["count"]
        kicked = conn.execute(
            "SELECT COUNT(*) AS count FROM analysis_logs WHERE user_kicked = 1"
        ).fetchone()["count"]

    return {
        "total": int(total),
        "aman": int(aman),
        "waspada": int(waspada),
        "bullying": int(bullying),
        "bullying_berat": int(bullying_berat),
        "deleted": int(deleted),
        "kicked": int(kicked),
    }