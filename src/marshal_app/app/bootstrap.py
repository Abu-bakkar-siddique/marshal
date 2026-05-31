from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from marshal_app.app.settings import DEFAULT_SETTINGS
from marshal_app.services.checkpoint_service import CheckpointService
from marshal_app.services.container import ServiceContainer
from marshal_app.services.progress_service import ProgressService
from marshal_app.services.planning_service import PlanningService
from marshal_app.services.project_service import ProjectService
from marshal_app.services.section_service import SectionService
from marshal_app.services.task_service import TaskService
from marshal_app.storage.db import connect, initialize_database
from marshal_app.storage.repositories.checkpoint_repository import CheckpointRepository
from marshal_app.storage.repositories.project_repository import ProjectRepository
from marshal_app.storage.repositories.section_repository import SectionRepository
from marshal_app.storage.repositories.task_repository import TaskRepository
from marshal_app.ui.main_window import MainWindow


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(DEFAULT_SETTINGS.app_name)
    app.setOrganizationName(DEFAULT_SETTINGS.organization_name)

    initialize_database(DEFAULT_SETTINGS.database_path)
    connection = connect(DEFAULT_SETTINGS.database_path)

    services = ServiceContainer(
        project_service=ProjectService(ProjectRepository(connection)),
        task_service=TaskService(TaskRepository(connection)),
        section_service=SectionService(SectionRepository(connection)),
        checkpoint_service=CheckpointService(CheckpointRepository(connection)),
        progress_service=ProgressService(),
        planning_service=PlanningService(),
    )

    window = MainWindow(services)
    window.show()

    return app.exec()
