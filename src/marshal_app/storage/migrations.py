from __future__ import annotations

from pathlib import Path

from marshal_app.storage.db import initialize_database


def migrate(database_path: Path) -> None:
    initialize_database(database_path)
