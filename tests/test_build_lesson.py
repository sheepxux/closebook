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
SUBJECTS = os.path.join(ROOT, "skills", "closebook", "schemas", "examples", "lesson.subjects.json")
NEW_LEARNER = os.path.join(ROOT, "skills", "closebook", "schemas", "examples", "lesson.new-learner.json")
BUILT_EXAMPLES = [(EXAMPLE, EXAMPLE_HTML),
                  (SUBJECTS, os.path.join(ROOT, "examples", "subject-widgets-lesson.html")),
                  (NEW_LEARNER, os.path.join(ROOT, "examples", "new-learner-lesson.html"))]


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
        self.assertEqual(build_lesson.check_lesson(load_json(SUBJECTS)), [])
        self.assertEqual(build_lesson.check_lesson(load_json(NEW_LEARNER)), [])

    def test_template_demo_is_clean(self):
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            demo = build_lesson.extract(fh.read())
        self.assertEqual(build_lesson.check_lesson(demo), [])

    def test_built_examples_match_template(self):
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            template = fh.read()
        for source, built in BUILT_EXAMPLES:
            with self.subTest(built=os.path.basename(built)), open(built, encoding="utf-8") as fh:
                self.assertEqual(fh.read(), build_lesson.embed(load_json(source), template),
                                 "rebuild %s with build_lesson.py" % os.path.relpath(built, ROOT))

    def test_template_is_self_contained(self):
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            html = fh.read()
        for marker in ("<script src", "<link ", "@import", "url(http", "fetch(", "XMLHttpRequest", ".innerHTML"):
            self.assertNotIn(marker, html)

    def test_example_covers_core_interactions(self):
        kinds = {k["interaction_type"] for k in self.lesson["knowledge_points"]}
        kinds |= {k["interaction_type"] for k in load_json(SHOWCASE)["knowledge_points"]}
        kinds |= {k["interaction_type"] for k in load_json(SUBJECTS)["knowledge_points"]}
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            kinds |= {k["interaction_type"] for k in build_lesson.extract(fh.read())["knowledge_points"]}
        required = {"mcq", "flashcard", "free_text", "plain_qa", "compare_table_fill", "diagram_fill", "timeline_fill", "simulation",
                    "numeric", "order_steps", "cloze_passage", "code_trace", "terminal", "graph"}
        self.assertTrue(required <= kinds, required - kinds)


class Embedding(Fixtures):
    def test_round_trip_and_script_escape(self):
        self.lesson["intro"] = "watch out for </script><script>alert(1)</script>"
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            html = build_lesson.embed(self.lesson, fh.read())
        self.assertNotIn("</script><script>alert", html)
        self.assertEqual(build_lesson.extract(html), self.lesson)
        self.assertEqual(html.count('<script type="application/json" id="lesson-data">'), 1)

    def test_html_comment_before_script_tag_is_escaped(self):
        # "<!--" ... "<script" inside the JSON would make the parser skip the real </script>.
        self.lesson["intro"] = "What does <!-- start, and what does a <script> tag do?"
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            html = build_lesson.embed(self.lesson, fh.read())
        data_block = build_lesson.DATA_BLOCK.search(html).group(2)
        self.assertNotIn("<!--", data_block)
        self.assertEqual(build_lesson.extract(html), self.lesson)
        self.assertEqual(html.count("</script>"), 2)

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
        self.assertIn("needs params (a parameter lab) or a fallback", str(errors(lesson)))

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


class TeachChunks(unittest.TestCase):
    def setUp(self):
        self.lesson = load_json(NEW_LEARNER)
        self.chunks = self.lesson["knowledge_points"][0]["teach"]["chunks"]

    def test_chunks_or_single_block_not_both(self):
        self.lesson["knowledge_points"][0]["teach"]["example"] = "一个例子"
        self.assertIn("either chunks or example", str(errors(self.lesson)))

    def test_check_follows_its_type_rules(self):
        self.chunks[0].update({"check_type": "mcq", "check": {"id": "c", "question": "?", "options": [
            {"text": "a", "correct": True, "explanation": "x"}, {"text": "b", "correct": True, "explanation": "y"}]}})
        self.assertIn("chunks[0].check", str(errors(self.lesson)))
        self.assertIn("exactly one correct option", str(errors(self.lesson)))

    def test_check_id_must_differ_from_items(self):
        self.chunks[1]["check"]["id"] = "doubled"
        self.assertIn("duplicate item id doubled", str(errors(self.lesson)))

    def test_analogy_needs_its_limit(self):
        del self.lesson["knowledge_points"][1]["teach"]["chunks"][0]["analogy_limit"]
        self.assertIn("analogy_limit", str(errors(self.lesson)))

    def test_length_reasons_count_and_mode_warn(self):
        self.chunks[0]["explain"] = "很长的讲解。" * 100
        self.chunks[1]["worked"][0].pop("why")
        self.chunks.extend(copy.deepcopy(self.chunks[:2]))
        for n, chunk in enumerate(self.chunks[2:]):
            chunk["check"]["id"] = "extra-%d" % n
        self.lesson["mode"] = "review"
        text = str(warnings(self.lesson))
        for expected in ("chunk is long", "worked steps without a why", "more than 3 chunks", "only in learn mode"):
            self.assertIn(expected, text)


