from __future__ import annotations

import sqlite3
from dataclasses import dataclass
import os


database_path = os.path("data/progress.db")

@dataclass
class LessonProgress:
    last_step : int 
    completed_steps : set[int]

class ProgressStore:
    def __init__(self, db_path : os.path = database_path):
        self.db_path = db_path
        self._initialize_db()
        #TODO: Setup connection, read into ghow commands work for sql

    def _initialize_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS progress (
                    user TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    lesson_id TEXT NOT NULL,
                    lesson_comleted BOOLEAN NOT NULL,
                    PRIMARY KEY(user, course_id, lesson_id)
                );
                """
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(database_path)
        return conn