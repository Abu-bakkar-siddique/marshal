from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from marshal_app.domain.enums import PlanningPhase
from marshal_app.services.planning_service import PlanningService, RuleBasedPlanningEngine


class PlanningServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = PlanningService(RuleBasedPlanningEngine())

    def test_creates_tentative_draft_before_structured_output(self) -> None:
        session = self.service.create_session(
            "Launch a landing page for the product and collect early signups."
        )

        self.assertGreaterEqual(len(session.tentative_tasks), 1)
        self.assertEqual(session.structured_tasks, [])
        self.assertFalse(self.service.render_structured_preview_text(session))
        self.assertIn("Tentative tasks", self.service.render_tentative_draft_text(session))

    def test_approval_turns_draft_into_structured_preview(self) -> None:
        session = self.service.create_session(
            "Build an onboarding flow, write the copy, and test the signup path."
        )
        approved = self.service.approve_session(session)

        self.assertEqual(approved.phase, PlanningPhase.APPROVED)
        self.assertEqual(len(approved.structured_tasks), len(session.tentative_tasks))
        self.assertTrue(self.service.render_structured_preview_text(approved))

    def test_revise_session_increments_revision_count(self) -> None:
        session = self.service.create_session("Ship a prototype")
        revised = self.service.revise_session(session, "Split it into UI, backend, and testing work.")

        self.assertEqual(revised.revision_count, session.revision_count + 1)
        self.assertGreater(len(revised.tentative_tasks), 0)
        self.assertGreater(len(revised.transcript), len(session.transcript))


if __name__ == "__main__":
    unittest.main()
