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

from marshal_app.domain.models import Project, Task
from marshal_app.ui.widgets.completed_panel import CompletedPanel
from marshal_app.ui.widgets.empty_state import EmptyState
from marshal_app.ui.widgets.progress_header import ProgressHeader
from marshal_app.ui.widgets.task_card import TaskCard
from marshal_app.ui.widgets.task_list_widget import TaskListWidget


class ProjectView(QWidget):
    queue_reordered = Signal(list)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ProjectView")

        self.eyebrow = QLabel("Project queue", self)
        self.eyebrow.setObjectName("Eyebrow")
        self.eyebrow.setVisible(False)

        self.title = QLabel("Select or create a project", self)
        self.title.setObjectName("ProjectTitle")

        self.subtitle = QLabel(
            "The first incomplete task will become active automatically.",
            self,
        )
        self.subtitle.setObjectName("ProjectSubtitle")
        self.subtitle.setWordWrap(True)
        self.subtitle.setVisible(False)

        self.add_task_button = QPushButton("new task", self)
        self.add_task_button.setObjectName("AddTaskButton")
        self.add_task_button.setEnabled(False)

        self.jump_to_completed_button = QPushButton("completed", self)
        self.jump_to_completed_button.setObjectName("SecondaryActionButton")
        self.jump_to_completed_button.setEnabled(False)
        self.jump_to_completed_button.clicked.connect(self.scroll_to_completed)
        self.jump_to_completed_button.setVisible(False)

        self.fullscreen_button = QPushButton("⛶", self)
        self.fullscreen_button.setObjectName("IconButton")
        self.fullscreen_button.setToolTip("Toggle fullscreen")
        self.fullscreen_button.setFixedSize(24, 24)

        self.progress_header = ProgressHeader(self)
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
        header_layout.addWidget(self.progress_header)
        header_layout.addWidget(self.subtitle)
        header_layout.addWidget(self.jump_to_completed_button)

        self.empty_state = EmptyState(
            "No project selected",
            "Create a project from the sidebar to start building an ordered queue.",
            self,
        )

        self.queue_label = QLabel("queue", self)
        self.queue_label.setObjectName("SectionTitle")
        self.queue_label.setVisible(False)

        self.queue_empty_state = EmptyState(
            "No tasks yet",
            "Add the first task to start the project queue.",
            self,
        )

        self.queue_complete_state = EmptyState(
            "Queue complete",
            "Every task in this project is done. You can still add more unless the project is closed.",
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
        self.content_layout.addWidget(self.queue_label)
        self.content_layout.addWidget(self.queue_empty_state)
        self.content_layout.addWidget(self.queue_complete_state)
        self.content_layout.addWidget(self.queue_list)
        self.content_layout.addWidget(self.completed_panel)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setWidget(content)

        self.add_row = QFrame(self)
        self.add_row.setObjectName("AddRow")
        add_layout = QVBoxLayout(self.add_row)
        add_layout.setContentsMargins(22, 8, 22, 8)
        add_layout.setSpacing(0)
        add_layout.addWidget(self.add_task_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.eyebrow)
        layout.addWidget(self.header)
        layout.addWidget(self.scroll_area, stretch=1)
        layout.addWidget(self.add_row)

        self.set_project(None, [], None)

    def set_project(
        self,
        project: Project | None,
        tasks: list[Task],
        active_task_id: int | None,
    ) -> list[TaskCard]:
        self.queue_list.clear()
        for layout in (self.completed_panel.content_layout,):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        if project is None:
            self.title.setText("Select or create a project")
            self.subtitle.clear()
            self.subtitle.setVisible(False)
            self.progress_header.set_progress(0, 0, 0)
            self.add_task_button.setEnabled(False)
            self.add_row.setVisible(False)
            self.jump_to_completed_button.setEnabled(False)
            self.empty_state.setVisible(True)
            self.queue_label.setVisible(False)
            self.queue_empty_state.setVisible(False)
            self.queue_complete_state.setVisible(False)
            self.queue_list.setVisible(False)
            self.completed_panel.setVisible(False)
            return []

        self.title.setText(project.title)
        description = project.description.strip()
        self.subtitle.setText(description)
        self.subtitle.setVisible(bool(description))
        incomplete_tasks = [task for task in tasks if not task.is_done]
        complete_tasks = [task for task in tasks if task.is_done]
        self.add_task_button.setEnabled(not project.is_closed)
        self.add_row.setVisible(True)
        self.jump_to_completed_button.setEnabled(bool(complete_tasks))
        self.empty_state.setVisible(False)
        self.queue_label.setVisible(False)
        self.completed_panel.setVisible(True)
        queued_cards = self.queue_list.set_tasks(incomplete_tasks, active_task_id)
        self.queue_list.setDragEnabled(len(incomplete_tasks) > 1)
        self.queue_empty_state.setVisible(False)
        self.queue_complete_state.setVisible(False)
        self.queue_list.setVisible(True)

        if not tasks:
            self.queue_list.setVisible(False)
            self.queue_empty_state.setVisible(True)
        elif not incomplete_tasks:
            self.queue_list.setVisible(False)
            self.queue_complete_state.setVisible(True)

        completed_cards: list[TaskCard] = []
        for task in complete_tasks:
            card = TaskCard(task, is_active=False, parent=self.completed_panel.content)
            self.completed_panel.content_layout.addWidget(card)
            completed_cards.append(card)

        if not complete_tasks:
            self.completed_panel.content_layout.addWidget(
                EmptyState(
                    "Nothing completed yet",
                    "Checked tasks will move here automatically.",
                    self.completed_panel.content,
                )
            )

        return queued_cards + completed_cards

    def scroll_to_completed(self) -> None:
        self.scroll_area.ensureWidgetVisible(self.completed_panel, 0, 48)

    def focus_queue(self) -> None:
        self.queue_list.focus_queue()

    def toggle_queue_move_mode(self) -> None:
        self.queue_list.toggle_move_mode()
