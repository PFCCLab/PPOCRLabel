from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from libs.autoLabelSettings import LANGUAGES, MODEL_PRESETS


class AutoLabelSettingsDialog(QDialog):
    def __init__(self, config, parent=None, language="ch", cli_overrides=False):
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(self.text("Automatic labeling settings", "自动标注设置"))
        self.setMinimumWidth(620)
        self.source = QComboBox()
        self.source.setObjectName("modelSource")
        self.source.addItem(
            self.text("Official Paddle model", "官方 Paddle 模型"), "official"
        )
        self.source.addItem(self.text("Local Paddle model", "本地 Paddle 模型"), "local")
        self.source.setCurrentIndex(self.source.findData(config["model_source"]))
        self.preset = QComboBox()
        self.preset.setObjectName("modelPreset")
        self.preset.addItems(MODEL_PRESETS)
        self.preset.setCurrentText(config["preset"])
        self.model_language = QComboBox()
        for key, label in LANGUAGES.items():
            self.model_language.addItem(label, key)
        self.model_language.setCurrentIndex(
            self.model_language.findData(config["language"])
        )
        self.det_directory = QLineEdit(config["det_model_dir"])
        self.det_directory.setObjectName("detModelDirectory")
        self.rec_directory = QLineEdit(config["rec_model_dir"])
        self.rec_directory.setObjectName("recModelDirectory")
        self.official_widget = QWidget()
        official = QFormLayout(self.official_widget)
        official.setContentsMargins(0, 0, 0, 0)
        official.addRow(self.text("Model", "模型"), self.preset)
        official.addRow(
            self.text("v5 mobile language", "v5 mobile 语言"), self.model_language
        )
        self.local_widget = QWidget()
        local = QFormLayout(self.local_widget)
        local.setContentsMargins(0, 0, 0, 0)
        local.addRow(
            self.text("Detection model", "检测模型"), self.directory_row(self.det_directory)
        )
        local.addRow(
            self.text("Recognition model", "识别模型"),
            self.directory_row(self.rec_directory),
        )
        note = QLabel(
            self.text(
                "Select exported Paddle inference directories containing inference.yml, "
                "inference.json (or .pdmodel) and inference.pdiparams.",
                "请选择导出的 Paddle 推理目录，包含 inference.yml、"
                "inference.json（或 .pdmodel）和 inference.pdiparams。",
            )
        )
        note.setWordWrap(True)
        local.addRow(note)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow(self.text("Model source", "模型来源"), self.source)
        layout.addLayout(form)
        layout.addWidget(self.official_widget)
        layout.addWidget(self.local_widget)
        if cli_overrides:
            notice = QLabel(
                self.text(
                    "Explicit command-line model arguments take priority for this session.",
                    "本次启动显式指定的命令行模型参数优先于目录配置。",
                )
            )
            notice.setWordWrap(True)
            layout.addWidget(notice)
        hint = QLabel(
            self.text(
                "Settings are saved for the current image directory. Confirmed images are skipped.",
                "设置按当前图片目录保存。批量自动标注会跳过已确认（√）图片。",
            )
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.source.currentIndexChanged.connect(self.update_fields)
        self.preset.currentIndexChanged.connect(self.update_fields)
        self.update_fields()

    def text(self, english, chinese):
        return chinese if self.language == "ch" else english

    def directory_row(self, edit):
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit)
        browse = QPushButton(self.text("Browse…", "浏览…"))
        browse.clicked.connect(lambda: self.browse(edit))
        layout.addWidget(browse)
        return row

    def browse(self, edit):
        directory = QFileDialog.getExistingDirectory(
            self, self.windowTitle(), edit.text()
        )
        if directory:
            edit.setText(directory)

    def update_fields(self):
        official = self.source.currentData() == "official"
        self.official_widget.setVisible(official)
        self.local_widget.setVisible(not official)
        self.model_language.setEnabled(self.preset.currentText() == "PP-OCRv5_mobile")

    def config(self):
        return {
            "model_source": self.source.currentData(),
            "preset": self.preset.currentText(),
            "language": self.model_language.currentData(),
            "det_model_dir": self.det_directory.text().strip(),
            "rec_model_dir": self.rec_directory.text().strip(),
        }
