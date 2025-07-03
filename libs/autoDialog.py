import datetime
import json
import logging
import time

import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox as BB,
    QProgressBar,
    QVBoxLayout,
    QListWidget,
)

from libs.utils import newIcon

logger = logging.getLogger("PPOCRLabel")


class Worker(QThread):
    progressBarValue = pyqtSignal(int)
    listValue = pyqtSignal(str)
    end_signal = pyqtSignal(int, str)
    handle = 0

    def __init__(self, ocr, img_list, main_thread, model):
        super(Worker, self).__init__()
        self.result_dic = None
        self.ocr = ocr
        self.img_list = img_list
        self.mainThread = main_thread
        self.model = model
        self.setStackSize(1024 * 1024)

    def run(self):
        try:
            findex = 0
            for img_path in self.img_list:
                if self.handle == 0:
                    self.listValue.emit(img_path)
                    if self.model == "paddle":
                        img = cv2.imdecode(
                            np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR
                        )
                        h, w, _ = img.shape
                        if h > 32 and w > 32:
                            result = self.ocr.predict(img)[0]
                            self.result_dic = []
                            for poly, text, score in zip(
                                result["rec_polys"],
                                result["rec_texts"],
                                result["rec_scores"],
                            ):
                                # Convert numpy array to list for JSON serialization
                                poly_list = (
                                    poly.tolist() if hasattr(poly, "tolist") else poly
                                )
                                self.result_dic.append([poly_list, (text, score)])
                        else:
                            logger.warning(
                                "The size of %s is too small to be recognised", img_path
                            )
                            self.result_dic = None

                    # 结果保存
                    if self.result_dic is None or len(self.result_dic) == 0:
                        logger.warning("Can not recognise file %s", img_path)
                        pass
                    else:
                        strs = ""
                        for res in self.result_dic:
                            chars = res[1][0]
                            cond = res[1][1]
                            posi = res[0]
                            strs += (
                                "Transcription: "
                                + chars
                                + " Probability: "
                                + str(cond)
                                + " Location: "
                                + json.dumps(posi)
                                + "\n"
                            )
                        # Sending large amounts of data repeatedly through pyqtSignal may affect the program efficiency
                        self.listValue.emit(strs)
                        self.mainThread.result_dic = self.result_dic
                        self.mainThread.filePath = img_path
                        # 保存
                        self.mainThread.saveFile(mode="Auto")
                    findex += 1
                    self.progressBarValue.emit(findex)
                else:
                    break
            self.end_signal.emit(0, "readAll")
            self.exec()
        except Exception as e:
            logger.error("Error in worker thread: %s", e)
            raise


class AutoDialog(QDialog):
    def __init__(
        self,
        text="Enter object label",
        parent=None,
        ocr=None,
        image_list=None,
        len_bar=0,
    ):
        super(AutoDialog, self).__init__(parent)
        self.setFixedWidth(1000)
        self.parent = parent
        self.ocr = ocr
        self.img_list = image_list
        self.len_bar = len_bar
        self.pb = QProgressBar(parent)
        self.pb.setRange(0, self.len_bar)
        self.pb.setValue(0)

        layout = QVBoxLayout()
        layout.addWidget(self.pb)
        self.model = "paddle"
        self.listWidget = QListWidget(self)
        layout.addWidget(self.listWidget)

        self.buttonBox = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(newIcon("done"))
        bb.button(BB.Cancel).setIcon(newIcon("undo"))
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)
        bb.button(BB.Ok).setEnabled(False)

        self.setLayout(layout)
        # self.setWindowTitle("自动标注中")
        self.setWindowModality(Qt.ApplicationModal)

        # self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.thread_1 = Worker(self.ocr, self.img_list, self.parent, "paddle")
        self.thread_1.progressBarValue.connect(self.handleProgressBarSingal)
        self.thread_1.listValue.connect(self.handleListWidgetSingal)
        self.thread_1.end_signal.connect(self.handleEndsignalSignal)
        self.time_start = time.time()  # save start time

    def handleProgressBarSingal(self, i):
        self.pb.setValue(i)

        # calculate time left of auto labeling
        # Use average time to prevent time fluctuations
        avg_time = (time.time() - self.time_start) / i
        time_left = str(
            datetime.timedelta(seconds=avg_time * (self.len_bar - i))
        ).split(".")[
            0
        ]  # Remove microseconds
        # show
        self.setWindowTitle("PPOCRLabel  --  " + f"Time Left: {time_left}")

    def handleListWidgetSingal(self, i):
        self.listWidget.addItem(i)
        titem = self.listWidget.item(self.listWidget.count() - 1)
        self.listWidget.scrollToItem(titem)

    def handleEndsignalSignal(self, i, str):
        if i == 0 and str == "readAll":
            self.buttonBox.button(BB.Ok).setEnabled(True)
            self.buttonBox.button(BB.Cancel).setEnabled(False)

    def reject(self):
        logger.debug("Auto recognition dialog rejected")
        self.thread_1.handle = -1
        self.thread_1.quit()
        while not self.thread_1.isFinished():
            pass
        self.accept()

    def validate(self):
        self.accept()

    def postProcess(self):
        try:
            self.edit.setText(self.edit.text().trimmed())
        except AttributeError:
            self.edit.setText(self.edit.text())
            logger.debug("Auto dialog text: %s", self.edit.text())

    def popUp(self):
        self.thread_1.start()
        return 1 if self.exec_() else None

    def closeEvent(self, event, **kwargs):
        self.reject()
