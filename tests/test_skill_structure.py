"""Structural checks for the closebook skill package.

Frontmatter rules follow the Agent Skills specification (agentskills.io/specification)
and Claude's upload constraints (allowed top-level keys, no XML tags, no reserved words).
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "closebook")
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
PATH_RE = re.compile(r"`((?:references|schemas|scripts|assets|modes|methods)/[A-Za-z0-9_./-]+)`")


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise AssertionError("SKILL.md has no frontmatter")
    fields, current = {}, None
    for line in match.group(1).splitlines():
        if line.startswith((" ", "\t")):
            fields[current] += "\n" + line
            continue
        key, _, value = line.partition(":")
        current = key.strip()
        fields[current] = value.strip()
    return fields


class SkillStructureTest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as fh:
            self.text = fh.read()
        self.fm = frontmatter(self.text)

    def test_frontmatter_keys(self):
        self.assertTrue(set(self.fm) <= ALLOWED_KEYS, set(self.fm) - ALLOWED_KEYS)

    def test_name(self):
        name = self.fm["name"]
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertEqual(name, os.path.basename(SKILL))
        self.assertNotIn("claude", name)
        self.assertNotIn("anthropic", name)

    def test_description(self):
        desc = self.fm["description"]
        self.assertTrue(0 < len(desc) <= 1024, len(desc))
        self.assertNotRegex(desc, r"<[^>]+>")

    def test_body_stays_lean(self):
        body_lines = self.text.split("---", 2)[2].strip().splitlines()
        self.assertLess(len(body_lines), 500)

    def test_referenced_files_exist(self):
        missing = []
        for dirpath, _, files in os.walk(SKILL):
            for name in files:
                if not name.endswith(".md"):
                    continue
                path = os.path.join(dirpath, name)
                with open(path, encoding="utf-8") as fh:
                    content = fh.read()
                for ref in PATH_RE.findall(content):
                    candidates = [os.path.join(SKILL, ref), os.path.join(SKILL, "references", ref),
                                  os.path.join(dirpath, ref), os.path.normpath(os.path.join(dirpath, "..", ref))]
                    if any(os.path.exists(c) for c in candidates):
                        continue
                    missing.append("%s -> %s" % (os.path.relpath(path, SKILL), ref))
        self.assertEqual(missing, [])

    def test_all_twelve_methods_and_four_modes_present(self):
        methods = sorted(os.listdir(os.path.join(SKILL, "references", "methods")))
        self.assertEqual(len([m for m in methods if m.endswith(".md")]), 12)
        modes = sorted(os.listdir(os.path.join(SKILL, "references", "modes")))
        self.assertEqual(modes, ["coding.md", "concept.md", "exam-prep.md", "language.md"])

    def test_no_junk_files_in_package(self):
        junk = []
        for dirpath, dirs, files in os.walk(SKILL):
            for name in files + dirs:
                if name.startswith("._") or name in (".DS_Store", "__pycache__") or name.endswith(".pyc"):
                    junk.append(os.path.join(dirpath, name))
        self.assertEqual(junk, [], "junk files break some skill uploads (e.g. Gemini rejects hidden binaries)")


if __name__ == "__main__":
    unittest.main()
