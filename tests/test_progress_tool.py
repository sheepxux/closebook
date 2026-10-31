"""Unit tests for skills/closebook/scripts/progress_tool.py (standard library only).

Run from the repository root:  python3 -m unittest discover -s tests -v
"""
import copy
import datetime as dt
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "closebook")
sys.path.insert(0, os.path.join(SKILL, "scripts"))

import progress_tool as pt  # noqa: E402

EXAMPLES = os.path.join(SKILL, "schemas", "examples")
FULL = os.path.join(EXAMPLES, "progress.full.json")
CORE = os.path.join(EXAMPLES, "progress.core.json")
EXPORT = os.path.join(EXAMPLES, "session-export.example.json")
GRADING = os.path.join(EXAMPLES, "grading.example.json")
TOOL = os.path.join(SKILL, "scripts", "progress_tool.py")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def errors(issues):
    return [i for i in issues if i.severity == "error"]


def warnings(issues):
    return [i for i in issues if i.severity == "warning"]


def blank(topic="T", kp_type="conceptual"):
    progress = pt.new_progress(topic, dt.date(2026, 10, 27))
    progress["knowledge_points"].append(pt.new_kp("kp1", "Point", "core", kp_type))
    return progress


def rec(progress, at, phase="retest", result="correct", hint=0, confidence=2, error_type=None, kp="kp1"):
    return pt.record_attempt(progress, kp, {
        "at": at, "phase": phase, "result": result, "hint_level": hint,
        "confidence": confidence, "error_type": error_type,
    })


class SchemaAndExamplesTest(unittest.TestCase):
    def test_examples_are_valid_without_warnings(self):
        for path in (FULL, CORE):
            issues = pt.validate_progress(load(path))
            self.assertEqual(issues, [], "%s: %r" % (path, issues))
        self.assertEqual(pt.validate_export(load(EXPORT)), [])

    def test_committed_core_example_matches_compact_of_full(self):
        self.assertEqual(load(CORE), pt.to_compact(load(FULL)))

    def test_every_schema_property_is_tiered(self):
        schema = load(pt.PROGRESS_SCHEMA)
        groups = [schema["properties"], schema["$defs"]["knowledge_point"]["properties"],
                  schema["$defs"]["attempt"]["properties"]]
        for props in groups:
            for name, spec in props.items():
                self.assertIn(spec.get("x-tier"), ("core", "extension"), name)

    def test_export_attempt_fields_mirror_progress_attempt(self):
        progress_attempt = set(load(pt.PROGRESS_SCHEMA)["$defs"]["attempt"]["properties"])
        export_attempt = set(load(pt.EXPORT_SCHEMA)["properties"]["attempts"]["items"]["properties"])
        self.assertEqual(export_attempt, progress_attempt | {"kp_id"})

    def test_compact_drops_extension_fields_but_keeps_box_zero(self):
        compact = pt.to_compact(load(FULL))
        self.assertEqual(compact["profile"], "core")
        self.assertNotIn("sessions", compact)
        kp5 = [k for k in compact["knowledge_points"] if k["id"] == "kp5"][0]
        self.assertEqual(kp5["leitner_box"], 0)
        self.assertIsNone(kp5["next_review"])
        for kp in compact["knowledge_points"]:
            self.assertNotIn("methods_selected", kp)
            for att in kp["attempts"]:
                self.assertNotIn("question", att)


