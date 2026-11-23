import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "database", "leafguard.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                disease TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def save_prediction(filename, disease, confidence):
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO predictions (filename, disease, confidence) VALUES (?, ?, ?)",
            (filename, disease, confidence),
        )
        connection.commit()


def get_history(limit=20):
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, filename, disease, confidence, created_at FROM predictions ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]
