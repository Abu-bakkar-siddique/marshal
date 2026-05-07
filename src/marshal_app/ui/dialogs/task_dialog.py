from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)


class TaskDialog(QDialog):
    def __init__(self, parent: QDialog | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New task")
        self.resize(440, 280)

        title_label = QLabel("Task title", self)
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Write the next concrete task")

        comments_label = QLabel("Comments", self)
        self.comments_input = QTextEdit(self)
        self.comments_input.setPlaceholderText("Optional details that do not fit in the title")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)
        layout.addWidget(comments_label)
        layout.addWidget(self.comments_input)
        layout.addWidget(buttons)

    def accept(self) -> None:
        if self.title.strip():
            super().accept()
            return
        self.title_input.setFocus()

    @property
    def title(self) -> str:
        return self.title_input.text().strip()

    @property
    def comments(self) -> str:
        return self.comments_input.toPlainText().strip()
