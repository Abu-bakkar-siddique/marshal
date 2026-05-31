from __future__ import annotations

from marshal_app.domain.models import Task


def derive_active_task(tasks: list[Task]) -> Task | None:
    incomplete = [task for task in tasks if not task.is_done]
    if not incomplete:
        return None
    return min(incomplete, key=lambda task: task.sort_order)

def can_close_project(tasks: list[Task]) -> bool:
    return bool(tasks) and all(task.is_done for task in tasks)

def project_progress(tasks: list[Task]) -> tuple[int, int, int]:
    total = len(tasks)
    done = sum(1 for task in tasks if task.is_done)
    percentage = round((done / total) * 100) if total else 0
    return done, total, percentage