class Expressions(unittest.TestCase):
    def value(self, src, **env):
        return build_lesson.compile_expr(src, list(env))(env)

    def test_grammar(self):
        self.assertEqual(self.value("a*(x-h)^2+k", a=2, h=1, k=3, x=2), 5)
        self.assertEqual(self.value("2x^2 - 3(x+1)", x=2), -1)
        self.assertEqual(self.value("-x^2", x=3), -9)
        self.assertEqual(self.value("2^3^2"), 512)
        self.assertEqual(self.value("2**3 × 2 ÷ 4 − 1"), 3)
        self.assertAlmostEqual(self.value("2*pi*sqrt(L/g)", L=1, g=9.8), 2.00709, places=4)
        self.assertEqual(self.value("max(1, x, 2) + min(4, 5)", x=7), 11)
        self.assertAlmostEqual(self.value("ln(e) + log(100) + sin(pi/2)"), 4)

    def test_rejects_anything_else(self):
        for src in ["", "2+", "(1", "1)", "y", "foo(1)", "__import__('os')", "x.real", "1; 2", "x[0]", "sin"]:
            with self.assertRaises(ValueError, msg=src):
                build_lesson.compile_expr(src, ["x"])


class SubjectWidgets(unittest.TestCase):
    def setUp(self):
        self.lesson = load_json(SUBJECTS)

    def item(self, kp_id):
        return [k for k in self.lesson["knowledge_points"] if k["id"] == kp_id][0]["items"][0]

    def assertError(self, message):
        self.assertIn(message, str(errors(self.lesson)))

    def test_numeric(self):
        del self.item("kp-num")["value"]
        self.assertError("numeric needs question and value")
        self.lesson = load_json(SUBJECTS)
        self.item("kp-num")["solution"] = []
        self.assertIn("without solution steps", str(warnings(self.lesson)))

    def test_order_steps(self):
        it = self.item("kp-parsons")
        it["distractors"].append(it["steps"][0])
        self.assertError("must all be different")
        it["distractors"].pop()
        it["alternatives"] = [it["steps"][:-1]]
        self.assertError("exactly the same items as steps")
        it["steps"] = it["steps"][:2]
        self.assertError(">= 3 steps")

    def test_cloze_passage(self):
        self.item("kp-cloze")["text"] = "no blanks here"
        self.assertError("at least one [[answer]] blank")
        self.item("kp-cloze")["text"] = "an [[ | ]] empty blank"
        self.assertError("empty blank")

    def test_code_trace(self):
        self.item("kp-trace")["trace"][-1]["line"] = 9
        self.assertError("past the end of the code")
        del self.item("kp-trace")["questions"]
        self.assertError("code_trace needs prompt, code, trace and questions")

    def test_terminal(self):
        self.item("kp-git")["commands"][0]["accept"] = []
        self.assertTrue(errors(self.lesson), "every step needs at least one accepted command")

    def test_graph_match(self):
        it = self.item("kp-parabola")
        it["target"]["a"] = 9
        self.assertError("outside the slider range")
        it["target"] = {"a": 1, "h": 0, "k": 0}
        self.assertError("already start at the target")
        it["target"] = {"a": 0.5, "h": 2}
        self.assertError("needs a number for k")
        it["target"]["z"] = 1
        self.assertError("unknown params: z")

    def test_graph_task_and_expression(self):
        it = self.item("kp-parabola")
        it["predict"] = copy.deepcopy(self.item("kp-sine")["predict"])
        self.assertError("exactly one task")
        del it["predict"]
        it["expr"] = "a*(x-h)^2+q"
        self.assertError("unknown name 'q'")
        it["expr"] = "sqrt(x - 100)"
        self.assertIn("no finite points", str(warnings(self.lesson)))
        it["params"][0]["name"] = "x"
        self.assertError("'x' is reserved")
        it["params"][1]["value"] = 50
        self.assertError("value is outside min..max")
        it["x_range"] = [3, 3]
        self.assertError("min < max")

    def test_simulation_lab(self):
        it = self.item("kp-pendulum")
        del it["predict"]
        self.assertError("needs a predict question")
        it["predict"] = copy.deepcopy(self.item("kp-sine")["predict"])
        it["predict"]["options"][1]["correct"] = True
        self.assertError("exactly one correct option")
        it["predict"]["options"][1]["correct"] = False
        it["outputs"][0]["expr"] = "2*pi*sqrt(L/"
        self.assertError("bad expression")
        it["outputs"], it["plot"] = [], None
        del it["plot"]
        self.assertError("needs outputs (readouts) or a plot")

    def test_trace_matches_a_real_run(self):
        it = self.item("kp-trace")
        self.assertEqual(build_lesson.verify_trace(it), [])
        self.assertEqual(build_lesson.check_code(self.lesson), [])
        wrong = copy.deepcopy(it)
        wrong["trace"][4]["vars"]["total"] = 4
        self.assertEqual(build_lesson.verify_trace(wrong), ["step 5 (line 3): total is 5 after this line, the trace says 4"])
        gap = copy.deepcopy(it)
        gap["trace"].pop(4)
        self.assertIn("a step that changes it is missing", str(build_lesson.verify_trace(gap)))
        silent = copy.deepcopy(it)
        del silent["trace"][-1]["out"]
        self.assertIn("prints '14'", str(build_lesson.verify_trace(silent)))

    def test_trace_through_a_function_call(self):
        code = "def f(n):\n    return n * 2\ny = f(3)\nprint(y)"
        with_return = [{"line": 1}, {"line": 3}, {"line": 2, "vars": {"n": 3}}, {"line": 3, "vars": {"y": 6}}, {"line": 4, "out": "6"}]
        without = [{"line": 1}, {"line": 3}, {"line": 2, "vars": {"n": 3}}, {"line": 4, "vars": {"y": 6}, "out": "6"}]
        for trace in (with_return, without):
            self.assertEqual(build_lesson.verify_trace({"code": code, "trace": trace}), [])

    def test_trace_freezes_mutable_snapshots(self):
        item = {"code": "xs = []\nxs.append(1)\nprint(xs)", "trace": [
            {"line": 1, "vars": {"xs": []}}, {"line": 2, "vars": {"xs": [1]}}, {"line": 3, "out": "[1]"},
        ]}
        self.assertEqual(build_lesson.verify_trace(item), [])
        item["trace"][0]["vars"]["xs"] = [1]
        self.assertIn("xs is []", str(build_lesson.verify_trace(item)))

    def test_trace_preserves_python_container_types(self):
        for code, wrong, correct in [
            ("x = (1, 2)", [1, 2], "(1, 2)"),
            ("x = {1: 2}", {"1": 2}, "{1: 2}"),
            ("x = [True]", [1], [True]),
            ("x = [(1,)]", [[1]], "[(1,)]"),
            ("x = 10**12", 10**12 + 1, 10**12),
        ]:
            with self.subTest(code=code):
                item = {"code": code, "trace": [{"line": 1, "vars": {"x": wrong}}]}
                self.assertTrue(build_lesson.verify_trace(item))
                item["trace"][0]["vars"]["x"] = correct
                self.assertEqual(build_lesson.verify_trace(item), [])

    def test_trace_rejects_missing_state_changes(self):
        cases = [
            {"code": "x = 0\nx = 1", "trace": [{"line": 1, "vars": {"x": 0}}]},
            {"code": "x = 0\nx = 1\nprint(x)", "trace": [
                {"line": 1, "vars": {"x": 0}}, {"line": 3, "vars": {"x": 1}, "out": "1"}]},
        ]
        for item in cases:
            with self.subTest(code=item["code"]):
                self.assertIn("a step that changes it is missing", str(build_lesson.verify_trace(item)))
        self.assertIn("omits new variable x", str(build_lesson.verify_trace({
            "code": "x = 1", "trace": [{"line": 1}],
        })))
        self.assertIn("unsupported Python trace", str(build_lesson.verify_trace({
            "code": "x = 1\ndel x", "trace": [{"line": 1, "vars": {"x": 1}}, {"line": 2}],
        })))

    def test_trace_accepts_none_and_atomic_comprehensions(self):
        item = {"code": "x = None\nys = [n * n for n in range(3)]\nprint(ys)", "trace": [
            {"line": 1, "vars": {"x": None}}, {"line": 2, "vars": {"ys": [0, 1, 4]}},
            {"line": 3, "out": "[0, 1, 4]"},
        ]}
        self.assertEqual(build_lesson.verify_trace(item), [])
        item["trace"][0]["vars"]["x"] = "None"
        self.assertEqual(build_lesson.verify_trace(item), [])

    def test_trace_break_and_optional_loop_check(self):
        item = {"code": "x = 0\nfor n in range(3):\n    x += n\n    if n == 1:\n        break\nprint(x)", "trace": [
            {"line": 1, "vars": {"x": 0}}, {"line": 2, "vars": {"n": 0}},
            {"line": 3}, {"line": 4}, {"line": 2, "vars": {"n": 1}},
            {"line": 3, "vars": {"x": 1}}, {"line": 4}, {"line": 5}, {"line": 6, "out": "1"},
        ]}
        self.assertEqual(build_lesson.verify_trace(item), [])
        # The bundled example intentionally omits the final for-condition check.
        self.assertEqual(build_lesson.verify_trace(self.item("kp-trace")), [])

    def test_trace_cannot_skip_unchanged_control_flow(self):
        item = {"code": "x = 0\nwhile x < 1:\n    break\nprint(x)", "trace": [
            {"line": 1, "vars": {"x": 0}}, {"line": 2}, {"line": 3}, {"line": 4, "out": "0"},
        ]}
        self.assertEqual(build_lesson.verify_trace(item), [])
        for missing in (1, 2):
            gap = copy.deepcopy(item)
            gap["trace"].pop(missing)
            self.assertIn("executes but is missing", str(build_lesson.verify_trace(gap)))
        for code in ("x = 1\nif x == 1:\n    pass\nprint(x)", "x = 1\nx = 1\nprint(x)"):
            gap = {"code": code, "trace": [
                {"line": 1, "vars": {"x": 1}}, {"line": len(code.splitlines()), "out": "1"},
            ]}
            self.assertIn("executes but is missing", str(build_lesson.verify_trace(gap)))

    def test_trace_preserves_blank_output_lines(self):
        item = {"code": "print()\nprint('done')", "trace": [{"line": 1, "out": ""}, {"line": 2, "out": "done"}]}
        self.assertEqual(build_lesson.verify_trace(item), [])
        del item["trace"][0]["out"]
        self.assertIn("complete output", str(build_lesson.verify_trace(item)))

    def test_trace_rejects_unsupported_code_before_running(self):
        for code in ["import os", "open('forbidden', 'w')", "input()", "eval('1')", "x = ().__class__",
                     "x = {}\ny = x.get.__globals__", "x = __builtins__", "class Example:\n    pass",
                     "print('x', file=None)", "getattr(1, 'real')", "x = 1\ndel x"]:
            with self.subTest(code=code):
                self.assertIn("unsupported Python trace", str(build_lesson.verify_trace({"code": code, "trace": []})))

    def test_trace_timeout(self):
        self.assertIn("timed out", str(build_lesson.verify_trace({
            "code": "x = 1", "trace": [{"line": 1, "vars": {"x": 1}}],
        }, timeout=0.000001)))

    def test_cli_always_checks_python_traces(self):
        self.item("kp-trace")["trace"][0]["vars"]["total"] = 99
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "lesson.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self.lesson, fh)
            for flags in ([], ["--run-code"]):
                err = io.StringIO()
                with redirect_stderr(err):
                    self.assertEqual(build_lesson.main([path, "--check"] + flags), 1)
                self.assertIn("total is 0", err.getvalue())

    def test_trace_runaway_and_crashing_code(self):
        self.assertIn("more than 5000 steps", str(build_lesson.verify_trace({"code": "while True:\n    pass", "trace": [{"line": 2}]})))
        self.assertIn("ZeroDivisionError", str(build_lesson.verify_trace({"code": "x = 1/0", "trace": [{"line": 1}]})))

    def test_run_code_only_runs_python(self):
        kp = [k for k in self.lesson["knowledge_points"] if k["id"] == "kp-trace"][0]
        kp["items"][0]["language"] = "JavaScript"
        self.assertIn("check this one by hand", str(build_lesson.check_code(self.lesson)))

    def test_fit_warnings(self):
        kp = [k for k in self.lesson["knowledge_points"] if k["id"] == "kp-sine"][0]
        kp["knowledge_type"] = "factual"
        self.assertIn("graph doesn't fit factual", str(warnings(self.lesson)))


if __name__ == "__main__":
    unittest.main()
