from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem, QSizePolicy, QWidget

from marshal_app.domain.models import Task
from marshal_app.ui.widgets.task_card import TaskCard


class TaskListWidget(QListWidget):
    order_changed = Signal(list)

    def __init__(self, *, reorderable: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._reorderable = reorderable
        self._move_mode = False
        self.setObjectName("TaskListWidget")
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSpacing(0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        self.setSizeAdjustPolicy(QAbstractItemView.SizeAdjustPolicy.AdjustToContents)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.currentItemChanged.connect(lambda *_: self._sync_card_states())

    def set_tasks(self, tasks: list[Task], active_task_id: int | None = None) -> list[TaskCard]:
        self.clear()
        self._move_mode = False
        cards: list[TaskCard] = []
        for task in tasks:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, task.id)
            card = TaskCard(task, is_active=(task.id == active_task_id), parent=self)
            item.setSizeHint(card.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, card)
            cards.append(card)
        if self.count():
            self.setCurrentRow(0)
        self._sync_card_states()
        self.sync_to_contents()
        return cards

    def task_ids_in_order(self) -> list[int]:
        task_ids: list[int] = []
        for index in range(self.count()):
            item = self.item(index)
            task_id = item.data(Qt.ItemDataRole.UserRole)
            if task_id is not None:
                task_ids.append(int(task_id))
        return task_ids

    def focus_queue(self) -> None:
        if self.count() and self.currentRow() < 0:
            self.setCurrentRow(0)
        self.setFocus(Qt.FocusReason.ShortcutFocusReason)
        self._sync_card_states()

    def toggle_move_mode(self) -> None:
        if not self._reorderable or self.count() < 2:
            return
        if self.currentRow() < 0:
            self.setCurrentRow(0)
        self._move_mode = not self._move_mode
        self._sync_card_states()

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_D:
            self.toggle_move_mode()
            event.accept()
            return

        if event.key() == Qt.Key.Key_Escape and self._move_mode:
            self._move_mode = False
            self._sync_card_states()
            event.accept()
            return

        if self._move_mode and event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            delta = -1 if event.key() == Qt.Key.Key_Up else 1
            self._move_current_item(delta)
            event.accept()
            return

        super().keyPressEvent(event)
        self._sync_card_states()

    def focusOutEvent(self, event) -> None:  # type: ignore[override]
        self._move_mode = False
        self._sync_card_states()
        super().focusOutEvent(event)

    def _move_current_item(self, delta: int) -> None:
        current_row = self.currentRow()
        if current_row < 0:
            return

        target_row = current_row + delta
        if target_row < 0 or target_row >= self.count():
            return

        item = self.item(current_row)
        if item is None:
            return

        widget = self.itemWidget(item)
        self.removeItemWidget(item)
        item = self.takeItem(current_row)
        self.insertItem(target_row, item)
        if widget is not None:
            self.setItemWidget(item, widget)
        self.setCurrentRow(target_row)
        self._sync_card_states()
        self.order_changed.emit(self.task_ids_in_order())

    def _sync_card_states(self) -> None:
        current_row = self.currentRow()
        has_focus = self.hasFocus()
        for index in range(self.count()):
            item = self.item(index)
            card = self.itemWidget(item)
            if isinstance(card, TaskCard):
                is_selected = has_focus and index == current_row
                card.set_keyboard_state(
                    selected=is_selected,
                    move_mode=is_selected and self._move_mode,
                )

    def sync_to_contents(self) -> None:
        frame = self.frameWidth() * 2
        total_height = frame
        if self.count() == 0:
            total_height += 2
        else:
            for index in range(self.count()):
                total_height += self.sizeHintForRow(index)
            total_height += max(0, self.count() - 1) * self.spacing()
        total_height += 4
        self.setFixedHeight(total_height)
