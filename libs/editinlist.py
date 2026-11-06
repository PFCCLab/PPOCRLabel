# !/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QModelIndex, QEvent, Qt, pyqtSignal
from PyQt5.QtWidgets import QAbstractItemView, QLineEdit, QListWidget


class EditInList(QListWidget):
    navigateRequested = pyqtSignal(int)
    editRequested = pyqtSignal()

    def __init__(self):
        super(EditInList, self).__init__()
        self.edited_item = None
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def _close_editors(self):
        for i in range(self.count()):
            self.closePersistentEditor(self.item(i))
        self.edited_item = None

    def _commit_editor(self, editor):
        item = self.currentItem()
        if item is not None and editor is not None:
            item.setText(editor.text())
        self._close_editors()
        self.setFocus()

    def open_editor(self, item=None):
        if item is None:
            item = self.currentItem()
        if item is None:
            return
        self._close_editors()
        self.edited_item = item
        self.setCurrentItem(item)
        self.openPersistentEditor(item)
        for editor in self.viewport().findChildren(QLineEdit):
            editor.installEventFilter(self)
            editor.setFocus()

    def item_clicked(self, modelindex: QModelIndex):
        self.open_editor(self.item(modelindex.row()))

    def focusNextPrevChild(self, next):
        # Keep Tab/Shift+Tab inside the list so they can cycle through boxes.
        if self.count() > 0:
            return False
        return super(EditInList, self).focusNextPrevChild(next)

    def eventFilter(self, obj, event):
        if isinstance(obj, QLineEdit) and event.type() == QEvent.KeyPress:
            key = event.key()
            if key in (Qt.Key_Tab, Qt.Key_Backtab):
                self._commit_editor(obj)
                step = (
                    -1
                    if key == Qt.Key_Backtab
                    or event.modifiers() & Qt.ShiftModifier
                    else 1
                )
                self.navigateRequested.emit(step)
                return True
            if key in (Qt.Key_Escape, Qt.Key_Return, Qt.Key_Enter):
                # Confirm the edit and go back to box navigation mode.
                self._commit_editor(obj)
                return True
        return super(EditInList, self).eventFilter(obj, event)

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key in (Qt.Key_Tab, Qt.Key_Backtab):
            step = (
                -1
                if key == Qt.Key_Backtab or event.modifiers() & Qt.ShiftModifier
                else 1
            )
            self.navigateRequested.emit(step)
            event.accept()
            return
        if key in (Qt.Key_F2, Qt.Key_Return, Qt.Key_Enter):
            self.editRequested.emit()
            event.accept()
            return
        if key == Qt.Key_Escape:
            self._close_editors()
            event.accept()
            return
        super(EditInList, self).keyPressEvent(event)
