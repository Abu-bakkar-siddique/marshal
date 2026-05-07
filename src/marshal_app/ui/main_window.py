from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow, QMessageBox, QSplitter, QStackedWidget

from marshal_app.services import ServiceContainer
from marshal_app.ui.dialogs.project_dialog import ProjectDialog
from marshal_app.ui.dialogs.task_dialog import TaskDialog
from marshal_app.ui.project_view import ProjectView
from marshal_app.ui.sidebar import Sidebar
from marshal_app.ui.standalone_view import StandaloneView
from marshal_app.ui.theme.styles import APP_STYLE_SHEET


class MainWindow(QMainWindow):
    def __init__(self, services: ServiceContainer) -> None:
        super().__init__()
        self.services = services
        self.selected_project_id: int | None = None

        self.setWindowTitle("marshal")
        self.resize(1280, 820)
        self.setStyleSheet(APP_STYLE_SHEET)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(1)

        self.sidebar = Sidebar(self)
        self.content_stack = QStackedWidget(self)
        self.project_view = ProjectView(self)
        self.standalone_view = StandaloneView(self)

        self.content_stack.addWidget(self.project_view)
        self.content_stack.addWidget(self.standalone_view)

        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.content_stack)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([280, 1000])

        self.setCentralWidget(splitter)
        self.focus_queue_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.focus_queue_shortcut.activated.connect(self._focus_project_queue)
        self.move_mode_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        self.move_mode_shortcut.activated.connect(self._toggle_queue_move_mode)
        self._connect_signals()
        self._refresh_projects()

    def _connect_signals(self) -> None:
        self.sidebar.add_project_button.clicked.connect(self._create_project)
        self.sidebar.standalone_button.clicked.connect(self._show_standalone_view)
        self.sidebar.project_list.itemSelectionChanged.connect(self._handle_project_selection)
        self.project_view.add_task_button.clicked.connect(self._create_task)
        self.project_view.queue_reordered.connect(self._reorder_project_tasks)

    def _refresh_projects(self) -> None:
        projects = self.services.project_service.list_projects()

        if self.selected_project_id is not None:
            known_ids = {project.id for project in projects}
            if self.selected_project_id not in known_ids:
                self.selected_project_id = None

        if self.selected_project_id is None and projects:
            self.selected_project_id = projects[0].id

        self.sidebar.set_projects(projects, self.selected_project_id)
        self._refresh_active_view()

    def _refresh_active_view(self) -> None:
        if self.selected_project_id is None:
            self.content_stack.setCurrentWidget(self.project_view)
            self.project_view.set_project(None, [], None)
            return

        project = self.services.project_service.get_project(self.selected_project_id)
        if project is None:
            self.selected_project_id = None
            self._refresh_projects()
            return

        tasks = self.services.task_service.list_project_tasks(project.id)
        active_task = self.services.task_service.active_task_for_project(project.id)
        done, total, percentage = self.services.progress_service.progress_for_tasks(tasks)
        cards = self.project_view.set_project(
            project,
            tasks,
            active_task.id if active_task else None,
        )
        self.project_view.progress_header.set_progress(done, total, percentage)
        for card in cards:
            card.toggled.connect(self._set_task_done_state)
            card.delete_requested.connect(self._delete_task)
        self.content_stack.setCurrentWidget(self.project_view)

    def _handle_project_selection(self) -> None:
        item = self.sidebar.project_list.currentItem()
        if item is None:
            return
        project_id = item.data(Qt.ItemDataRole.UserRole)
        if project_id is None:
            return
        self.selected_project_id = int(project_id)
        self._refresh_active_view()

    def _create_project(self) -> None:
        dialog = ProjectDialog(self)
        if dialog.exec() == ProjectDialog.DialogCode.Accepted:
            project = self.services.project_service.create_project(
                dialog.title,
                dialog.description,
            )
            self.selected_project_id = project.id
            self._refresh_projects()

    def _create_task(self) -> None:
        if self.selected_project_id is None:
            return
        dialog = TaskDialog(self)
        if dialog.exec() == TaskDialog.DialogCode.Accepted:
            self.services.task_service.create_task_for_project(
                self.selected_project_id,
                dialog.title,
                dialog.comments,
            )
            self._refresh_active_view()

    def _set_task_done_state(self, task_id: int, is_done: bool) -> None:
        self.services.task_service.set_done_state(task_id, is_done)
        self._refresh_active_view()

    def _delete_task(self, task_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Delete task",
            "Delete this task from the project?",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.services.task_service.delete_task(task_id)
        self._refresh_active_view()

    def _reorder_project_tasks(self, ordered_task_ids: list[int]) -> None:
        if self.selected_project_id is None:
            return
        self.services.task_service.reorder_project_tasks(
            self.selected_project_id,
            ordered_task_ids,
        )
        self._refresh_active_view()

    def _show_standalone_view(self) -> None:
        self.sidebar.project_list.clearSelection()
        self.selected_project_id = None
        self.content_stack.setCurrentWidget(self.standalone_view)

    def _focus_project_queue(self) -> None:
        if self.content_stack.currentWidget() is not self.project_view:
            return
        self.project_view.focus_queue()

    def _toggle_queue_move_mode(self) -> None:
        if self.content_stack.currentWidget() is not self.project_view:
            return
        self.project_view.toggle_queue_move_mode()
