import sqlite3
from typing import Optional

DB_NAME = "cdr_files.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cdr_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_hash TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            changed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def get_file_by_hash(file_hash: str) -> Optional[tuple]:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM cdr_files WHERE file_hash = ?", (file_hash,))
    row = cur.fetchone()
    conn.close()
    return row


def insert_file(filename: str, file_hash: str, status: str) -> bool:
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO cdr_files (filename, file_hash, status) VALUES (?, ?, ?)",
            (filename, file_hash, status)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def update_status(file_hash: str, status: str) -> bool:
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "UPDATE cdr_files SET status = ?, changed = CURRENT_TIMESTAMP WHERE file_hash = ?",
            (status, file_hash)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False
