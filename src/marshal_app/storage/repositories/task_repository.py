from __future__ import annotations

import sqlite3

from marshal_app.domain.models import Task


class TaskRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create_for_project(
        self,
        project_id: int,
        title: str,
        comments: str = "",
    ) -> Task:
        next_sort_order = self._next_sort_order_for_project(project_id)
        cursor = self._connection.execute(
            """
            INSERT INTO tasks (project_id, title, comments, sort_order)
            VALUES (?, ?, ?, ?)
            """,
            (project_id, title, comments, next_sort_order),
        )
        self._connection.commit()
        task_id = int(cursor.lastrowid)
        task = self.get(task_id)
        if task is None:
            raise RuntimeError("Failed to create task")
        return task

    def get(self, task_id: int) -> Task | None:
        row = self._connection.execute(
            """
            SELECT id, project_id, section_id, title, comments, is_done, sort_order,
                   completed_at, created_at, updated_at
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()
        if row is None:
            return None
        return Task(
            id=row["id"],
            project_id=row["project_id"],
            section_id=row["section_id"],
            title=row["title"],
            comments=row["comments"],
            is_done=bool(row["is_done"]),
            sort_order=row["sort_order"],
            completed_at=row["completed_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_for_project(self, project_id: int) -> list[Task]:
        rows = self._connection.execute(
            """
            SELECT id, project_id, section_id, title, comments, is_done, sort_order,
                   completed_at, created_at, updated_at
            FROM tasks
            WHERE project_id = ?
            ORDER BY is_done, sort_order, id
            """,
            (project_id,),
        ).fetchall()
        return [
            Task(
                id=row["id"],
                project_id=row["project_id"],
                section_id=row["section_id"],
                title=row["title"],
                comments=row["comments"],
                is_done=bool(row["is_done"]),
                sort_order=row["sort_order"],
                completed_at=row["completed_at"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def update_done_state(self, task_id: int, is_done: bool) -> None:
        self._connection.execute(
            """
            UPDATE tasks
            SET is_done = ?,
                completed_at = CASE WHEN ? = 1 THEN CURRENT_TIMESTAMP ELSE NULL END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (int(is_done), int(is_done), task_id),
        )
        self._connection.commit()

    def delete(self, task_id: int) -> None:
        self._connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self._connection.commit()

    def reorder_project_tasks(self, project_id: int, ordered_task_ids: list[int]) -> None:
        updates = [
            (index * 100, task_id, project_id)
            for index, task_id in enumerate(ordered_task_ids, start=1)
        ]
        self._connection.executemany(
            """
            UPDATE tasks
            SET sort_order = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND project_id = ? AND is_done = 0
            """,
            updates,
        )
        self._connection.commit()

    def _next_sort_order_for_project(self, project_id: int) -> int:
        row = self._connection.execute(
            """
            SELECT COALESCE(MAX(sort_order), 0) AS max_sort_order
            FROM tasks
            WHERE project_id = ?
            """,
            (project_id,),
        ).fetchone()
        return int(row["max_sort_order"]) + 100
