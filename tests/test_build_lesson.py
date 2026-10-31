from __future__ import annotations

import copy
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "closebook", "scripts"))

import build_lesson  # noqa: E402
from progress_tool import load_json  # noqa: E402

EXAMPLE = os.path.join(ROOT, "skills", "closebook", "schemas", "examples", "lesson.http-cache.json")
EXAMPLE_HTML = os.path.join(ROOT, "examples", "http-cache-lesson.html")
SHOWCASE = os.path.join(ROOT, "tests", "fixtures", "showcase.lesson.json")


def errors(lesson):
    return [i for i in build_lesson.check_lesson(lesson) if i.severity == "error"]


def warnings(lesson):
    return [i for i in build_lesson.check_lesson(lesson) if i.severity == "warning"]


class Fixtures(unittest.TestCase):
    def setUp(self):
        self.lesson = load_json(EXAMPLE)

    def kp(self, kp_id):
        return [k for k in self.lesson["knowledge_points"] if k["id"] == kp_id][0]


class ExampleLessons(Fixtures):
    def test_example_and_showcase_are_clean(self):
        self.assertEqual(build_lesson.check_lesson(self.lesson), [])
        self.assertEqual(build_lesson.check_lesson(load_json(SHOWCASE)), [])

    def test_template_demo_is_clean(self):
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            demo = build_lesson.extract(fh.read())
        self.assertEqual(build_lesson.check_lesson(demo), [])

    def test_built_example_matches_template(self):
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            expected = build_lesson.embed(self.lesson, fh.read())
        with open(EXAMPLE_HTML, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), expected, "rebuild examples/http-cache-lesson.html with build_lesson.py")

    def test_template_is_self_contained(self):
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            html = fh.read()
        for marker in ("<script src", "<link ", "@import", "url(http", "fetch(", "XMLHttpRequest", ".innerHTML"):
            self.assertNotIn(marker, html)

    def test_example_covers_core_interactions(self):
        kinds = {k["interaction_type"] for k in self.lesson["knowledge_points"]}
        kinds |= {k["interaction_type"] for k in load_json(SHOWCASE)["knowledge_points"]}
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            kinds |= {k["interaction_type"] for k in build_lesson.extract(fh.read())["knowledge_points"]}
        required = {"mcq", "flashcard", "free_text", "plain_qa", "compare_table_fill"}
        self.assertTrue(required <= kinds, required - kinds)


