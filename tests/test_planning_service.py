from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from marshal_app.domain.enums import PlanningPhase
from marshal_app.domain.models import Project
from marshal_app.services.planning_service import (
    GeminiPlanningEngine,
    PlanningService,
    RuleBasedPlanningEngine,
)


class FakeGeminiClient:
    def __init__(self, payload: dict[str, object]) -> None:
        """Store a fake AI response for the planner tests."""
        self.payload = payload

    def generate_json(
        self,
        *,
        system_instruction: str,
        user_input: str,
        schema_name: str,
        schema: dict[str, object],
    ) -> dict[str, object]:
        """Return the stored fake response instead of calling a real model."""
        return self.payload


class FakeProjectService:
    def __init__(self) -> None:
        """Track project creation calls without touching the real database."""
        self.created: list[tuple[str, str]] = []

    def create_project(self, title: str, description: str = "") -> Project:
        """Record the project that would have been created."""
        self.created.append((title, description))
        return Project(id=42, title=title, description=description, sort_order=100)


class FakeTaskService:
    def __init__(self) -> None:
        """Track task creation calls without touching the real database."""
        self.created: list[tuple[int, str, str]] = []

    def create_task_for_project(self, project_id: int, title: str, comments: str = "") -> None:
        """Record the task that would have been added to a project."""
        self.created.append((project_id, title, comments))


class PlanningServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        """Create a planner service that uses the simple rule-based engine."""
        self.service = PlanningService(RuleBasedPlanningEngine())

    def test_creates_tentative_draft_before_structured_output(self) -> None:
        """Check that the planner shows a draft before any accepted tasks."""
        session = self.service.create_session(
            "Launch a landing page for the product and collect early signups."
        )

        self.assertGreaterEqual(len(session.tentative_tasks), 1)
        self.assertEqual(session.structured_tasks, [])
        self.assertFalse(self.service.render_structured_preview_text(session))
        self.assertIn("Tentative tasks", self.service.render_tentative_draft_text(session))

    def test_approval_turns_draft_into_structured_preview(self) -> None:
        """Check that approving a draft turns it into structured work items."""
        session = self.service.create_session(
            "Build an onboarding flow, write the copy, and test the signup path."
        )
        approved = self.service.approve_session(session)

        self.assertEqual(approved.phase, PlanningPhase.APPROVED)
        self.assertEqual(len(approved.structured_tasks), len(session.tentative_tasks))
        self.assertTrue(self.service.render_structured_preview_text(approved))

    def test_revise_session_increments_revision_count(self) -> None:
        """Check that giving feedback makes the planner produce a new revision."""
        session = self.service.create_session("Ship a prototype")
        revised = self.service.revise_session(session, "Split it into UI, backend, and testing work.")

        self.assertEqual(revised.revision_count, session.revision_count + 1)
        self.assertGreater(len(revised.tentative_tasks), 0)
        self.assertGreater(len(revised.transcript), len(session.transcript))

    def test_gemini_engine_parses_structured_payload(self) -> None:
        """Check that the Gemini planner reads a structured response correctly."""
        engine = GeminiPlanningEngine(
            FakeGeminiClient(
                {
                    "goal_summary": "Launch a landing page",
                    "project_description": "Launch plan focused on headlines and signups.",
                    "tentative_tasks": [
                        {
                            "title": "Draft headline options and variations",
                            "description": "Write three possible page headlines.",
                            "rationale": "Keeps the first step small.",
                        }
                    ],
                    "clarification_question": "",
                }
            )
        )

        result = engine.draft("Launch a landing page and collect signups.")

        self.assertEqual(result.goal_summary, "Launch a landing page")
        self.assertEqual(result.project_description, "Launch plan focused on headlines and signups.")
        self.assertEqual(len(result.tentative_tasks), 1)
        self.assertLessEqual(len(result.tentative_tasks[0].title.split()), 3)
        self.assertIsNone(result.clarification_question)

    def test_materialize_session_creates_project_and_tasks(self) -> None:
        """Check that accepting a plan creates a real project and real tasks."""
        project_service = FakeProjectService()
        task_service = FakeTaskService()
        session = self.service.create_session(
            "Build an onboarding flow, write the copy, and test the signup path."
        )
        approved = self.service.approve_session(session)

        project = self.service.materialize_session(approved, project_service, task_service)

        self.assertEqual(project.id, 42)
        self.assertEqual(len(project_service.created), 1)
        self.assertLessEqual(len(project_service.created[0][0].split()), 3)
        self.assertLessEqual(len(project_service.created[0][1]), 120)
        self.assertNotIn("Build an onboarding flow", project_service.created[0][1])
        self.assertGreaterEqual(len(task_service.created), 1)
        self.assertTrue(all(len(title.split()) <= 3 for _, title, _ in task_service.created))
        self.assertEqual(task_service.created[0][0], 42)


if __name__ == "__main__":
    unittest.main()
