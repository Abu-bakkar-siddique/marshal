from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget


class ProgressHeader(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ProgressHeader")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.percentage_label = QLabel("0 of 0 done", self)
        self.percentage_label.setObjectName("ProgressPercentage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.percentage_label)

    def set_progress(self, done: int, total: int, percentage: int) -> None:
        self.percentage_label.setText(f"{done} of {total} done")
        self.progress_bar.setValue(percentage)
