from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QWidget


class ProgressHeader(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ProgressHeader")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.percentage_label = QLabel("0%", self)
        self.percentage_label.setObjectName("ProgressPercentage")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.progress_bar, stretch=1)
        layout.addWidget(self.percentage_label)

    def set_progress(self, done: int, total: int, percentage: int) -> None:
        self.percentage_label.setText(f"{percentage}%")
        self.progress_bar.setValue(percentage)
