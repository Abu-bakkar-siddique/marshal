from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from marshal_app.services.checkpoint_service import CheckpointService
from marshal_app.services.container import ServiceContainer
from marshal_app.services.planning_service import PlanningService, RuleBasedPlanningEngine
from marshal_app.services.progress_service import ProgressService
from marshal_app.services.project_service import ProjectService
from marshal_app.services.section_service import SectionService
from marshal_app.services.task_service import TaskService
from marshal_app.storage.db import connect, initialize_database
from marshal_app.storage.repositories.checkpoint_repository import CheckpointRepository
from marshal_app.storage.repositories.project_repository import ProjectRepository
from marshal_app.storage.repositories.section_repository import SectionRepository
from marshal_app.storage.repositories.task_repository import TaskRepository
from marshal_app.ui.main_window import MainWindow


class PlanningGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Create a single Qt application for the whole GUI test class."""
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        """Open a fresh window backed by a temporary database."""
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "marshal.db"
        initialize_database(self.db_path)
        self.connection = connect(self.db_path)
        self.services = ServiceContainer(
            project_service=ProjectService(ProjectRepository(self.connection)),
            task_service=TaskService(TaskRepository(self.connection)),
            section_service=SectionService(SectionRepository(self.connection)),
            checkpoint_service=CheckpointService(CheckpointRepository(self.connection)),
            progress_service=ProgressService(),
            planning_service=PlanningService(RuleBasedPlanningEngine()),
        )
        self.window = MainWindow(self.services)
        self.window.show()
        QTest.qWait(50)

    def tearDown(self) -> None:
        """Close the window and clean up the temporary database."""
        self.window.close()
        self.connection.close()
        self._tmpdir.cleanup()

    def test_accepting_planner_creates_project_and_tasks(self) -> None:
        """Check that the planner can be used from the real Qt interface."""
        planner_button = self.window.sidebar.planner_button
        QTest.mouseClick(planner_button, Qt.MouseButton.LeftButton)
        QTest.qWait(20)

        self.assertIs(self.window.content_stack.currentWidget(), self.window.planning_view)

        input_text = "Build a landing page for the product and collect early signups."
        self.window.planning_view.input_edit.setFocus()
        QTest.keyClicks(self.window.planning_view.input_edit, input_text)
        QTest.mouseClick(self.window.planning_view.send_button, Qt.MouseButton.LeftButton)
        QTest.qWait(50)

        self.assertTrue(self.window.planning_view.accept_button.isEnabled())
        transcript = self.window.planning_view.transcript.toPlainText()
        self.assertIn("Tentative tasks", transcript)

        QTest.mouseClick(self.window.planning_view.accept_button, Qt.MouseButton.LeftButton)
        QTest.qWait(100)

        self.assertIs(self.window.content_stack.currentWidget(), self.window.project_view)
        self.assertIsNotNone(self.window.selected_project_id)

        project_rows = self.connection.execute(
            "SELECT title, description FROM projects ORDER BY id"
        ).fetchall()
        task_rows = self.connection.execute(
            "SELECT title, comments FROM tasks ORDER BY id"
        ).fetchall()

        self.assertEqual(len(project_rows), 1)
        self.assertLessEqual(len(project_rows[0]["title"].split()), 3)
        self.assertLessEqual(len(project_rows[0]["description"]), 120)
        self.assertGreaterEqual(len(task_rows), 1)
        self.assertTrue(all(len(row["title"].split()) <= 3 for row in task_rows))


if __name__ == "__main__":
    unittest.main()
