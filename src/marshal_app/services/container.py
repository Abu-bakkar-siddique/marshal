from __future__ import annotations

from dataclasses import dataclass

from marshal_app.services.checkpoint_service import CheckpointService
from marshal_app.services.progress_service import ProgressService
from marshal_app.services.planning_service import PlanningService
from marshal_app.services.project_service import ProjectService
from marshal_app.services.section_service import SectionService
from marshal_app.services.task_service import TaskService


@dataclass(slots=True)
class ServiceContainer:
    project_service: ProjectService
    task_service: TaskService
    section_service: SectionService
    checkpoint_service: CheckpointService
    progress_service: ProgressService
    planning_service: PlanningService
