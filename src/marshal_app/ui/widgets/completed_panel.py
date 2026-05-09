from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class CompletedPanel(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        left_line = QFrame(self)
        left_line.setObjectName("SectionLine")
        left_line.setFrameShape(QFrame.Shape.HLine)

        self.title = QLabel("Completed", self)
        self.title.setObjectName("SectionDividerTitle")

        right_line = QFrame(self)
        right_line.setObjectName("SectionLine")
        right_line.setFrameShape(QFrame.Shape.HLine)

        divider = QHBoxLayout()
        divider.setContentsMargins(22, 10, 22, 4)
        divider.setSpacing(10)
        divider.addWidget(left_line)
        divider.addWidget(self.title)
        divider.addWidget(right_line)

        self.content = QWidget(self)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(divider)
        layout.addWidget(self.content)
