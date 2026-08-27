import ast
import unittest
from pathlib import Path


sourcePath = Path(__file__).parents[1] / "PPOCRLabel.py"
tree = ast.parse(sourcePath.read_text(encoding="utf-8"))
nodes = [
    node
    for node in tree.body
    if (
        isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "DEFAULT_RECOGNITION_MODELS"
            for target in node.targets
        )
    )
    or (isinstance(node, ast.FunctionDef) and node.name == "getRecognitionModelName")
]
namespace = {}
exec(compile(ast.Module(nodes, type_ignores=[]), str(sourcePath), "exec"), namespace)


class ModelLanguageTest(unittest.TestCase):
    def test_default_recognition_model_selection(self):
        getModelName = namespace["getRecognitionModelName"]
        self.assertEqual(
            getModelName("en", "PP-OCRv5_mobile_rec", None),
            "en_PP-OCRv5_mobile_rec",
        )
        self.assertEqual(getModelName("en", "custom_rec", None), "custom_rec")
        self.assertEqual(
            getModelName("en", "PP-OCRv5_mobile_rec", "custom_dir"),
            "PP-OCRv5_mobile_rec",
        )

    def test_language_switch_keeps_mkldnn_disabled(self):
        modelChoose = next(
            node
            for classNode in tree.body
            if isinstance(classNode, ast.ClassDef) and classNode.name == "MainWindow"
            for node in classNode.body
            if isinstance(node, ast.FunctionDef) and node.name == "modelChoose"
        )
        self.assertTrue(
            any(
                isinstance(node, ast.Constant) and node.value == "enable_mkldnn"
                for node in ast.walk(modelChoose)
            )
        )


if __name__ == "__main__":
    unittest.main()
