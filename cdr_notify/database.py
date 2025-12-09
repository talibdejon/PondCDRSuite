import sqlite3
from pathlib import Path
from typing import Optional

# ============================================================
# Configure database location here
# ============================================================

# Example for production:
# DATABASE_PATH = "/var/lib/cdr_notify/cdr_files.db"
#
# Example for development/testing:
# DATABASE_PATH = "./cdr_files.db"

DATABASE_PATH: str = "./cdr_files.db"


# ============================================================
# Connection helper
# ============================================================

def get_connection() -> sqlite3.Connection:
    """
    Open a SQLite connection using DATABASE_PATH.
    """
    if not DATABASE_PATH:
        raise RuntimeError("DATABASE_PATH is not set.")

    db_path = Path(DATABASE_PATH).expanduser().resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# Initialization
# ============================================================

def init_db() -> None:
    """
    Create the cdr_files table if it does not exist.
    """
    create_sql = """
    CREATE TABLE IF NOT EXISTS cdr_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        hash TEXT NOT NULL,
        changed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT CHECK(status IN ('Arrived', 'Sent', 'Delivered', 'Removed')) DEFAULT 'Arrived'
    );
    """

    conn = get_connection()
    try:
        conn.execute(create_sql)
        conn.commit()
    finally:
        conn.close()


# ============================================================
# DB operations
# ============================================================

def fetch_by_hash(file_hash: str) -> Optional[sqlite3.Row]:
    """
    Select a record by its file hash.
    """
    conn = get_connection()
    try:
        cur = conn.execute("SELECT * FROM cdr_files WHERE hash = ?", (file_hash,))
        return cur.fetchone()
    finally:
        conn.close()


def insert_record(filename: str, file_hash: str, status: str) -> int:
    """
    Insert a new file record. Returns the inserted row id.
    """
    sql = """
    INSERT INTO cdr_files (filename, hash, status)
    VALUES (?, ?, ?)
    """

    conn = get_connection()
    try:
        cur = conn.execute(sql, (filename, file_hash, status))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_status(file_hash: str, new_status: str) -> bool:
    """
    Update status of an existing record by its hash.
    Returns True if at least one row was updated.
    """
    sql = """
    UPDATE cdr_files
    SET status = ?, changed = CURRENT_TIMESTAMP
    WHERE hash = ?
    """

    conn = get_connection()
    try:
        cur = conn.execute(sql, (new_status, file_hash))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
