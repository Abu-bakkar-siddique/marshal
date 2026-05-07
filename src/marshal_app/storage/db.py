from __future__ import annotations

import sqlite3
from pathlib import Path

from marshal_app.app.paths import PACKAGE_ROOT


def connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def initialize_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path = PACKAGE_ROOT / "storage" / "schema.sql"

    with connect(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
