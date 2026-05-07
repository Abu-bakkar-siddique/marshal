from __future__ import annotations

import sqlite3

from marshal_app.domain.models import TaskCheckpoint


class CheckpointRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def latest_for_task(self, task_id: int) -> TaskCheckpoint | None:
        row = self._connection.execute(
            """
            SELECT id, task_id, body, created_at
            FROM task_checkpoints
            WHERE task_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (task_id,),
        ).fetchone()
        if row is None:
            return None
        return TaskCheckpoint(
            id=row["id"],
            task_id=row["task_id"],
            body=row["body"],
            created_at=row["created_at"],
        )
