from __future__ import annotations

from PySide6.QtCore import QPointF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from marshal_app.domain.models import Task


class TaskCheckBox(QCheckBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(14, 14)

    def sizeHint(self) -> QSize:  # type: ignore[override]
        return QSize(14, 14)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        border = QColor(255, 255, 255, 38)
        fill = QColor("#e8e8e8") if self.isChecked() else QColor(0, 0, 0, 0)
        painter.setPen(QPen(QColor("#e8e8e8") if self.isChecked() else border, 1))
        painter.setBrush(fill)
        painter.drawEllipse(0.5, 0.5, 13, 13)

        if self.isChecked():
            pen = QPen(QColor("#1c1c1c"), 1.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(QPointF(4.0, 7.1), QPointF(6.0, 9.1))
            painter.drawLine(QPointF(6.0, 9.1), QPointF(10.2, 4.8))


class TaskCard(QFrame):
    toggled = Signal(int, bool)
    delete_requested = Signal(int)

    def __init__(
        self,
        task: Task,
        *,
        is_active: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("TaskCard")
        self.setProperty("active", is_active)
        self.setProperty("done", task.is_done)
        self.setProperty("keyboardSelected", False)
        self.setProperty("moveMode", False)
        self.setProperty("expanded", False)
        self.task_id = task.id
        self.is_done = task.is_done
        self._expanded = False

        self.checkbox = TaskCheckBox(self)
        self.checkbox.setObjectName("TaskCheck")
        self.checkbox.setChecked(task.is_done)
        self.checkbox.toggled.connect(self._emit_toggled)

        self.title_label = QLabel(task.title, self)
        self.title_label.setObjectName("TaskTitle")

        self.active_dot = QLabel("", self)
        self.active_dot.setObjectName("ActiveDot")
        self.active_dot.setFixedSize(5, 5)
        self.active_dot.setVisible(is_active)

        self.expand_label = QLabel("⌄", self)
        self.expand_label.setObjectName("ExpandButton")
        self.expand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.expand_label.setFixedWidth(14)

        self.delete_button = QPushButton("delete", self)
        self.delete_button.setObjectName("CardActionButton")
        self.delete_button.clicked.connect(self._emit_delete_requested)

        self.detail_label = QLabel(task.comments, self)
        self.detail_label.setObjectName("TaskDetail")
        self.detail_label.setWordWrap(True)
        self.detail_label.setVisible(bool(task.comments))

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        header_layout.addWidget(self.checkbox)
        header_layout.addWidget(self.title_label, stretch=1)
        header_layout.addWidget(self.active_dot)
        header_layout.addWidget(self.expand_label)
        header_layout.addWidget(self.delete_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 8, 22, 8)
        layout.setSpacing(0)
        layout.addLayout(header_layout)
        layout.addWidget(self.detail_label)
        self.detail_label.setVisible(False)

    def _emit_toggled(self, checked: bool) -> None:
        if self.task_id is None:
            return
        self.toggled.emit(self.task_id, checked)

    def _emit_delete_requested(self) -> None:
        if self.task_id is None:
            return
        self.delete_requested.emit(self.task_id)

    def set_keyboard_state(self, *, selected: bool, move_mode: bool) -> None:
        self.setProperty("keyboardSelected", selected)
        self.setProperty("moveMode", move_mode)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if child not in (self.checkbox, self.delete_button):
                self.toggle_expanded()
                event.accept()
                return
        super().mousePressEvent(event)

    def toggle_expanded(self) -> None:
        self._expanded = not self._expanded
        self.detail_label.setVisible(self._expanded and bool(self.detail_label.text().strip()))
        self.expand_label.setText("⌃" if self._expanded else "⌄")
        self.setProperty("expanded", self._expanded)
        self.style().unpolish(self)
        self.style().polish(self)
