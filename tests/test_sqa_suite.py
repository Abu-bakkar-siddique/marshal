from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from marshal_app.domain.models import Task
from marshal_app.domain.rules import can_close_project, derive_active_task, project_progress
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


class DatabaseFixture(unittest.TestCase):
    def setUp(self) -> None:
        """Create one temporary database and the services that use it."""
        self._tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tempdir.name) / "marshal.db"
        initialize_database(self.db_path)
        self.connection = connect(self.db_path)
        self.addCleanup(self.connection.close)
        self.addCleanup(self._tempdir.cleanup)

        self.project_repository = ProjectRepository(self.connection)
        self.task_repository = TaskRepository(self.connection)
        self.section_repository = SectionRepository(self.connection)
        self.checkpoint_repository = CheckpointRepository(self.connection)

        self.project_service = ProjectService(self.project_repository)
        self.task_service = TaskService(self.task_repository)
        self.section_service = SectionService(self.section_repository)
        self.checkpoint_service = CheckpointService(self.checkpoint_repository)
        self.progress_service = ProgressService()
        self.planning_service = PlanningService(RuleBasedPlanningEngine())
        self.services = ServiceContainer(
            project_service=self.project_service,
            task_service=self.task_service,
            section_service=self.section_service,
            checkpoint_service=self.checkpoint_service,
            progress_service=self.progress_service,
            planning_service=self.planning_service,
        )

    def insert_project(self, title: str, description: str = "", sort_order: int = 100) -> int:
        """Insert a project row directly into SQLite for test setup."""
        cursor = self.connection.execute(
            """
            INSERT INTO projects (title, description, sort_order)
            VALUES (?, ?, ?)
            """,
            (title, description, sort_order),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def insert_section(self, project_id: int, title: str, description: str = "") -> int:
        """Insert a section row directly into SQLite for test setup."""
        cursor = self.connection.execute(
            """
            INSERT INTO sections (project_id, title, description)
            VALUES (?, ?, ?)
            """,
            (project_id, title, description),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def insert_task(
        self,
        *,
        project_id: int | None,
        title: str,
        comments: str = "",
        is_done: int = 0,
        sort_order: int = 100,
        section_id: int | None = None,
        completed_at: str | None = None,
    ) -> int:
        """Insert a task row directly into SQLite for test setup."""
        cursor = self.connection.execute(
            """
            INSERT INTO tasks (
                project_id, section_id, title, comments, is_done, sort_order, completed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, section_id, title, comments, is_done, sort_order, completed_at),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def insert_checkpoint(self, task_id: int, body: str, created_at: str) -> int:
        """Insert a checkpoint row directly into SQLite for test setup."""
        cursor = self.connection.execute(
            """
            INSERT INTO task_checkpoints (task_id, body, created_at)
            VALUES (?, ?, ?)
            """,
            (task_id, body, created_at),
        )
        self.connection.commit()
        return int(cursor.lastrowid)


class SchemaAndIntegrityTests(unittest.TestCase):
    def test_initialize_database_creates_expected_tables_and_indexes(self) -> None:
        """Check that the app creates the tables and indexes it depends on."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "marshal.db"
            initialize_database(db_path)

            with connect(db_path) as connection:
                tables = {
                    row["name"]
                    for row in connection.execute(
                        """
                        SELECT name
                        FROM sqlite_master
                        WHERE type = 'table'
                        ORDER BY name
                        """
                    ).fetchall()
                }
                indexes = {
                    row["name"]
                    for row in connection.execute(
                        """
                        SELECT name
                        FROM sqlite_master
                        WHERE type = 'index'
                        ORDER BY name
                        """
                    ).fetchall()
                }

        self.assertTrue({"projects", "sections", "tasks", "task_checkpoints"}.issubset(tables))
        self.assertIn("idx_tasks_project_order", indexes)
        self.assertIn("idx_checkpoints_task_created", indexes)

    def test_section_insert_requires_existing_project(self) -> None:
        """Check that SQLite rejects a section that points to no project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "marshal.db"
            initialize_database(db_path)

            with connect(db_path) as connection:
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(
                        """
                        INSERT INTO sections (project_id, title, description)
                        VALUES (?, ?, ?)
                        """,
                        (999, "Orphan section", ""),
                    )
                    connection.commit()


class RepositoryBehaviorTests(DatabaseFixture):
    def test_project_repository_assigns_progressive_sort_order(self) -> None:
        """Check that new projects are numbered in the order they are created."""
        first = self.project_repository.create("Alpha", "first")
        second = self.project_repository.create("Beta", "second")

        self.assertEqual(first.sort_order, 100)
        self.assertEqual(second.sort_order, 200)

    def test_project_service_lists_projects_in_sort_order(self) -> None:
        """Check that the project list comes back in the expected order."""
        gamma = self.project_repository.create("Gamma")
        alpha = self.project_repository.create("Alpha")

        listed = self.project_service.list_projects()
        self.assertEqual([project.title for project in listed], [gamma.title, alpha.title])

    def test_task_repository_creates_project_and_standalone_tasks(self) -> None:
        """Check that tasks can belong to a project or stand alone."""
        project_id = self.insert_project("Queue")

        project_task = self.task_repository.create_for_project(project_id, "Ship feature", "project work")
        standalone_task = self.task_repository.create_standalone("Pay invoice", "personal work")

        self.assertEqual(project_task.project_id, project_id)
        self.assertIsNone(standalone_task.project_id)
        self.assertEqual(project_task.sort_order, 100)
        self.assertEqual(standalone_task.sort_order, 100)

    def test_task_repository_orders_incomplete_tasks_before_completed_tasks(self) -> None:
        """Check that unfinished tasks stay ahead of finished ones."""
        project_id = self.insert_project("Queue")
        done_id = self.insert_task(project_id=project_id, title="Completed", is_done=1, sort_order=300)
        later_id = self.insert_task(project_id=project_id, title="Later", is_done=0, sort_order=200)
        early_id = self.insert_task(project_id=project_id, title="Early", is_done=0, sort_order=100)

        ordered = self.task_repository.list_for_project(project_id)
        self.assertEqual([task.id for task in ordered], [early_id, later_id, done_id])
        self.assertEqual(derive_active_task(ordered).id, early_id)

    def test_task_repository_done_state_round_trips_completed_timestamp(self) -> None:
        """Check that marking a task done stores and clears its finish time."""
        task_id = self.insert_task(project_id=None, title="Standalone", sort_order=100)

        self.task_repository.update_done_state(task_id, True)
        completed = self.task_repository.get(task_id)
        self.assertIsNotNone(completed)
        self.assertTrue(completed.is_done)
        self.assertIsNotNone(completed.completed_at)

        self.task_repository.update_done_state(task_id, False)
        reopened = self.task_repository.get(task_id)
        self.assertIsNotNone(reopened)
        self.assertFalse(reopened.is_done)
        self.assertIsNone(reopened.completed_at)

    def test_task_repository_reorder_skips_completed_tasks(self) -> None:
        """Check that completed tasks are left at the end during reordering."""
        project_id = self.insert_project("Queue")
        first_id = self.insert_task(project_id=project_id, title="First", sort_order=100)
        second_id = self.insert_task(project_id=project_id, title="Second", sort_order=200)
        done_id = self.insert_task(project_id=project_id, title="Done", is_done=1, sort_order=300)

        self.task_repository.reorder_project_tasks(project_id, [second_id, done_id, first_id])

        ordered = self.task_repository.list_for_project(project_id)
        self.assertEqual([task.id for task in ordered], [second_id, first_id, done_id])
        self.assertEqual([task.sort_order for task in ordered[:2]], [100, 300])
        self.assertEqual(ordered[-1].sort_order, 300)

    def test_section_repository_lists_sections_for_project(self) -> None:
        """Check that the app returns the sections belonging to one project."""
        project_id = self.insert_project("Publication")
        section_a = self.insert_section(project_id, "Drafting")
        section_b = self.insert_section(project_id, "Review")

        sections = self.section_repository.list_for_project(project_id)
        self.assertEqual([section.id for section in sections], [section_a, section_b])

    def test_checkpoint_repository_returns_latest_checkpoint(self) -> None:
        """Check that the newest checkpoint is the one returned."""
        task_id = self.insert_task(project_id=None, title="Standalone", sort_order=100)
        first = self.insert_checkpoint(task_id, "First checkpoint", "2026-05-01 10:00:00")
        second = self.insert_checkpoint(task_id, "Second checkpoint", "2026-05-01 12:00:00")

        latest = self.checkpoint_repository.latest_for_task(task_id)
        self.assertIsNotNone(latest)
        self.assertEqual(latest.id, second)
        self.assertEqual(latest.body, "Second checkpoint")
        self.assertEqual(latest.task_id, task_id)
        self.assertNotEqual(first, second)


class ServiceAndPlanningTests(DatabaseFixture):
    def test_service_container_exposes_expected_services(self) -> None:
        """Check that the service container stores the services we built."""
        self.assertIs(self.services.project_service, self.project_service)
        self.assertIs(self.services.task_service, self.task_service)
        self.assertIs(self.services.section_service, self.section_service)
        self.assertIs(self.services.checkpoint_service, self.checkpoint_service)
        self.assertIs(self.services.progress_service, self.progress_service)
        self.assertIs(self.services.planning_service, self.planning_service)

    def test_section_service_delegates_to_repository(self) -> None:
        """Check that the section service reads back the same section row."""
        project_id = self.insert_project("Research")
        section_id = self.insert_section(project_id, "Reading list")

        sections = self.section_service.list_sections(project_id)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].id, section_id)

    def test_checkpoint_service_returns_latest_checkpoint(self) -> None:
        """Check that the checkpoint service returns the latest saved note."""
        task_id = self.insert_task(project_id=None, title="Standalone", sort_order=100)
        self.insert_checkpoint(task_id, "Draft checkpoint", "2026-05-01 09:00:00")
        self.insert_checkpoint(task_id, "Final checkpoint", "2026-05-01 10:00:00")

        checkpoint = self.checkpoint_service.latest_for_task(task_id)
        self.assertIsNotNone(checkpoint)
        self.assertEqual(checkpoint.body, "Final checkpoint")

    def test_progress_service_matches_domain_progress_rules(self) -> None:
        """Check that the progress service agrees with the domain logic."""
        tasks = [
            Task(id=1, title="One", is_done=True),
            Task(id=2, title="Two", is_done=False),
            Task(id=3, title="Three", is_done=False),
            Task(id=4, title="Four", is_done=True),
        ]

        self.assertEqual(self.progress_service.progress_for_tasks(tasks), project_progress(tasks))
        self.assertEqual(self.progress_service.progress_for_tasks(tasks), (2, 4, 50))
        self.assertFalse(can_close_project(tasks))

    def test_task_service_active_task_tracks_first_open_item(self) -> None:
        """Check that the task service picks the first unfinished task."""
        project_id = self.insert_project("Release")
        first_id = self.insert_task(project_id=project_id, title="Draft", sort_order=100)
        second_id = self.insert_task(project_id=project_id, title="Ship", sort_order=200)

        self.task_service.set_done_state(first_id, True)
        active = self.task_service.active_task_for_project(project_id)

        self.assertIsNotNone(active)
        self.assertEqual(active.id, second_id)


class PlanningWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        """Create a planner service for the workflow tests."""
        self.service = PlanningService(RuleBasedPlanningEngine())

    def test_empty_input_uses_fallback_tasks_and_default_question(self) -> None:
        """Check that blank input still produces a simple fallback plan."""
        session = self.service.create_session("")

        self.assertEqual(session.phase.name, "DRAFT")
        self.assertEqual(session.goal_summary, "No input provided yet")
        self.assertEqual(len(session.tentative_tasks), 3)
        self.assertIsNotNone(session.clarification_question)
        self.assertIn("What should this planner work on?", session.clarification_question or "")
        self.assertIn("Fallback draft", [task.rationale for task in session.tentative_tasks])

    def test_short_input_prompts_for_clarification(self) -> None:
        """Check that vague input asks the user to be more specific."""
        session = self.service.create_session("Launch the site")

        self.assertEqual(session.phase.name, "DRAFT")
        self.assertIsNotNone(session.clarification_question)
        self.assertIn("concrete outcome", session.clarification_question or "")
        self.assertIn("Tentative tasks:", self.service.render_tentative_draft_text(session))

    def test_bullets_become_distinct_tasks(self) -> None:
        """Check that a list in the prompt turns into separate tasks."""
        session = self.service.create_session("Draft homepage copy; wire checkout flow; add analytics.")

        titles = [task.title for task in session.tentative_tasks]
        self.assertEqual(titles, ["Draft homepage copy", "Wire checkout flow", "Add analytics"])
        self.assertEqual(session.phase.name, "REVIEW")

    def test_rule_engine_caps_task_count_at_five(self) -> None:
        """Check that the planner does not produce too many tasks at once."""
        session = self.service.create_session("one. two. three. four. five. six. seven.")

        self.assertEqual(len(session.tentative_tasks), 5)
        self.assertEqual([task.title for task in session.tentative_tasks], ["One", "Two", "Three", "Four", "Five"])

    def test_revision_increments_counter_and_extends_transcript(self) -> None:
        """Check that a revision is counted and added to the conversation."""
        session = self.service.create_session("Build a portfolio site")
        revised = self.service.revise_session(session, "Split it into layout, copy, and deployment.")

        self.assertEqual(revised.revision_count, 1)
        self.assertGreater(len(revised.transcript), len(session.transcript))
        self.assertIn("User clarification:", self.service.render_transcript_text(revised))
        self.assertIn("Assistant revision:", self.service.render_transcript_text(revised))

    def test_approval_clones_tentative_tasks_into_structured_output(self) -> None:
        """Check that approval copies the draft tasks into final output."""
        session = self.service.create_session("Ship a landing page with email capture and analytics")
        approved = self.service.approve_session(session)

        self.assertEqual(approved.phase.name, "APPROVED")
        self.assertEqual(len(approved.structured_tasks), len(session.tentative_tasks))
        self.assertEqual([task.title for task in approved.structured_tasks], [task.title for task in session.tentative_tasks])
        self.assertIn("Structured output:", self.service.render_structured_preview_text(approved))

    def test_render_transcript_joins_messages_with_spacing(self) -> None:
        """Check that the transcript is printed in a readable format."""
        session = self.service.create_session("Write docs")

        transcript = self.service.render_transcript_text(session)
        self.assertIn("User:", transcript)
        self.assertIn("Assistant:", transcript)
        self.assertIn("\n\n", transcript)


if __name__ == "__main__":
    unittest.main(verbosity=2)