class ValidationTest(unittest.TestCase):
    def setUp(self):
        self.p = load(FULL)

    def test_missing_required_field(self):
        del self.p["knowledge_points"][0]["mastery"]
        self.assertTrue(any("mastery" in i.message for i in errors(pt.validate_progress(self.p))))

    def test_bad_enum(self):
        self.p["knowledge_points"][0]["knowledge_type"] = "vibes"
        self.assertTrue(errors(pt.validate_progress(self.p)))

    def test_unknown_field_is_error_unless_lenient(self):
        self.p["knowledge_points"][0]["mood"] = "good"
        self.assertTrue(errors(pt.validate_progress(self.p)))
        lenient = pt.validate_progress(self.p, lenient=True)
        self.assertFalse(errors(lenient))
        self.assertTrue(any(i.code == "unknown_field" for i in warnings(lenient)))

    def test_impossible_calendar_date(self):
        self.p["updated"] = "2026-02-30"
        self.assertTrue(any("calendar" in i.message for i in errors(pt.validate_progress(self.p))))

    def test_duplicate_ids(self):
        self.p["knowledge_points"][1]["id"] = "kp1"
        self.assertTrue(any("duplicate" in i.message for i in errors(pt.validate_progress(self.p))))

    def test_scheduled_box_needs_date(self):
        self.p["knowledge_points"][0]["next_review"] = None
        self.assertTrue(errors(pt.validate_progress(self.p)))

    def test_drift_between_state_and_history_is_reported(self):
        self.p["knowledge_points"][0]["leitner_box"] = 5
        drift = [i for i in pt.validate_progress(self.p) if i.code == "drift"]
        self.assertTrue(drift)
        self.assertEqual(pt.validate_progress(pt.recompute(self.p)), [])

    def test_other_major_version_rejected(self):
        self.p["schema_version"] = "2.0"
        self.assertTrue(errors(pt.validate_progress(self.p)))

    def test_unknown_weak_point(self):
        self.p["weak_points"].append({"kp_id": "nope"})
        self.assertTrue(errors(pt.validate_progress(self.p)))

    def test_confidence_on_contested_point_warns(self):
        p = blank(kp_type="contested")
        p["knowledge_points"][0]["attempts"].append(
            {"at": "2026-10-27", "phase": "retest", "result": "coherent", "confidence": 3})
        pt.recompute(p)
        self.assertTrue(any("confidence" in i.message for i in warnings(pt.validate_progress(p))))


