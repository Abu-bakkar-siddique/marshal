from __future__ import annotations

from marshal_app.domain.models import Project
from marshal_app.storage.repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    def create_project(self, title: str, description: str = "") -> Project:
        return self._repository.create(title, description)

    def get_project(self, project_id: int) -> Project | None:
        return self._repository.get(project_id)

    def list_projects(self) -> list[Project]:
        return self._repository.list_all()
