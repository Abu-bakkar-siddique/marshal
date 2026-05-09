from __future__ import annotations

from marshal_app.domain.models import Task
from marshal_app.domain.rules import derive_active_task
from marshal_app.storage.repositories.task_repository import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create_task_for_project(
        self,
        project_id: int,
        title: str,
        comments: str = "",
    ) -> Task:
        return self._repository.create_for_project(project_id, title, comments)

    def create_standalone_task(self, title: str, comments: str = "") -> Task:
        return self._repository.create_standalone(title, comments)

    def set_done_state(self, task_id: int, is_done: bool) -> None:
        self._repository.update_done_state(task_id, is_done)

    def delete_task(self, task_id: int) -> None:
        self._repository.delete(task_id)

    def reorder_project_tasks(self, project_id: int, ordered_task_ids: list[int]) -> None:
        self._repository.reorder_project_tasks(project_id, ordered_task_ids)

    def reorder_standalone_tasks(self, ordered_task_ids: list[int]) -> None:
        self._repository.reorder_standalone_tasks(ordered_task_ids)

    def list_project_tasks(self, project_id: int) -> list[Task]:
        return self._repository.list_for_project(project_id)

    def list_standalone_tasks(self) -> list[Task]:
        return self._repository.list_standalone()

    def active_task_for_project(self, project_id: int) -> Task | None:
        return derive_active_task(self.list_project_tasks(project_id))