class SchedulingTest(unittest.TestCase):
    def test_new_point_pass_goes_to_box_one_tomorrow(self):
        p = blank()
        kp = rec(p, "2026-10-27")
        self.assertEqual((kp["leitner_box"], kp["next_review"], kp["mastery"]), (1, "2026-10-28", "solid"))

    def test_only_first_attempt_of_day_promotes(self):
        p = blank()
        rec(p, "2026-10-27T10:00")
        kp = rec(p, "2026-10-27T10:30", phase="synthesis")
        self.assertEqual(kp["leitner_box"], 1)

    def test_pass_after_failure_same_day_is_fuzzy_and_not_promoted(self):
        p = blank()
        rec(p, "2026-10-27T10:00", result="incorrect", error_type="memory_lapse")
        kp = rec(p, "2026-10-27T10:20")
        self.assertEqual((kp["leitner_box"], kp["mastery"]), (1, "fuzzy"))

    def test_failure_resets_to_box_one(self):
        p = blank()
        for day in ("2026-10-27", "2026-10-28", "2026-10-31"):
            rec(p, day)
        self.assertEqual(p["knowledge_points"][0]["leitner_box"], 3)
        kp = rec(p, "2026-11-07", result="incorrect", confidence=1, error_type="memory_lapse")
        self.assertEqual((kp["leitner_box"], kp["next_review"], kp["mastery"]), (1, "2026-11-08", "weak"))
        self.assertNotIn("priority_flag", kp)

    def test_high_confidence_error_flag_set_and_cleared_on_later_day(self):
        p = blank()
        kp = rec(p, "2026-10-27T10:00", result="incorrect", confidence=3, error_type="misconception")
        self.assertTrue(kp["priority_flag"])
        self.assertTrue(kp["errors"][0]["high_confidence"])
        kp = rec(p, "2026-10-27T10:30")
        self.assertTrue(kp.get("priority_flag"), "same-day success must not clear the flag")
        self.assertFalse(kp["errors"][0]["resolved"])
        kp = rec(p, "2026-10-28")
        self.assertNotIn("priority_flag", kp)
        self.assertTrue(kp["errors"][0]["resolved"])

    def test_hint_levels(self):
        p = blank()
        rec(p, "2026-10-27")
        rec(p, "2026-10-28")
        rec(p, "2026-10-31")
        kp = rec(p, "2026-11-07", hint=2)
        self.assertEqual((kp["leitner_box"], kp["mastery"]), (2, "fuzzy"))
        kp = rec(p, "2026-11-10", hint=3)
        self.assertEqual((kp["leitner_box"], kp["mastery"]), (1, "weak"))

    def test_diagnostic_never_schedules(self):
        p = blank()
        kp = rec(p, "2026-10-27", phase="diagnostic", result="incorrect", confidence=3)
        self.assertEqual((kp["leitner_box"], kp["next_review"], kp["mastery"]), (0, None, "not_assessed"))
        self.assertNotIn("priority_flag", kp)
        self.assertEqual(kp["errors"], [])

    def test_verify_known_starts_at_box_two(self):
        p = blank()
        kp = rec(p, "2026-10-27", phase="verify_known")
        self.assertEqual((kp["leitner_box"], kp["next_review"], kp["status"]), (2, "2026-10-30", "skipped_known"))

    def test_verify_known_failure_is_taught_normally(self):
        p = blank()
        kp = rec(p, "2026-10-27", phase="verify_known", result="incorrect", confidence=2, error_type="memory_lapse")
        self.assertEqual((kp["leitner_box"], kp["status"]), (1, "active"))

    def test_box_caps_at_five(self):
        p = blank()
        day = dt.date(2026, 1, 1)
        for _ in range(7):
            rec(p, day.isoformat())
            day += dt.timedelta(days=40)
        kp = p["knowledge_points"][0]
        self.assertEqual(kp["leitner_box"], 5)
        self.assertEqual(pt.parse_date(kp["next_review"]) - pt.parse_date(kp["last_reviewed"]), dt.timedelta(days=30))

    def test_worked_example_from_reference_doc(self):
        p = blank()
        rec(p, "2026-10-27T09:00", phase="diagnostic", result="dont_know", confidence=None)
        self.assertEqual(rec(p, "2026-10-27T09:10")["next_review"], "2026-10-28")
        self.assertEqual(rec(p, "2026-10-27T09:40", phase="synthesis", confidence=None)["leitner_box"], 1)
        kp = rec(p, "2026-10-28", phase="review", result="incorrect", confidence=3, error_type="misconception")
        self.assertEqual((kp["leitner_box"], kp["next_review"], kp.get("priority_flag")), (1, "2026-10-29", True))
        kp = rec(p, "2026-10-29", phase="review")
        self.assertEqual((kp["leitner_box"], kp["next_review"], kp.get("priority_flag")), (2, "2026-11-01", None))
        kp = rec(p, "2026-11-01", phase="review", result="partial", error_type="memory_lapse")
        self.assertEqual((kp["leitner_box"], kp["next_review"], kp["mastery"]), (1, "2026-11-02", "fuzzy"))

    def test_custom_intervals(self):
        p = blank()
        p["settings"]["leitner_intervals_days"] = [2, 4, 8, 16, 32]
        self.assertEqual(rec(p, "2026-10-27")["next_review"], "2026-10-29")

    def test_exam_date_caps_next_review(self):
        p = blank()
        p["exam"] = {"date": "2026-11-05"}
        for day in ("2026-10-27", "2026-10-28", "2026-10-31"):
            kp = rec(p, day)
        self.assertEqual(kp["next_review"], "2026-11-04")

    def test_plain_talk_recall_fields(self):
        p = blank()
        kp = rec(p, "2026-10-27", phase="plain_talk_recall", result="partial", error_type="memory_lapse")
        self.assertTrue(kp["plain_talk_used"])
        self.assertEqual(kp["plain_talk_recall_result"], "partial")
        self.assertEqual(p["weak_points"][0]["kp_id"], "kp1")

    def test_contested_coherence_results_schedule(self):
        p = blank(kp_type="contested")
        kp = rec(p, "2026-10-27", result="partly_coherent", confidence=None)
        self.assertEqual((kp["leitner_box"], kp["mastery"]), (1, "fuzzy"))
        self.assertEqual(pt.validate_progress(p), [])

    def test_recompute_reproduces_example(self):
        full = load(FULL)
        self.assertEqual(pt.recompute(copy.deepcopy(full)), full)


