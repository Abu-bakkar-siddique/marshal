from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from marshal_app.domain.models import Task


class TaskCard(QFrame):
    toggled = Signal(int, bool)
    delete_requested = Signal(int)

    def __init__(
        self,
        task: Task,
        *,
        is_active: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("TaskCard")
        self.setProperty("active", is_active)
        self.setProperty("done", task.is_done)
        self.setProperty("keyboardSelected", False)
        self.setProperty("moveMode", False)
        self.task_id = task.id
        self.is_done = task.is_done

        self.checkbox = QCheckBox(self)
        self.checkbox.setChecked(task.is_done)
        self.checkbox.toggled.connect(self._emit_toggled)

        self.title_label = QLabel(task.title, self)
        self.title_label.setObjectName("TaskTitle")

        self.state_label = QLabel("ACTIVE" if is_active else "DONE" if task.is_done else "QUEUE", self)
        self.state_label.setObjectName("TaskState")
        self.state_label.setProperty(
            "stateKind",
            "active" if is_active else "done" if task.is_done else "queue",
        )
        self.state_label.setVisible(is_active)

        self.delete_button = QPushButton("delete", self)
        self.delete_button.setObjectName("CardActionButton")
        self.delete_button.clicked.connect(self._emit_delete_requested)

        self.detail_label = QLabel(task.comments, self)
        self.detail_label.setObjectName("TaskDetail")
        self.detail_label.setWordWrap(True)
        self.detail_label.setVisible(bool(task.comments))

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        header_layout.addWidget(self.checkbox)
        header_layout.addWidget(self.title_label, stretch=1)
        header_layout.addWidget(self.state_label)
        header_layout.addWidget(self.delete_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        layout.addLayout(header_layout)
        layout.addWidget(self.detail_label)

    def _emit_toggled(self, checked: bool) -> None:
        if self.task_id is None:
            return
        self.toggled.emit(self.task_id, checked)

    def _emit_delete_requested(self) -> None:
        if self.task_id is None:
            return
        self.delete_requested.emit(self.task_id)

    def set_keyboard_state(self, *, selected: bool, move_mode: bool) -> None:
        self.setProperty("keyboardSelected", selected)
        self.setProperty("moveMode", move_mode)
        self.style().unpolish(self)
        self.style().polish(self)
