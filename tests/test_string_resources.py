import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

import libs.resources
from libs.stringBundle import StringBundle


class StringResourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_auto_recognition_notice_is_available(self):
        for locale in ("en", "zh-CN"):
            bundle = StringBundle.getBundle(locale)
            self.assertTrue(bundle.getString("autoRecognitionNotice").strip())