class QueriesTest(unittest.TestCase):
    def setUp(self):
        self.p = load(FULL)

    def test_due_priority_order(self):
        rows = pt.due_items(self.p, dt.date(2026, 10, 31))
        self.assertEqual([r["kp_id"] for r in rows], ["kp2", "kp3", "kp1", "kp4"])
        self.assertTrue(rows[0]["priority_flag"])
        self.assertEqual(rows[0]["days_overdue"], 2)

    def test_due_respects_limit_and_excludes_optional(self):
        self.assertEqual(len(pt.due_items(self.p, dt.date(2026, 10, 31), limit=2)), 2)
        self.assertEqual(pt.due_items(self.p, dt.date(2026, 10, 28)), [])
        ids = [r["kp_id"] for r in pt.due_items(self.p, dt.date(2027, 1, 1), limit=0)]
        self.assertNotIn("kp5", ids)

    def test_high_confidence_errors(self):
        rows = pt.high_confidence_errors(self.p)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["kp_id"] == "kp2" and r["still_flagged"] for r in rows))

    def test_error_stats(self):
        stats = {r["error_type"]: r for r in pt.error_stats(self.p)}
        self.assertEqual(stats["misconception"], {"error_type": "misconception", "total": 2,
                                                  "unresolved": 2, "high_confidence": 2})
        self.assertEqual(stats["transfer_failure"]["unresolved"], 0)

    def test_method_stats_groups_by_type_and_method(self):
        stats = {(r["knowledge_type"], r["method"]): r for r in pt.method_stats(self.p)}
        self.assertEqual(stats[("factual", "retrieval")]["accuracy"], 0.0)
        self.assertEqual(stats[("judgment", "elaborative_interrogation")]["mean_hint_level"], 1.0)
        self.assertNotIn(("conceptual", "unspecified"), stats)

    def test_interaction_stats_time(self):
        stats = {r["interaction"]: r for r in pt.interaction_stats(self.p)}
        self.assertEqual(stats["plain_qa"]["timed_attempts"], 2)
        self.assertEqual(stats["plain_qa"]["mean_duration_sec"], 29.5)
        self.assertIsNone(stats["free_text"]["mean_duration_sec"])

    def test_calibration(self):
        result = pt.calibration(self.p)
        self.assertEqual(result["rated_answers"], 9)
        self.assertEqual(result["by_confidence"]["3"], {"answers": 4, "accuracy": 0.5})
        self.assertEqual(result["verdict"], "overconfident")
        self.assertEqual(pt.calibration(blank())["verdict"], "insufficient_data")


