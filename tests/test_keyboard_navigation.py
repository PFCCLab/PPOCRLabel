import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QLineEdit

from libs.editinlist import EditInList


class KeyboardNavigationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.list = EditInList()
        for text in ("one", "two", "three"):
            self.list.addItem(text)
        self.list.resize(300, 200)
        self.list.show()
        self.list.setCurrentRow(0)
        self.list.setFocus()
        self.app.processEvents()
        self.steps = []
        self.list.navigateRequested.connect(self.steps.append)
        self.list.editRequested.connect(self.list.open_editor)

    def tearDown(self):
        self.list.close()
        self.list.deleteLater()
        self.app.processEvents()

    def test_tab_and_shift_tab_emit_navigation_steps(self):
        QTest.keyClick(self.list, Qt.Key_Tab)
        self.app.processEvents()
        QTest.keyClick(self.list, Qt.Key_Backtab, Qt.ShiftModifier)
        self.app.processEvents()
        self.assertEqual(self.steps, [1, -1])

    def test_enter_opens_editor_and_confirms_text(self):
        QTest.keyClick(self.list, Qt.Key_F2)
        self.app.processEvents()
        editors = self.list.viewport().findChildren(QLineEdit)
        self.assertTrue(editors)
        editor = editors[-1]
        editor.selectAll()
        QTest.keyClicks(editor, "changed")
        QTest.keyClick(editor, Qt.Key_Return)
        self.app.processEvents()
        self.assertEqual(self.list.item(0).text(), "changed")
        self.assertIs(self.app.focusWidget(), self.list)

    def test_escape_confirms_edit(self):
        QTest.keyClick(self.list, Qt.Key_F2)
        self.app.processEvents()
        editor = self.list.viewport().findChildren(QLineEdit)[-1]
        editor.selectAll()
        QTest.keyClicks(editor, "escaped")
        QTest.keyClick(editor, Qt.Key_Escape)
        self.app.processEvents()
        self.assertEqual(self.list.item(0).text(), "escaped")


if __name__ == "__main__":
    unittest.main()
