from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from marshal_app.domain.models import Project, Task
from marshal_app.domain.rules import can_close_project, derive_active_task, project_progress
from marshal_app.services.project_service import ProjectService
from marshal_app.services.task_service import TaskService
from marshal_app.storage.db import connect, initialize_database
from marshal_app.storage.repositories.project_repository import ProjectRepository
from marshal_app.storage.repositories.task_repository import TaskRepository


class DomainRulesTests(unittest.TestCase):
    def test_derive_active_task_picks_first_incomplete_by_sort_order(self) -> None:
        tasks = [
            Task(id=1, title="Done first", is_done=True, sort_order=100),
            Task(id=2, title="Later task", is_done=False, sort_order=300),
            Task(id=3, title="Earliest active", is_done=False, sort_order=200),
        ]

        active = derive_active_task(tasks)

        self.assertIsNotNone(active)
        self.assertEqual(active.id, 3)
        self.assertEqual(active.title, "Earliest active")

    def test_project_progress_and_close_rules_handle_empty_and_completed_lists(self) -> None:
        self.assertEqual(project_progress([]), (0, 0, 0))
        self.assertFalse(can_close_project([]))

        tasks = [
            Task(id=1, title="One", is_done=True),
            Task(id=2, title="Two", is_done=True),
            Task(id=3, title="Three", is_done=True),
        ]

        self.assertEqual(project_progress(tasks), (3, 3, 100))
        self.assertTrue(can_close_project(tasks))


class RepositoryAndServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tempdir.name) / "marshal.db"
        initialize_database(self.db_path)
        self.connection = connect(self.db_path)
        self.project_repository = ProjectRepository(self.connection)
        self.task_repository = TaskRepository(self.connection)
        self.project_service = ProjectService(self.project_repository)
        self.task_service = TaskService(self.task_repository)

    def tearDown(self) -> None:
        self.connection.close()
        self._tempdir.cleanup()

    def test_project_and_task_services_round_trip_through_sqlite(self) -> None:
        project = self.project_service.create_project("Release v1", "Ship the first public build")
        self.assertIsInstance(project, Project)
        self.assertIsNotNone(project.id)
        self.assertEqual(project.sort_order, 100)
        project_id = project.id
        assert project_id is not None

        first = self.task_service.create_task_for_project(project_id, "Draft release notes")
        second = self.task_service.create_task_for_project(project_id, "Finalize changelog")
        self.assertEqual(first.sort_order, 100)
        self.assertEqual(second.sort_order, 200)

        first_id = first.id
        assert first_id is not None
        self.task_service.set_done_state(first_id, True)

        ordered_tasks = self.task_service.list_project_tasks(project_id)
        self.assertEqual([task.title for task in ordered_tasks], ["Finalize changelog", "Draft release notes"])
        self.assertTrue(ordered_tasks[-1].is_done)

        active_task = self.task_service.active_task_for_project(project_id)
        self.assertIsNotNone(active_task)
        self.assertEqual(active_task.title, "Finalize changelog")

        self.task_service.create_standalone_task("Triage inbox")
        standalone_tasks = self.task_service.list_standalone_tasks()
        self.assertEqual(len(standalone_tasks), 1)
        self.assertEqual(standalone_tasks[0].title, "Triage inbox")


if __name__ == "__main__":
    unittest.main()
