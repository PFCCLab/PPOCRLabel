# !/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QEvent, QModelIndex
from PyQt5.QtWidgets import QApplication, QLineEdit, QListWidget


class EditInList(QListWidget):
    def __init__(self):
        super(EditInList, self).__init__()
        self.edited_item = None
        self._app_filter_active = False

    def item_clicked(self, modelindex: QModelIndex):
        try:
            if self.edited_item is not None:
                self.closePersistentEditor(self.edited_item)
        except Exception:
            self.edited_item = self.currentItem()

        self.edited_item = self.item(modelindex.row())
        self.openPersistentEditor(self.edited_item)
        self.editItem(self.edited_item)
        self._install_app_filter()

    def mouseDoubleClickEvent(self, event):
        pass

    def leaveEvent(self, event):
        pass

    def activate_edit(self):
        """Open persistent editor for the currently selected item (called by F2/Tab)."""
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
        self._install_app_filter()

    def _install_app_filter(self):
        if not self._app_filter_active:
            QApplication.instance().installEventFilter(self)
            self._app_filter_active = True

    def _remove_app_filter(self):
        if self._app_filter_active:
            QApplication.instance().removeEventFilter(self)
            self._app_filter_active = False

    def _editor_text(self):
        """Return current text from whichever QLineEdit child is visible."""
        for child in self.findChildren(QLineEdit):
            if child.isVisible():
                return child.text()
        return None

    def _save_and_close(self):
        """Write editor text back to the item, then close all editors."""
        if self.edited_item is not None:
            text = self._editor_text()
            if text is not None:
                self.edited_item.setText(text)
        self._remove_app_filter()
        for i in range(self.count()):
            self.closePersistentEditor(self.item(i))
        self.edited_item = None

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            focused = QApplication.focusWidget()
            # Only act when the focused widget is inside this list
            if focused is not None and self.isAncestorOf(focused):
                key = event.key()
                if key == 16777217:  # Tab: save, move to next, open editor
                    self._save_and_close()
                    next_row = self.currentRow() + 1
                    if next_row < self.count():
                        self.setCurrentRow(next_row)
                        self.scrollToItem(self.item(next_row))
                        self.activate_edit()
                    return True
                if key == 16777218:  # Shift+Tab: save, move to previous, open editor
                    self._save_and_close()
                    prev_row = self.currentRow() - 1
                    if prev_row >= 0:
                        self.setCurrentRow(prev_row)
                        self.scrollToItem(self.item(prev_row))
                        self.activate_edit()
                    return True
        return False

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key in (16777220, 16777221):  # Enter / Return: save and move to next
            self._save_and_close()
            next_row = self.currentRow() + 1
            if next_row < self.count():
                self.setCurrentRow(next_row)
                self.scrollToItem(self.item(next_row))
            event.accept()
            return
        if key == 16777217:  # Tab with no editor open: just navigate
            next_row = self.currentRow() + 1
            if next_row < self.count():
                self.setCurrentRow(next_row)
                self.scrollToItem(self.item(next_row))
            event.accept()
            return
        if key == 16777218:  # Shift+Tab with no editor open: navigate back
            prev_row = self.currentRow() - 1
            if prev_row >= 0:
                self.setCurrentRow(prev_row)
                self.scrollToItem(self.item(prev_row))
            event.accept()
            return
        super().keyPressEvent(event)
