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
    return (os.path.join(out_dir, "closebook.zip"), os.path.join(out_dir, "closebook-gemini.zip"),
            os.path.join(out_dir, "closebook-chatgpt.zip"))


class PackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.full, cls.gemini, cls.chatgpt = build(cls.tmp.name)
        with zipfile.ZipFile(cls.full) as zf:
            cls.full_names = zf.namelist()
        with zipfile.ZipFile(cls.gemini) as zf:
            cls.gemini_names = zf.namelist()
        with zipfile.ZipFile(cls.chatgpt) as zf:
            cls.chatgpt_names = zf.namelist()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_root_folder_is_skill_name(self):
        for names in (self.full_names, self.gemini_names, self.chatgpt_names):
            self.assertTrue(all(n.startswith("closebook/") for n in names))
            self.assertIn("closebook/SKILL.md", names)

    def test_runtime_files_included(self):
        for rel in ("scripts/progress_tool.py", "scripts/build_lesson.py",
                    "assets/lesson-template.html", "schemas/progress.schema.json",
                    "schemas/lesson-data.schema.json", "schemas/session-export.schema.json",
                    "schemas/grading.schema.json",
                    "references/teaching-flow.md"):
            self.assertIn("closebook/" + rel, self.full_names)

    def test_dev_files_and_junk_excluded(self):
        for name in self.full_names + self.gemini_names + self.chatgpt_names:
            base = name.rsplit("/", 1)[-1]
            self.assertNotIn("/evals/", name)
            self.assertNotIn("__pycache__", name)
            self.assertFalse(base.startswith("._") or base == ".DS_Store" or base.endswith(".pyc"), name)

    def test_gemini_build_drops_agents_only(self):
        self.assertIn("closebook/agents/openai.yaml", self.full_names)
        self.assertFalse(any(n.startswith("closebook/agents/") for n in self.gemini_names))
        self.assertEqual(set(self.full_names) - set(self.gemini_names), {"closebook/agents/openai.yaml"})

    def test_chatgpt_build_drops_assets_only(self):
        self.assertFalse(any(n.startswith("closebook/assets/") for n in self.chatgpt_names))
        self.assertEqual(set(self.full_names) - set(self.chatgpt_names), {"closebook/assets/lesson-template.html"})
        self.assertIn("closebook/scripts/build_lesson.py", self.chatgpt_names)

    def test_output_is_deterministic(self):
        with tempfile.TemporaryDirectory() as other:
            full2, gemini2, chatgpt2 = build(other)
            for a, b in ((self.full, full2), (self.gemini, gemini2), (self.chatgpt, chatgpt2)):
                with open(a, "rb") as fa, open(b, "rb") as fb:
                    self.assertEqual(fa.read(), fb.read())


if __name__ == "__main__":
    unittest.main()
