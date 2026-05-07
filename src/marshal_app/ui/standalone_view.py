from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from marshal_app.ui.widgets.empty_state import EmptyState


class StandaloneView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        title = QLabel("Standalone tasks", self)
        title.setObjectName("ProjectTitle")

        subtitle = QLabel(
            "Standalone tasks are intentionally flexible and do not inherit the strict project queue rules.",
            self,
        )
        subtitle.setObjectName("ProjectSubtitle")
        subtitle.setWordWrap(True)

        empty_state = EmptyState(
            "No standalone tasks yet",
            "This area is scaffolded and ready for the task list implementation pass.",
            self,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(empty_state)
        layout.addStretch(1)
