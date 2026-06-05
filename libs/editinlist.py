# !/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QEvent, QModelIndex
from PyQt5.QtWidgets import QListWidget


class EditInList(QListWidget):
    def __init__(self):
        super(EditInList, self).__init__()
        self.edited_item = None

    def item_clicked(self, modelindex: QModelIndex):
        try:
            if self.edited_item is not None:
                self.closePersistentEditor(self.edited_item)
        except Exception:
            self.edited_item = self.currentItem()

        self.edited_item = self.item(modelindex.row())
        self.openPersistentEditor(self.edited_item)
        self.editItem(self.edited_item)

    def mouseDoubleClickEvent(self, event):
        pass

    def leaveEvent(self, event):
        pass

    def activate_edit(self):
        """Open persistent editor for the currently selected item (called by F2)."""
        item = self.currentItem()
        if item is None:
            return
        if self.edited_item is not None:
            try:
                self.closePersistentEditor(self.edited_item)
            except Exception:
                pass
        self.edited_item = item
        self.openPersistentEditor(item)
        self.editItem(item)
        # Intercept Tab/Shift+Tab inside the editor widget before QLineEdit consumes them
        editor = self.indexWidget(self.indexFromItem(item))
        if editor is not None:
            editor.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == 16777217:  # Tab: save, move to next, open editor
                self._close_editors()
                next_row = self.currentRow() + 1
                if next_row < self.count():
                    self.setCurrentRow(next_row)
                    self.scrollToItem(self.item(next_row))
                    self.activate_edit()
                return True
            if (
                key == 16777218
            ):  # Shift+Tab / Backtab: save, move to previous, open editor
                self._close_editors()
                prev_row = self.currentRow() - 1
                if prev_row >= 0:
                    self.setCurrentRow(prev_row)
                    self.scrollToItem(self.item(prev_row))
                    self.activate_edit()
                return True
        return super().eventFilter(obj, event)

    def _close_editors(self):
        for i in range(self.count()):
            self.closePersistentEditor(self.item(i))
        self.edited_item = None

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key in (16777220, 16777221):  # Enter / Return: save and move to next
            self._close_editors()
            next_row = self.currentRow() + 1
            if next_row < self.count():
                self.setCurrentRow(next_row)
                self.scrollToItem(self.item(next_row))
            event.accept()
            return
        super().keyPressEvent(event)
