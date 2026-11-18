"""C11 Database: SQLite storage for all records and the audit log.

Build step 2. Planned responsibilities:
- Create tables for the records in models.py.
- Provide read/write helpers used by services and pipeline jobs.
- Record approvals, rejections, fallbacks, and deletions in the audit log.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(db_path: str) -> sqlite3.Connection:
    """Open the database, creating its folder if needed."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Create all tables. Build step 2."""
    raise NotImplementedError("Build step 2: database schema")
