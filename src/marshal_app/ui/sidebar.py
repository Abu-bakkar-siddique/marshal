from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from marshal_app.domain.models import Project


class Sidebar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        title = QLabel("marshal", self)
        title.setObjectName("SidebarTitle")

        subtitle = QLabel("Projects and standalone tasks", self)
        subtitle.setObjectName("SidebarSubtitle")
        subtitle.setVisible(False)

        self.project_list = QListWidget(self)
        self.project_list.setObjectName("ProjectList")

        self.add_project_button = QPushButton("new project", self)
        self.standalone_button = QPushButton("standalone", self)

        button_row = QHBoxLayout()
        button_row.addWidget(self.add_project_button)
        button_row.addWidget(self.standalone_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(button_row)
        layout.addWidget(self.project_list, stretch=1)

    def set_projects(self, projects: list[Project], selected_project_id: int | None = None) -> None:
        self.project_list.blockSignals(True)
        self.project_list.clear()
        for project in projects:
            item = QListWidgetItem(project.title)
            item.setData(Qt.ItemDataRole.UserRole, project.id)
            self.project_list.addItem(item)
            if project.id == selected_project_id:
                self.project_list.setCurrentItem(item)
        self.project_list.blockSignals(False)