class MergeAndImportTest(unittest.TestCase):
    def test_merging_compact_copy_into_full_changes_nothing(self):
        full = load(FULL)
        merged = pt.merge_progress(full, pt.to_compact(full))
        self.assertEqual(merged, full)

    def test_compact_chat_session_merges_into_full(self):
        full = load(FULL)
        chat = pt.to_compact(full)
        pt.record_attempt(chat, "kp2", {"at": "2026-10-31", "phase": "review", "result": "correct",
                                        "hint_level": 0, "confidence": 2})
        merged = pt.merge_progress(full, chat)
        kp2 = pt.get_kp(merged, "kp2")
        self.assertEqual(len(kp2["attempts"]), 5)
        self.assertEqual((kp2["leitner_box"], kp2["next_review"]), (2, "2026-11-03"))
        self.assertIn("mnemonics", kp2, "extension fields from the full file survive")
        self.assertEqual(merged["profile"], "full")
        self.assertEqual(merged["updated"], "2026-10-31")
        self.assertEqual(errors(pt.validate_progress(merged)), [])

    def test_merge_refuses_different_topics(self):
        other = load(FULL)
        other["topic"] = "Something else"
        with self.assertRaises(pt.ToolError):
            pt.merge_progress(load(FULL), other)

    def test_merge_adds_new_points(self):
        other = load(FULL)
        other["knowledge_points"].append(pt.new_kp("kp9", "New", "minor", "factual"))
        self.assertIn("kp9", pt.kp_index(pt.merge_progress(load(FULL), other)))

    def test_import_html_session(self):
        merged = pt.import_session(load(FULL), load(EXPORT))
        self.assertEqual(errors(pt.validate_progress(merged)), [])
        idx = pt.kp_index(merged)
        self.assertEqual((idx["kp2"]["leitner_box"], idx["kp2"]["next_review"]), (2, "2026-11-03"))
        self.assertNotIn("priority_flag", idx["kp2"])
        self.assertTrue(all(e["resolved"] for e in idx["kp2"]["errors"]))
        self.assertEqual((idx["kp3"]["leitner_box"], idx["kp3"]["mastery"]), (1, "fuzzy"))
        self.assertEqual(idx["kp3"]["errors"][-1]["error_type"], "memory_lapse")
        self.assertEqual((idx["kp1"]["leitner_box"], idx["kp1"]["next_review"]), (3, "2026-11-07"))
        self.assertEqual(idx["kp6"]["plain_talk_recall_result"], "partial")
        self.assertTrue(idx["kp6"]["plain_talk_used"])
        self.assertTrue(idx["kp3"]["attempts"][-1]["self_assessed"])
        self.assertEqual(merged["updated"], "2026-10-31")

    def test_import_is_idempotent(self):
        once = pt.import_session(load(FULL), load(EXPORT))
        self.assertEqual(pt.import_session(once, load(EXPORT)), once)

    def test_import_without_existing_progress(self):
        export = load(EXPORT)
        with self.assertRaises(pt.ToolError):
            pt.import_session(None, export)
        export["attempts"] = [a for a in export["attempts"] if a["kp_id"] == "kp6"]
        created = pt.import_session(None, export)
        self.assertEqual([k["id"] for k in created["knowledge_points"]], ["kp6"])
        self.assertEqual((created["topic"], created["created"]), ("HTTP 缓存", "2026-10-31"))
        self.assertEqual(errors(pt.validate_progress(created)), [])

    def test_import_unknown_point_fails(self):
        export = load(EXPORT)
        export["attempts"][0]["kp_id"] = "ghost"
        with self.assertRaises(pt.ToolError):
            pt.import_session(load(FULL), export)


class GradingTest(unittest.TestCase):
    def imported(self):
        return pt.import_session(load(FULL), load(EXPORT))

    def attempt(self, progress, kp_id, attempt_id):
        return [a for a in pt.get_kp(progress, kp_id)["attempts"] if a.get("id") == attempt_id][0]

    def test_example_grading_is_valid(self):
        self.assertEqual(pt.validate_grading(load(GRADING)), [])

    def test_grading_replaces_self_checks(self):
        graded, changed, unmatched = pt.apply_grading(self.imported(), load(GRADING))
        self.assertEqual((changed, unmatched), (2, []))
        self.assertEqual(errors(pt.validate_progress(graded)), [])
        curl = self.attempt(graded, "kp3", "html-2")
        self.assertEqual((curl["result"], curl["coach_graded"], curl["error_type"]), ("incorrect", True, "memory_lapse"))
        self.assertNotIn("self_assessed", curl)
        self.assertIn("If-None-Match", curl["note"])
        self.assertEqual(sum(1 for e in pt.get_kp(graded, "kp3")["errors"] if e.get("question", "").startswith("带上")), 1,
                         "the old error entry is replaced, not duplicated")
        recall = self.attempt(graded, "kp6", "html-4")
        self.assertEqual((recall["result"], recall["coach_graded"]), ("correct", True))
        self.assertEqual(pt.get_kp(graded, "kp6")["plain_talk_recall_result"], "correct")

    def test_grading_is_idempotent_and_reports_unknown_ids(self):
        once, _, _ = pt.apply_grading(self.imported(), load(GRADING))
        twice, changed, _ = pt.apply_grading(once, load(GRADING))
        self.assertEqual((twice, changed), (once, 0))
        grading = load(GRADING)
        grading["grades"].append({"attempt_id": "ghost", "result": "correct"})
        _, changed, unmatched = pt.apply_grading(self.imported(), grading)
        self.assertEqual((changed, unmatched), (2, ["ghost"]))

    def test_correct_grade_clears_the_error(self):
        grading = load(GRADING)
        grading["grades"] = [{"attempt_id": "html-2", "result": "correct", "feedback": "对。"}]
        graded, _, _ = pt.apply_grading(self.imported(), grading)
        curl = self.attempt(graded, "kp3", "html-2")
        self.assertNotIn("error_type", curl)
        self.assertFalse(any(e.get("question", "").startswith("带上") for e in pt.get_kp(graded, "kp3").get("errors", [])))

    def test_invalid_grading_is_rejected(self):
        bad = load(GRADING)
        bad["grades"][0]["result"] = "great"
        self.assertTrue(errors(pt.validate_grading(bad)))
        bad = load(GRADING)
        bad["grades"] = []
        self.assertTrue(errors(pt.validate_grading(bad)))


