from __future__ import annotations

from marshal_app.domain.models import TaskCheckpoint
from marshal_app.storage.repositories.checkpoint_repository import CheckpointRepository


class CheckpointService:
    def __init__(self, repository: CheckpointRepository) -> None:
        self._repository = repository

    def latest_for_task(self, task_id: int) -> TaskCheckpoint | None:
        return self._repository.latest_for_task(task_id)
