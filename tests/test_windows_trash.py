import ast
import os
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


sourcePath = Path(__file__).parents[1] / "PPOCRLabel.py"
tree = ast.parse(sourcePath.read_text(encoding="utf-8"))
moveFunction = next(
    node
    for node in tree.body
    if isinstance(node, ast.FunctionDef) and node.name == "moveFileToTrash"
)
namespace = {
    "os": os,
    "platform": platform,
    "subprocess": subprocess,
    "logger": type("Logger", (), {"debug": staticmethod(lambda *_args: None)})(),
}
exec(
    compile(ast.Module([moveFunction], type_ignores=[]), str(sourcePath), "exec"),
    namespace,
)


class WindowsTrashTest(unittest.TestCase):
    @unittest.skipUnless(platform.system() == "Windows", "Windows-only check")
    def test_explicit_path_buffer(self):
        with tempfile.NamedTemporaryFile(
            prefix="ppocrlabel_trash_", delete=False
        ) as file:
            tempPath = Path(file.name)

        try:
            self.assertTrue(namespace["moveFileToTrash"](str(tempPath)))
            self.assertFalse(tempPath.exists())
        finally:
            tempPath.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
