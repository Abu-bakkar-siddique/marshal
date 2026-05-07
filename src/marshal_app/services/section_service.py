from __future__ import annotations

from marshal_app.domain.models import Section
from marshal_app.storage.repositories.section_repository import SectionRepository


class SectionService:
    def __init__(self, repository: SectionRepository) -> None:
        self._repository = repository

    def list_sections(self, project_id: int) -> list[Section]:
        return self._repository.list_for_project(project_id)
