from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from marshal_app.domain.enums import PlanningPhase
from marshal_app.services.planning_service import PlanningSession, PlanningService


class PlanningView(QWidget):
    def __init__(self, planning_service: PlanningService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("PlanningView")
        self._planning_service = planning_service
        self._session: PlanningSession | None = None

        self.title = QLabel("AI planner", self)
        self.title.setObjectName("PlanningTitle")

        self.subtitle = QLabel(
            "Draft a tentative task list from raw input, then confirm it with an explicit OK.",
            self,
        )
        self.subtitle.setObjectName("PlanningSubtitle")
        self.subtitle.setWordWrap(True)

        self.status_label = QLabel("Enter raw input to begin.", self)
        self.status_label.setObjectName("PlanningStatus")
        self.status_label.setWordWrap(True)

        header = QFrame(self)
        header.setObjectName("PlanningHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(22, 18, 22, 14)
        header_layout.setSpacing(8)
        header_layout.addWidget(self.title)
        header_layout.addWidget(self.subtitle)
        header_layout.addWidget(self.status_label)

        self.raw_input_label = QLabel("Raw input", self)
        self.raw_input_label.setObjectName("PlanningSectionTitle")
        self.raw_input_edit = QPlainTextEdit(self)
        self.raw_input_edit.setObjectName("PlanningInput")
        self.raw_input_edit.setPlaceholderText("Describe the goal in rough language.")
        self.raw_input_edit.setFixedHeight(108)

        self.feedback_label = QLabel("Revision notes", self)
        self.feedback_label.setObjectName("PlanningSectionTitle")
        self.feedback_edit = QPlainTextEdit(self)
        self.feedback_edit.setObjectName("PlanningFeedback")
        self.feedback_edit.setPlaceholderText("Tell the planner what to change, add, or separate.")
        self.feedback_edit.setFixedHeight(84)

        self.generate_button = QPushButton("generate draft", self)
        self.generate_button.setObjectName("PrimaryActionButton")
        self.generate_button.clicked.connect(self._generate_draft)

        self.refine_button = QPushButton("refine", self)
        self.refine_button.setObjectName("SecondaryActionButton")
        self.refine_button.clicked.connect(self._refine_draft)

        self.ok_button = QPushButton("OK", self)
        self.ok_button.setObjectName("PrimaryActionButton")
        self.ok_button.clicked.connect(self._approve_draft)

        self.reset_button = QPushButton("reset", self)
        self.reset_button.setObjectName("SecondaryActionButton")
        self.reset_button.clicked.connect(self._reset_session)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(10)
        action_row.addWidget(self.generate_button)
        action_row.addWidget(self.refine_button)
        action_row.addWidget(self.ok_button)
        action_row.addWidget(self.reset_button)
        action_row.addStretch(1)

        self.question_label = QLabel("", self)
        self.question_label.setObjectName("PlanningQuestion")
        self.question_label.setWordWrap(True)
        self.question_label.setVisible(False)

        self.conversation_label = QLabel("Conversation", self)
        self.conversation_label.setObjectName("PlanningSectionTitle")
        self.conversation_output = QPlainTextEdit(self)
        self.conversation_output.setObjectName("PlanningConversation")
        self.conversation_output.setReadOnly(True)
        self.conversation_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.conversation_output.setPlaceholderText("The draft conversation will appear here.")
        self.conversation_output.setFixedHeight(172)

        self.tentative_label = QLabel("Tentative draft", self)
        self.tentative_label.setObjectName("PlanningSectionTitle")
        self.tentative_output = QPlainTextEdit(self)
        self.tentative_output.setObjectName("PlanningDraft")
        self.tentative_output.setReadOnly(True)
        self.tentative_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.tentative_output.setPlaceholderText("A tentative task list will appear here.")
        self.tentative_output.setFixedHeight(182)

        self.structured_container = QWidget(self)
        structured_layout = QVBoxLayout(self.structured_container)
        structured_layout.setContentsMargins(0, 0, 0, 0)
        structured_layout.setSpacing(8)

        self.structured_label = QLabel("Structured output", self.structured_container)
        self.structured_label.setObjectName("PlanningSectionTitle")
        self.structured_output = QPlainTextEdit(self.structured_container)
        self.structured_output.setObjectName("PlanningStructured")
        self.structured_output.setReadOnly(True)
        self.structured_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.structured_output.setPlaceholderText("Structured tasks appear here after OK.")
        self.structured_output.setFixedHeight(182)
        structured_layout.addWidget(self.structured_label)
        structured_layout.addWidget(self.structured_output)

        content = QWidget(self)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(14)
        content_layout.addWidget(self.raw_input_label)
        content_layout.addWidget(self.raw_input_edit)
        content_layout.addLayout(action_row)
        content_layout.addWidget(self.feedback_label)
        content_layout.addWidget(self.feedback_edit)
        content_layout.addWidget(self.question_label)
        content_layout.addWidget(self.conversation_label)
        content_layout.addWidget(self.conversation_output)
        content_layout.addWidget(self.tentative_label)
        content_layout.addWidget(self.tentative_output)
        content_layout.addWidget(self.structured_container)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setWidget(content)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addWidget(self.scroll_area, stretch=1)

        self._set_idle_state()

    def focus_input(self) -> None:
        self.raw_input_edit.setFocus()

    def _set_idle_state(self) -> None:
        self._session = None
        self.status_label.setText("Enter raw input to begin.")
        self.question_label.setVisible(False)
        self.structured_output.clear()
        self.structured_container.setVisible(False)
        self.tentative_output.clear()
        self.conversation_output.clear()
        self.feedback_edit.clear()
        self.ok_button.setEnabled(False)
        self.refine_button.setEnabled(False)

    def _generate_draft(self) -> None:
        raw_input = self.raw_input_edit.toPlainText().strip()
        if not raw_input:
            self.status_label.setText("Add a goal first.")
            self.raw_input_edit.setFocus()
            return

        self._session = self._planning_service.create_session(raw_input)
        self._render_session(status_prefix="Draft generated.")

    def _refine_draft(self) -> None:
        if self._session is None:
            self.status_label.setText("Generate a draft first.")
            return

        feedback = self.feedback_edit.toPlainText().strip()
        if not feedback:
            self.status_label.setText("Add revision notes before refining.")
            self.feedback_edit.setFocus()
            return

        self._session = self._planning_service.revise_session(self._session, feedback)
        self._render_session(status_prefix="Draft refined.")

    def _approve_draft(self) -> None:
        if self._session is None:
            self.status_label.setText("Generate a draft first.")
            return

        self._session = self._planning_service.approve_session(self._session)
        self._render_session(status_prefix="OK signal received.")

    def _reset_session(self) -> None:
        self.raw_input_edit.clear()
        self._set_idle_state()

    def _render_session(self, *, status_prefix: str) -> None:
        if self._session is None:
            self._set_idle_state()
            return

        if self._session.phase == PlanningPhase.APPROVED:
            self.status_label.setText("OK signal received. Structured output is rendered below.")
        else:
            self.status_label.setText(
                f"{status_prefix} Review the tentative list before sending the OK signal."
            )
        self.question_label.setVisible(bool(self._session.clarification_question))
        if self._session.clarification_question:
            self.question_label.setText(f"Clarification: {self._session.clarification_question}")
        else:
            self.question_label.clear()

        self.conversation_output.setPlainText(
            self._planning_service.render_transcript_text(self._session)
        )
        self.tentative_output.setPlainText(
            self._planning_service.render_tentative_draft_text(self._session)
        )
        self.ok_button.setEnabled(bool(self._session.tentative_tasks))
        self.refine_button.setEnabled(True)

        if self._session.phase == PlanningPhase.APPROVED:
            self.structured_container.setVisible(True)
            self.structured_output.setPlainText(
                self._planning_service.render_structured_preview_text(self._session)
            )
        else:
            self.structured_container.setVisible(False)
            self.structured_output.clear()
