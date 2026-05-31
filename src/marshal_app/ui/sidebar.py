from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from marshal_app.domain.models import Project


class Sidebar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")

        title = QLabel("marshal", self)
        title.setObjectName("SidebarTitle")

        project_label = QLabel("Projects", self)
        project_label.setObjectName("SidebarSectionLabel")

        self.project_list = QListWidget(self)
        self.project_list.setObjectName("ProjectList")

        self.planner_button = QPushButton("plan", self)
        self.planner_button.setObjectName("SidebarActionButton")
        self.add_project_button = QPushButton("new project", self)
        self.add_project_button.setObjectName("SidebarActionButton")
        self.standalone_button = QPushButton("standalone", self)
        self.standalone_button.setObjectName("SidebarActionButton")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 12)
        layout.setSpacing(0)
        layout.addWidget(title)
        layout.addWidget(project_label)
        layout.addWidget(self.project_list, stretch=1)
        layout.addWidget(self.planner_button)
        layout.addWidget(self.standalone_button)
        layout.addWidget(self.add_project_button)

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
