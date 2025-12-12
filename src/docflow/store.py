from __future__ import annotations
import sqlite3
import json
from datetime import datetime

class Store:
    def __init__(self, path: str):
        self.path = path

    def init(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
              run_id TEXT PRIMARY KEY,
              started_at TEXT,
              finished_at TEXT,
              pdf_original TEXT,
              status TEXT,
              extraction_json TEXT,
              error TEXT
            )""")
            conn.commit()

    def log_start(self, run_id: str, pdf_original: str):
        with sqlite3.connect(self.path) as conn:
            conn.execute("INSERT INTO runs(run_id, started_at, pdf_original, status)"
                         " VALUES(?,?,?,?)",
                         (run_id, datetime.utcnow().isoformat(), pdf_original, "processing"))
            conn.commit()

    def log_finish(self, run_id: str, status: str,
                   extraction: dict | None = None, error: str | None = None):
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "UPDATE runs SET finished_at=?, status=?, extraction_json=?, error=? WHERE run_id=?",
                (datetime.utcnow().isoformat(), status,
                 json.dumps(extraction) if extraction else None, error, run_id))
            conn.commit()