class Embedding(Fixtures):
    def test_round_trip_and_script_escape(self):
        self.lesson["intro"] = "watch out for </script><script>alert(1)</script>"
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            html = build_lesson.embed(self.lesson, fh.read())
        self.assertNotIn("</script><script>alert", html)
        self.assertEqual(build_lesson.extract(html), self.lesson)
        self.assertEqual(html.count('<script type="application/json" id="lesson-data">'), 1)

    def test_cli_builds_and_rejects(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "nested", "lesson.html")
            with redirect_stderr(io.StringIO()):
                self.assertEqual(build_lesson.main([EXAMPLE, "--out", out]), 0)
            with open(out, encoding="utf-8") as fh:
                self.assertEqual(build_lesson.extract(fh.read())["lesson_id"], "http-cache-2026-10-31")
            bad = copy.deepcopy(self.lesson)
            bad["knowledge_points"][1]["items"][0]["options"][0]["correct"] = True
            path = os.path.join(tmp, "bad.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(bad, fh, ensure_ascii=False)
            err = io.StringIO()
            with redirect_stderr(err):
                self.assertEqual(build_lesson.main([path, "--check"]), 1)
            self.assertIn("exactly one correct option", err.getvalue())
            with redirect_stderr(io.StringIO()):
                self.assertEqual(build_lesson.main([out, "--check"]), 0)


class SchemaAndSemantics(Fixtures):
    def test_schema_errors(self):
        self.lesson["lesson_id"] = "has space"
        self.kp("kp1")["interaction_type"] = "drag_sort"
        del self.kp("kp2")["interaction_reason"]
        paths = {i.path for i in errors(self.lesson)}
        self.assertIn("$.lesson_id", paths)
        self.assertIn("$.knowledge_points[0].interaction_type", paths)
        self.assertIn("$.knowledge_points[1]", paths)

    def test_mcq_rules(self):
        options = self.kp("kp2")["items"][0]["options"]
        options[0]["correct"] = True
        self.assertIn("exactly one correct option", str(errors(self.lesson)))
        options[0]["correct"] = False
        del options[2]["explanation"]
        self.assertTrue(errors(self.lesson), "every option needs an explanation")

    def test_type_specific_rules(self):
        cases = [
            ("kp3", lambda it: it.pop("answer"), "plain_qa needs question and answer"),
            ("kp4", lambda it: it["rows"][0]["cells"].pop(), "needs 2 cells"),
            ("kp4", lambda it: [c.update(blank=False) for r in it["rows"] for c in r["cells"]], "no blank cells"),
            ("kp1", lambda it: it["edges"].append({"from": "n1", "to": "zz"}), "unknown node"),
            ("kp1", lambda it: [n.update(blank=False) for n in it["nodes"]], "no blank nodes"),
        ]
        for kp_id, mutate, message in cases:
            lesson = copy.deepcopy(self.lesson)
            kp = [k for k in lesson["knowledge_points"] if k["id"] == kp_id][0]
            mutate(kp["items"][0])
            self.assertIn(message, str(errors(lesson)), message)

    def test_free_text_without_required_point_warns(self):
        for p in self.kp("kp6")["items"][0]["reference_points"]:
            p["required"] = False
        self.assertIn("no reference point is marked required", str(warnings(self.lesson)))

    def test_simulation_needs_fallback(self):
        lesson = load_json(SHOWCASE)
        del lesson["knowledge_points"][1]["items"][0]["fallback"]
        self.assertIn("need a fallback", str(errors(lesson)))

    def test_duplicate_ids(self):
        self.kp("kp6")["id"] = "kp1"
        self.assertIn("duplicate id kp1", str(errors(self.lesson)))

    def test_plain_talk_rules(self):
        pt = self.lesson["plain_talk"]
        del pt["points"][0]["analogy_limit"]
        pt["recall"]["kp_id"] = "kp9"
        self.lesson["free_recall"]["reference_points"][0]["kp_id"] = "kp9"
        found = str(errors(self.lesson))
        self.assertIn("analogy_limit", found)
        self.assertIn("$.plain_talk.recall", found)
        self.assertIn("$.free_recall[0]", found)

    def test_fit_warnings(self):
        self.kp("kp6")["interaction_type"] = "mcq"
        self.kp("kp6")["items"] = copy.deepcopy(self.kp("kp2")["items"])
        pt = self.lesson["plain_talk"]["points"][1]
        pt["analogy"], pt["analogy_limit"] = "like a fridge", "fridges don't expire"
        found = str(warnings(self.lesson))
        self.assertIn("mcq doesn't fit judgment", found)
        self.assertIn("factual point with an analogy", found)
        self.assertEqual(errors(self.lesson), [])

    def test_strict_turns_warnings_into_failures(self):
        self.kp("kp6")["interaction_type"] = "mcq"
        self.kp("kp6")["items"] = copy.deepcopy(self.kp("kp2")["items"])
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "l.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self.lesson, fh, ensure_ascii=False)
            with redirect_stderr(io.StringIO()):
                self.assertEqual(build_lesson.main([path, "--check"]), 0)
                self.assertEqual(build_lesson.main([path, "--check", "--strict"]), 1)

    def test_long_teaching_block_warns(self):
        self.kp("kp6")["teach"]["example"] = "很长的例子。" * 100
        self.assertIn("teaching block is long", str(warnings(self.lesson)))


if __name__ == "__main__":
    unittest.main()