class CliTest(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = pt.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_new_record_due_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "p.json")
            code, _, _ = self.run_cli("new", "--topic", "Spanish preterite", "--date", "2026-10-31",
                                      "--kp", "kp1|Regular endings|core|language_production",
                                      "--kp", "kp2|Irregular stems|important|language_production|factual",
                                      "--language", "en", "--out", path)
            self.assertEqual(code, 0)
            code, _, err = self.run_cli("record", path, "--kp", "kp2", "--phase", "retest",
                                        "--result", "incorrect", "--confidence", "3",
                                        "--error-type", "memory_lapse", "--date", "2026-10-31")
            self.assertEqual(code, 0)
            self.assertIn("PRIORITY", err)
            self.run_cli("record", path, "--kp", "kp1", "--phase", "retest", "--result", "correct",
                         "--confidence", "2", "--date", "2026-10-31")
            data = load(path)
            self.assertEqual(pt.get_kp(data, "kp2")["attempts"][0]["id"], "kp2-1")
            self.assertEqual(pt.get_kp(data, "kp2")["secondary_types"], ["factual"])
            code, out, _ = self.run_cli("due", path, "--date", "2026-11-01", "--json")
            self.assertEqual([r["kp_id"] for r in json.loads(out)], ["kp2", "kp1"])
            code, out, _ = self.run_cli("validate", path)
            self.assertEqual(code, 0)
            self.assertIn("VALID", out)

    def test_validate_reports_invalid_with_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.json")
            bad = load(FULL)
            bad["knowledge_points"][0]["importance"] = "huge"
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(bad, fh)
            code, out, _ = self.run_cli("validate", path, "--json")
            self.assertEqual(code, 1)
            self.assertFalse(json.loads(out)["valid"])

    def test_compact_output_is_valid_and_roundtrips(self):
        code, out, _ = self.run_cli("compact", FULL)
        self.assertEqual(code, 0)
        compact = json.loads(out)
        self.assertEqual(pt.validate_progress(compact), [])
        self.assertNotIn("\n", out.strip())

    def test_missing_file_is_a_clean_error(self):
        code, _, err = self.run_cli("due", "/nonexistent/p.json")
        self.assertEqual(code, 2)
        self.assertIn("not found", err)

    def test_apply_grading_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "p.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(load(FULL), fh)
            code, _, err = self.run_cli("apply-grading", path, GRADING)
            self.assertEqual(code, 2, "attempts not imported yet")
            self.assertIn("import the session export first", err)
            self.assertEqual(self.run_cli("import-session", path, EXPORT)[0], 0)
            code, _, err = self.run_cli("apply-grading", path, GRADING)
            self.assertEqual(code, 0)
            self.assertIn("applied 2 grade(s)", err)
            self.assertTrue(pt.get_kp(load(path), "kp6")["attempts"][-1]["coach_graded"])
            code, out, _ = self.run_cli("validate", GRADING)
            self.assertEqual(code, 0)
            self.assertIn("grading: VALID", out)

    def test_script_runs_as_subprocess(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        proc = subprocess.run([sys.executable, TOOL, "validate", EXPORT], capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("session export: VALID", proc.stdout)


if __name__ == "__main__":
    unittest.main()
