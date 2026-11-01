"""Tests for tools/package_skill.py: ZIP layout, exclusions, determinism."""
import contextlib
import io
import os
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import package_skill  # noqa: E402


def build(out_dir):
    with contextlib.redirect_stdout(io.StringIO()):
        package_skill.main(["--out", out_dir])
    return os.path.join(out_dir, "closebook.zip")


class PackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.zip = build(cls.tmp.name)
        with zipfile.ZipFile(cls.zip) as zf:
            cls.names = zf.namelist()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_single_zip_is_the_only_output(self):
        self.assertEqual([n for n in os.listdir(self.tmp.name) if n.endswith(".zip")], ["closebook.zip"])

    def test_root_folder_is_skill_name(self):
        self.assertTrue(all(n.startswith("closebook/") for n in self.names))
        self.assertIn("closebook/SKILL.md", self.names)

    def test_runtime_files_included(self):
        for rel in ("scripts/progress_tool.py", "scripts/build_lesson.py",
                    "schemas/progress.schema.json", "schemas/lesson-data.schema.json",
                    "schemas/session-export.schema.json", "schemas/grading.schema.json",
                    "references/teaching-flow.md", "references/host-widgets.md", "references/html-lesson.md"):
            self.assertIn("closebook/" + rel, self.names)

    def test_upload_zip_leaves_out_yaml_and_javascript(self):
        self.assertFalse(any(n.startswith("closebook/agents/") for n in self.names), "Gemini refuses .yaml uploads")
        self.assertFalse(any(n.startswith("closebook/assets/") for n in self.names), "ChatGPT refuses JavaScript")
        self.assertFalse(any(n.endswith((".js", ".html", ".yaml", ".yml")) for n in self.names))
        # the directory install keeps both
        self.assertTrue(os.path.exists(os.path.join(package_skill.SKILL_DIR, "assets", "lesson-template.html")))
        self.assertTrue(os.path.exists(os.path.join(package_skill.SKILL_DIR, "agents", "openai.yaml")))

    def test_dev_files_and_junk_excluded(self):
        for name in self.names:
            base = name.rsplit("/", 1)[-1]
            self.assertNotIn("/evals/", name)
            self.assertNotIn("__pycache__", name)
            self.assertFalse(base.startswith("._") or base == ".DS_Store" or base.endswith(".pyc"), name)

    def test_output_is_deterministic(self):
        with tempfile.TemporaryDirectory() as other:
            with open(self.zip, "rb") as fa, open(build(other), "rb") as fb:
                self.assertEqual(fa.read(), fb.read())


if __name__ == "__main__":
    unittest.main()
