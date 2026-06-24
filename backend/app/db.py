from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "app.db"


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                overall_score REAL NOT NULL DEFAULT 6.0,
                target_score REAL NOT NULL DEFAULT 7.0,
                exam_date TEXT NOT NULL DEFAULT '2026-06-25',
                skill_listening REAL NOT NULL DEFAULT 6.0,
                skill_reading REAL NOT NULL DEFAULT 6.0,
                skill_speaking REAL NOT NULL DEFAULT 6.0,
                skill_writing REAL NOT NULL DEFAULT 6.0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                username TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS inbox_items (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
                module TEXT NOT NULL,
                icon TEXT,
                title TEXT NOT NULL,
                meta TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS practice_records (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
                module TEXT NOT NULL,
                record_type TEXT NOT NULL,
                ref_id TEXT,
                title TEXT,
                overall_score REAL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS daily_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                pinned INTEGER NOT NULL DEFAULT 0,
                source TEXT NOT NULL DEFAULT 'system',
                sort_order INTEGER NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_username ON sessions(username);
            CREATE INDEX IF NOT EXISTS idx_inbox_username ON inbox_items(username, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_records_username ON practice_records(username, module, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_tasks_username ON daily_tasks(username, sort_order);
            """
        )
        conn.commit()
    finally:
        conn.close()
