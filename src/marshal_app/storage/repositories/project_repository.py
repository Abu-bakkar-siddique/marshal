from __future__ import annotations

import sqlite3

from marshal_app.domain.models import Project


class ProjectRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(self, title: str, description: str = "") -> Project:
        next_sort_order = self._next_sort_order()
        cursor = self._connection.execute(
            """
            INSERT INTO projects (title, description, sort_order)
            VALUES (?, ?, ?)
            """,
            (title, description, next_sort_order),
        )
        self._connection.commit()
        project_id = int(cursor.lastrowid)
        project = self.get(project_id)
        if project is None:
            raise RuntimeError("Failed to create project")
        return project

    def get(self, project_id: int) -> Project | None:
        row = self._connection.execute(
            """
            SELECT id, title, description, sort_order, is_closed, closed_at, created_at, updated_at
            FROM projects
            WHERE id = ?
            """,
            (project_id,),
        ).fetchone()
        if row is None:
            return None
        return Project(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            sort_order=row["sort_order"],
            is_closed=bool(row["is_closed"]),
            closed_at=row["closed_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_all(self) -> list[Project]:
        rows = self._connection.execute(
            """
            SELECT id, title, description, sort_order, is_closed, closed_at, created_at, updated_at
            FROM projects
            ORDER BY sort_order, id
            """
        ).fetchall()
        return [
            Project(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                sort_order=row["sort_order"],
                is_closed=bool(row["is_closed"]),
                closed_at=row["closed_at"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def _next_sort_order(self) -> int:
        row = self._connection.execute(
            "SELECT COALESCE(MAX(sort_order), 0) AS max_sort_order FROM projects"
        ).fetchone()
        return int(row["max_sort_order"]) + 100
