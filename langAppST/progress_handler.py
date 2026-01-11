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
        #TODO: Setup connection, read into ghow commands work for sql


    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(database_path)
        return conn