from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QTextCursor

from marshal_app.domain.enums import PlanningPhase
from marshal_app.services.planning_service import PlanningSession, PlanningService


class PlanningView(QWidget):
    accepted = Signal(object)

    def __init__(self, planning_service: PlanningService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("PlanningView")
        self._planning_service = planning_service
        self._session: PlanningSession | None = None

        self.title = QLabel("AI planner", self)
        self.title.setObjectName("PlanningTitle")

        self.status_label = QLabel("Type a goal and press send.", self)
        self.status_label.setObjectName("PlanningStatus")
        self.status_label.setWordWrap(True)

        self.transcript = QPlainTextEdit(self)
        self.transcript.setObjectName("PlanningTranscript")
        self.transcript.setReadOnly(True)
        self.transcript.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.transcript.setPlaceholderText("The conversation will appear here.")
        self.transcript.setMinimumHeight(220)

        self.input_edit = QPlainTextEdit(self)
        self.input_edit.setObjectName("PlanningInput")
        self.input_edit.setPlaceholderText("Type a goal or a refinement...")
        self.input_edit.setFixedHeight(96)

        self.send_button = QPushButton("send", self)
        self.send_button.setObjectName("PrimaryActionButton")
        self.send_button.clicked.connect(self._send_message)

        self.accept_button = QPushButton("accept", self)
        self.accept_button.setObjectName("PrimaryActionButton")
        self.accept_button.clicked.connect(self._accept_plan)

        self.reset_button = QPushButton("clear", self)
        self.reset_button.setObjectName("SecondaryActionButton")
        self.reset_button.clicked.connect(self._reset_session)

        button_row = QWidget(self)
        button_row_layout = QHBoxLayout(button_row)
        button_row_layout.setContentsMargins(0, 0, 0, 0)
        button_row_layout.setSpacing(8)
        button_row_layout.addWidget(self.send_button)
        button_row_layout.addWidget(self.accept_button)
        button_row_layout.addWidget(self.reset_button)
        button_row_layout.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)
        layout.addWidget(self.title)
        layout.addWidget(self.status_label)
        layout.addWidget(self.transcript, stretch=1)
        layout.addWidget(self.input_edit)
        layout.addWidget(button_row)

        self._set_idle_state()

    def focus_input(self) -> None:
        self.input_edit.setFocus()

    def _set_idle_state(self) -> None:
        self._session = None
        self.status_label.setText("Type a goal and press send.")
        self.transcript.clear()
        self.input_edit.clear()
        self.accept_button.setEnabled(False)

    def _send_message(self) -> None:
        text = self.input_edit.toPlainText().strip()
        if not text:
            self.status_label.setText("Type something first.")
            self.input_edit.setFocus()
            return

        if self._session is None or self._session.phase == PlanningPhase.APPROVED:
            self._session = self._planning_service.create_session(text)
        else:
            self._session = self._planning_service.revise_session(self._session, text)

        self._render_session()
        self.input_edit.clear()
        self.input_edit.setFocus()

    def _accept_plan(self) -> None:
        if self._session is None:
            self.status_label.setText("Generate a draft first.")
            return

        self._session = self._planning_service.approve_session(self._session)
        self._render_session()
        self.accept_button.setEnabled(False)
        self.accepted.emit(self._session)

    def _reset_session(self) -> None:
        self._set_idle_state()
        self.input_edit.setFocus()

    def _render_session(self) -> None:
        if self._session is None:
            self._set_idle_state()
            return

        self.transcript.setPlainText(self._planning_service.render_transcript_text(self._session))
        self.transcript.moveCursor(QTextCursor.MoveOperation.End)

        if self._session.phase == PlanningPhase.APPROVED:
            self.status_label.setText("Accepted. The plan is now saved to a project.")
            self.accept_button.setEnabled(False)
        else:
            status = "Draft ready. Refine it or accept it."
            if self._session.clarification_question:
                status = f"{status} {self._session.clarification_question}"
            self.status_label.setText(status)
            self.accept_button.setEnabled(bool(self._session.tentative_tasks))
