# !/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QModelIndex
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

    def keyPressEvent(self, event) -> None:
        if event.key() in [16777220, 16777221]:  # Enter / Return
            for i in range(self.count()):
                self.closePersistentEditor(self.item(i))
            event.accept()
            return
        super().keyPressEvent(event)
