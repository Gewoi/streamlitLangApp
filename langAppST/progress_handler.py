from __future__ import annotations

import sqlite3
from dataclasses import dataclass
import os
from pathlib import Path

from datetime import datetime, timezone
import json

DB_PATH = Path("data") / "progress.sqlite"

class ProgressStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._initialize_db()
        #TODO: Setup connection, read into ghow commands work for sql

    def _initialize_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS lesson_progress (
                    user TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    lesson_id TEXT NOT NULL,
                    completed INT NOT NULL DEFAULT 0,
                    mistakes INT NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(user, course_id, lesson_id)
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_stats (
                    user TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    known_words TEXT NOT NULL DEFAULT "{}",
                    PRIMARY KEY(user, course_id)
                );
                """
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        return conn
    
    def lesson_completed(self, user: str, course_id: str, lesson_id: str, mistakes_made : int, new_words = {}) -> None:
        now = datetime.now(timezone.utc).isoformat()
        completed_list = self.get_known_words(user=user, course_id=course_id)
        completed_list.update(new_words)
        completed_json = json.dumps(completed_list)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO lesson_progress(user, course_id, lesson_id, completed, mistakes, updated_at)
                VALUES(?,?,?,?,?,?)
                ON CONFLICT(user, course_id, lesson_id)
                DO UPDATE SET mistakes=excluded.mistakes, updated_at=excluded.updated_at
                """,
                (user, course_id, lesson_id, 1, mistakes_made, now),
            )
            conn.execute(
                    """
                    INSERT INTO user_stats(user, course_id, known_words)
                    VALUES(?,?,?)
                    ON CONFLICT(user, course_id)
                    DO UPDATE SET known_words=excluded.known_words
                    """,
                    (user, course_id, completed_json),
                )
            
    def check_lesson_completed(self, user: str, course_id: str, lesson_id : str):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT completed FROM lesson_progress WHERE user=? AND course_id=? AND lesson_id=?",
                (user, course_id, lesson_id),
            ).fetchone()
        if not row:
            return 0
        return int(row[0])

    def reset_lesson(self, user: str, course_id: str, lesson_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM lesson_progress WHERE user=? AND course_id=? AND lesson_id=?",
                (user, course_id, lesson_id),
            )

    def get_known_words(self, user: str, course_id: str):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT known_words FROM user_stats WHERE user=? AND course_id=?",
                (user, course_id),
            ).fetchone()
        if not row:
            return {}
        completed_json = row
        try:
            completed_list = json.loads(completed_json) if completed_json else {}
        except Exception:
            completed_list = {}
        return completed_list