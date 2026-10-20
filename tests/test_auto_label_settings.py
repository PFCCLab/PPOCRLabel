import ast
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from libs.autoLabelSettings import (
    CONFIG_FILENAME,
    default_config,
    load_config,
    resolve_models,
    save_config,
    validate_config,
)


class DatasetSettingsTest(unittest.TestCase):
    def test_directory_isolation_and_no_implicit_writes(self):
        with tempfile.TemporaryDirectory() as root:
            first, second = Path(root) / "first", Path(root) / "second"
            first.mkdir()
            second.mkdir()
            self.assertEqual(load_config(first), default_config())
            self.assertEqual(list(first.iterdir()), [])
            config = {**default_config(), "preset": "PP-OCRv6_medium"}
            save_config(first, config)
            self.assertEqual(load_config(first), config)
            self.assertEqual(load_config(second), default_config())

    def test_saved_fields_exclude_credentials(self):
        with tempfile.TemporaryDirectory() as root:
            save_config(root, {**default_config(), "api_key": "private-test-value"})
            text = (Path(root) / CONFIG_FILENAME).read_text(encoding="utf-8")
            self.assertNotIn("private-test-value", text)
            self.assertEqual(json.loads(text)["schema_version"], 1)

    def test_failed_replace_preserves_previous_configuration(self):
        with tempfile.TemporaryDirectory() as root:
            save_config(root, default_config())
            path = Path(root) / CONFIG_FILENAME
            original = path.read_bytes()
            with patch(
                "libs.autoLabelSettings.os.replace", side_effect=OSError("disk")
            ):
                with self.assertRaises(OSError):
                    save_config(root, {**default_config(), "preset": "PP-OCRv6_tiny"})
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual([p.name for p in Path(root).iterdir()], [CONFIG_FILENAME])

    def test_local_model_identity_and_explicit_cli_priority(self):
        with tempfile.TemporaryDirectory() as root:
            for task in ("det", "rec"):
                directory = Path(root) / task
                directory.mkdir()
                (directory / "inference.yml").write_text(
                    "Global:\n  model_name: PP-OCRv6_medium_" + task,
                    encoding="utf-8",
                )
                (directory / "inference.json").write_text("{}", encoding="utf-8")
                (directory / "inference.pdiparams").write_bytes(b"test")
            config = {
                **default_config(),
                "model_source": "local",
                "det_model_dir": str(Path(root) / "det"),
                "rec_model_dir": str(Path(root) / "rec"),
            }
            self.assertEqual(
                resolve_models(config)["rec_model_name"], "PP-OCRv6_medium_rec"
            )
            options = resolve_models(
                {**default_config(), "preset": "PP-OCRv6_medium"},
                {"det_model_name": "PP-OCRv5_mobile_det"},
            )
            self.assertEqual(options["det_model_name"], "PP-OCRv5_mobile_det")
            self.assertEqual(options["rec_model_name"], "PP-OCRv6_medium_rec")
            with self.assertRaises(ValueError):
                resolve_models(config, {"rec_model_name": "wrong_name"})

    def test_invalid_settings_fail_instead_of_selecting_a_different_model(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / CONFIG_FILENAME).write_text("{broken", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(root)
        with self.assertRaises(ValueError):
            resolve_models({**default_config(), "model_source": "local"})


def model_method_namespace():
    source = Path(__file__).parents[1] / "PPOCRLabel.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "getRecognitionModelName"
    ]
    main = next(
        n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MainWindow"
    )
    functions += [
        n
        for n in main.body
        if isinstance(n, ast.FunctionDef) and n.name == "setAutoLabelConfig"
    ]
    namespace = {
        "validate_config": validate_config,
        "resolve_models": resolve_models,
        "save_config": save_config,
        "DEFAULT_RECOGNITION_MODELS": {
            "ch": "PP-OCRv5_mobile_rec",
            "en": "en_PP-OCRv5_mobile_rec",
        },
        "QApplication": Mock(),
        "Qt": SimpleNamespace(WaitCursor=1),
    }
    for name in ("PaddleOCR", "TextRecognition", "TextDetection"):
        namespace[name] = Mock(side_effect=lambda **kwargs: object())
    exec(
        compile(ast.Module(functions, type_ignores=[]), str(source), "exec"), namespace
    )
    return namespace


class ModelSwitchTest(unittest.TestCase):
    def test_three_models_switch_together_and_failed_load_preserves_old_set(self):
        namespace = model_method_namespace()
        switch = namespace["setAutoLabelConfig"]
        window = SimpleNamespace(
            lang="ch",
            gpu="cpu",
            cls_model_dir=None,
            model_cli_overrides={},
            _loaded_model_options=None,
        )
        switch(window, default_config())
        original = (window.ocr, window.text_recognizer, window.text_detector)
        previous_config = window.model_config.copy()
        namespace["TextDetection"].side_effect = RuntimeError("test model failure")
        with self.assertRaises(RuntimeError):
            switch(window, {**default_config(), "preset": "PP-OCRv6_medium"})
        self.assertEqual(
            (window.ocr, window.text_recognizer, window.text_detector), original
        )
        self.assertEqual(window.model_config, previous_config)
        namespace["TextDetection"].side_effect = lambda **kwargs: object()
        switch(window, {**default_config(), "preset": "PP-OCRv6_medium"})
        for new, old in zip(
            (window.ocr, window.text_recognizer, window.text_detector), original
        ):
            self.assertIsNot(new, old)
        count = namespace["PaddleOCR"].call_count
        switch(window, window.model_config)
        self.assertEqual(namespace["PaddleOCR"].call_count, count)
        for name in ("PaddleOCR", "TextRecognition", "TextDetection"):
            self.assertFalse(namespace[name].call_args.kwargs["enable_mkldnn"])


if __name__ == "__main__":
    unittest.main()
