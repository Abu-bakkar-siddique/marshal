from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EmptyState(QWidget):
    def __init__(self, title: str, message: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        title_label = QLabel(title, self)
        title_label.setObjectName("EmptyStateTitle")

        message_label = QLabel(message, self)
        message_label.setObjectName("EmptyStateMessage")
        message_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(title_label)
        layout.addWidget(message_label)
