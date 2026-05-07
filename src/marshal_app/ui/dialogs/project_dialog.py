from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)


class ProjectDialog(QDialog):
    def __init__(self, parent: QDialog | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New project")
        self.resize(440, 260)

        title_label = QLabel("Project title", self)
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("What are you trying to accomplish?")

        description_label = QLabel("Description", self)
        self.description_input = QTextEdit(self)
        self.description_input.setPlaceholderText("Optional context for this project")

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
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)
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
    def description(self) -> str:
        return self.description_input.toPlainText().strip()
