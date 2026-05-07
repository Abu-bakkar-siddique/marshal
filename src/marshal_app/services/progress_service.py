from __future__ import annotations

from marshal_app.domain.models import Task
from marshal_app.domain.rules import project_progress


class ProgressService:
    def progress_for_tasks(self, tasks: list[Task]) -> tuple[int, int, int]:
        return project_progress(tasks)
