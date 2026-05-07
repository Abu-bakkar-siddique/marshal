from __future__ import annotations

import sqlite3

from marshal_app.domain.models import Section


class SectionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def list_for_project(self, project_id: int) -> list[Section]:
        rows = self._connection.execute(
            """
            SELECT id, project_id, title, description, created_at, updated_at
            FROM sections
            WHERE project_id = ?
            ORDER BY id
            """,
            (project_id,),
        ).fetchall()
        return [
            Section(
                id=row["id"],
                project_id=row["project_id"],
                title=row["title"],
                description=row["description"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]
