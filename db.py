"""Database helper: one SQLite connection per request, schema initialisation."""
import sqlite3
from pathlib import Path

from flask import current_app, g

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Return the connection for the current request, opening it if needed."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_connection(_exc=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(db_path) -> None:
    """Create all tables (drops existing ones) and insert the four user profiles."""
    connection = sqlite3.connect(db_path)
    connection.executescript(SCHEMA_PATH.read_text())
    connection.commit()
    connection.close()
