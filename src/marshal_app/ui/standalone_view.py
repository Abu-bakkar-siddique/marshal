from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from marshal_app.domain.models import Task
from marshal_app.ui.widgets.completed_panel import CompletedPanel
from marshal_app.ui.widgets.empty_state import EmptyState
from marshal_app.ui.widgets.task_card import TaskCard
from marshal_app.ui.widgets.task_list_widget import TaskListWidget


class StandaloneView(QWidget):
    queue_reordered = Signal(list)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ProjectView")

        self.title = QLabel("Standalone tasks", self)
        self.title.setObjectName("ProjectTitle")

        self.subtitle = QLabel(
            "Flexible tasks that are not attached to a project queue.",
            self,
        )
        self.subtitle.setObjectName("ProjectSubtitle")
        self.subtitle.setWordWrap(True)

        self.fullscreen_button = QPushButton("⛶", self)
        self.fullscreen_button.setObjectName("IconButton")
        self.fullscreen_button.setToolTip("Toggle fullscreen")
        self.fullscreen_button.setFixedSize(24, 24)

        self.header = QFrame(self)
        self.header.setObjectName("ProjectHeader")
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(10)
        title_row.addWidget(self.title, stretch=1)
        title_row.addWidget(self.fullscreen_button)

        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(22, 18, 22, 14)
        header_layout.setSpacing(10)
        header_layout.addLayout(title_row)
        header_layout.addWidget(self.subtitle)

        self.empty_state = EmptyState(
            "No standalone tasks yet",
            "Add quick tasks here when they do not belong inside a project.",
            self,
        )

        self.queue_list = TaskListWidget(reorderable=True, parent=self)
        self.queue_list.order_changed.connect(self.queue_reordered.emit)

        self.completed_panel = CompletedPanel(self)

        content = QWidget(self)
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_layout.addWidget(self.empty_state)
        self.content_layout.addWidget(self.queue_list)
        self.content_layout.addWidget(self.completed_panel)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setWidget(content)

        self.add_task_button = QPushButton("new standalone task", self)
        self.add_task_button.setObjectName("AddTaskButton")

        self.add_row = QFrame(self)
        self.add_row.setObjectName("AddRow")
        add_layout = QVBoxLayout(self.add_row)
        add_layout.setContentsMargins(22, 8, 22, 8)
        add_layout.setSpacing(0)
        add_layout.addWidget(self.add_task_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.header)
        layout.addWidget(self.scroll_area, stretch=1)
        layout.addWidget(self.add_row)

    def set_tasks(self, tasks: list[Task]) -> list[TaskCard]:
        self.queue_list.clear()
        while self.completed_panel.content_layout.count():
            item = self.completed_panel.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        incomplete_tasks = [task for task in tasks if not task.is_done]
        complete_tasks = [task for task in tasks if task.is_done]

        self.empty_state.setVisible(not tasks)
        queued_cards = self.queue_list.set_tasks(incomplete_tasks, active_task_id=None)
        self.queue_list.setDragEnabled(len(incomplete_tasks) > 1)
        self.queue_list.setVisible(bool(incomplete_tasks))
        self.completed_panel.setVisible(bool(tasks))

        completed_cards: list[TaskCard] = []
        for task in complete_tasks:
            card = TaskCard(task, is_active=False, parent=self.completed_panel.content)
            self.completed_panel.content_layout.addWidget(card)
            completed_cards.append(card)

        if tasks and not complete_tasks:
            self.completed_panel.content_layout.addWidget(
                EmptyState(
                    "Nothing completed yet",
                    "Checked standalone tasks will move here automatically.",
                    self.completed_panel.content,
                )
            )

        return queued_cards + completed_cards

    def focus_queue(self) -> None:
        self.queue_list.focus_queue()

    def toggle_queue_move_mode(self) -> None:
        self.queue_list.toggle_move_mode()
