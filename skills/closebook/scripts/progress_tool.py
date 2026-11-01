#!/usr/bin/env python3
"""closebook progress tool (Python 3.8+, standard library only).

Validate progress files, list due reviews, record attempts with the Leitner
rules from references/spaced-repetition.md, merge progress files, import
session exports (e.g. from the HTML lesson page) and report statistics.

Run `python3 progress_tool.py -h` or `python3 progress_tool.py <command> -h`.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

SCHEMA_MAJOR = "1"
SCHEMA_VERSION = "1.0"
HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_DIR = os.path.join(os.path.dirname(HERE), "schemas")
PROGRESS_SCHEMA = os.path.join(SCHEMA_DIR, "progress.schema.json")
EXPORT_SCHEMA = os.path.join(SCHEMA_DIR, "session-export.schema.json")
EXPORT_FORMAT = "closebook-session-export"
GRADING_SCHEMA = os.path.join(SCHEMA_DIR, "grading.schema.json")
GRADING_FORMAT = "closebook-grading"

DEFAULT_INTERVALS = [1, 3, 7, 14, 30]
DEFAULT_BATCH = 8

SCORED_PHASES = {"verify_known", "retest", "review", "synthesis", "plain_talk_recall", "project"}
UNSCHEDULED_STATUSES = {"optional_extension", "planned"}
PASS_RESULTS = {"correct", "coherent"}
FUZZY_RESULTS = {"partial", "partly_coherent"}
FAIL_RESULTS = {"incorrect", "incoherent", "dont_know"}
COHERENCE_RESULTS = {"coherent", "partly_coherent", "incoherent"}
SCORE = {
    "correct": 1.0, "coherent": 1.0,
    "partial": 0.5, "partly_coherent": 0.5,
    "incorrect": 0.0, "incoherent": 0.0, "dont_know": 0.0,
}
TO_RECALL_RESULT = {
    "correct": "correct", "coherent": "correct",
    "partial": "partial", "partly_coherent": "partial",
    "incorrect": "incorrect", "incoherent": "incorrect", "dont_know": "incorrect",
}
MASTERY_ORDER = {"weak": 1, "fuzzy": 2, "solid": 3, "not_assessed": 4}
IMPORTANCE_ORDER = {"core": 0, "important": 1, "minor": 2}
DEFAULT_REMEDY = {
    "misconception": "Contrast case that breaks the wrong model; ask why-not; retest in a new form.",
    "memory_lapse": "Retrieve again later in the session; add a memory hook if factual.",
    "careless": "Named once; no re-teaching needed.",
    "misread": "Re-ask with the key word marked; look for that cue next time.",
    "transfer_failure": "New-context variant; explain why the rule applies there.",
}


# --------------------------------------------------------------------------
# I/O helpers
# --------------------------------------------------------------------------

class ToolError(Exception):
    pass


def load_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise ToolError("file not found: %s" % path)
    except json.JSONDecodeError as exc:
        raise ToolError("%s is not valid JSON: %s" % (path, exc))


def dump_json(data: Any, compact: bool = False) -> str:
    if compact:
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def write_json(path: str, data: Any, compact: bool = False) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".closebook-", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(dump_json(data, compact=compact))
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value[:10])
    except (TypeError, ValueError):
        raise ToolError("invalid date: %r" % (value,))


def today_or(value: Optional[str]) -> dt.date:
    return parse_date(value) if value else dt.date.today()


# --------------------------------------------------------------------------
# Minimal JSON Schema validator (the subset used by closebook schemas)
# --------------------------------------------------------------------------

class Issue:
    __slots__ = ("severity", "path", "message", "code")

    def __init__(self, severity: str, path: str, message: str, code: str = "schema"):
        self.severity = severity
        self.path = path or "$"
        self.message = message
        self.code = code

    def __repr__(self) -> str:
        return "%s %s: %s" % (self.severity.upper(), self.path, self.message)

    def as_dict(self) -> Dict[str, str]:
        return {"severity": self.severity, "path": self.path, "message": self.message, "code": self.code}


_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


class SchemaValidator:
    def __init__(self, schema_path: str):
        self.base_dir = os.path.dirname(os.path.abspath(schema_path))
        self.root = load_json(schema_path)
        self._docs = {os.path.basename(schema_path): self.root}

    def _doc(self, name: str) -> Dict[str, Any]:
        if name not in self._docs:
            self._docs[name] = load_json(os.path.join(self.base_dir, name))
        return self._docs[name]

    def _resolve(self, ref: str, current_doc: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        file_part, _, pointer = ref.partition("#")
        doc = self._doc(file_part) if file_part else current_doc
        node: Any = doc
        for part in [p for p in pointer.split("/") if p]:
            node = node[part.replace("~1", "/").replace("~0", "~")]
        return node, doc

    def validate(self, instance: Any) -> List[Issue]:
        issues: List[Issue] = []
        self._check(instance, self.root, "$", issues, self.root)
        return issues

    def _check(self, inst: Any, schema: Dict[str, Any], path: str, out: List[Issue], doc: Dict[str, Any]) -> None:
        if "$ref" in schema:
            target, target_doc = self._resolve(schema["$ref"], doc)
            self._check(inst, target, path, out, target_doc)
            schema = {k: v for k, v in schema.items() if k != "$ref"}

        for key in ("oneOf", "anyOf"):
            if key in schema:
                branch_issues = []
                ok = 0
                for branch in schema[key]:
                    trial: List[Issue] = []
                    self._check(inst, branch, path, trial, doc)
                    if not trial:
                        ok += 1
                    branch_issues.append(trial)
                if ok == 0:
                    best = min(branch_issues, key=len)
                    out.extend(best if best else [Issue("error", path, "matches no allowed form")])
                elif key == "oneOf" and ok > 1:
                    out.append(Issue("error", path, "matches more than one form"))

        stype = schema.get("type")
        if stype is not None:
            types = stype if isinstance(stype, list) else [stype]
            if not any(_TYPE_CHECKS[t](inst) for t in types):
                out.append(Issue("error", path, "expected %s, got %s" % ("/".join(types), _json_type(inst))))
                return

        if "const" in schema and inst != schema["const"]:
            out.append(Issue("error", path, "must be %r" % (schema["const"],)))
        if "enum" in schema and inst not in schema["enum"]:
            allowed = ", ".join("null" if e is None else str(e) for e in schema["enum"])
            out.append(Issue("error", path, "%r is not one of: %s" % (inst, allowed)))

        if isinstance(inst, str):
            if "minLength" in schema and len(inst) < schema["minLength"]:
                out.append(Issue("error", path, "shorter than %d characters" % schema["minLength"]))
            if "maxLength" in schema and len(inst) > schema["maxLength"]:
                out.append(Issue("error", path, "longer than %d characters" % schema["maxLength"]))
            if "pattern" in schema and not re.search(schema["pattern"], inst):
                out.append(Issue("error", path, "%r does not match %s" % (inst, schema["pattern"])))

        if _TYPE_CHECKS["number"](inst):
            if "minimum" in schema and inst < schema["minimum"]:
                out.append(Issue("error", path, "%s is below minimum %s" % (inst, schema["minimum"])))
            if "maximum" in schema and inst > schema["maximum"]:
                out.append(Issue("error", path, "%s is above maximum %s" % (inst, schema["maximum"])))

        if isinstance(inst, list):
            if "minItems" in schema and len(inst) < schema["minItems"]:
                out.append(Issue("error", path, "needs at least %d items" % schema["minItems"]))
            if "maxItems" in schema and len(inst) > schema["maxItems"]:
                out.append(Issue("error", path, "allows at most %d items" % schema["maxItems"]))
            if "items" in schema:
                for i, item in enumerate(inst):
                    self._check(item, schema["items"], "%s[%d]" % (path, i), out, doc)

        if isinstance(inst, dict):
            for req in schema.get("required", []):
                if req not in inst:
                    out.append(Issue("error", path, "missing required field '%s'" % req, code="missing"))
            props = schema.get("properties", {})
            for key, value in inst.items():
                sub = "%s.%s" % (path, key)
                if key in props:
                    self._check(value, props[key], sub, out, doc)
                elif schema.get("additionalProperties") is False:
                    out.append(Issue("error", sub, "unknown field", code="unknown_field"))


def _json_type(value: Any) -> str:
    for name in ("null", "boolean", "integer", "number", "string", "array", "object"):
        if _TYPE_CHECKS[name](value):
            return name
    return type(value).__name__


def schema_tiers(schema_path: str = PROGRESS_SCHEMA) -> Dict[str, Dict[str, str]]:
    """Return {'top': {field: tier}, 'kp': {...}, 'attempt': {...}} from x-tier tags."""
    schema = load_json(schema_path)

    def tiers(props: Dict[str, Any]) -> Dict[str, str]:
        return {k: v.get("x-tier", "core") for k, v in props.items()}

    return {
        "top": tiers(schema["properties"]),
        "kp": tiers(schema["$defs"]["knowledge_point"]["properties"]),
        "attempt": tiers(schema["$defs"]["attempt"]["properties"]),
    }


# --------------------------------------------------------------------------
# Settings and accessors
# --------------------------------------------------------------------------

def intervals_of(progress: Dict[str, Any]) -> List[int]:
    return list((progress.get("settings") or {}).get("leitner_intervals_days") or DEFAULT_INTERVALS)


def batch_size_of(progress: Dict[str, Any]) -> int:
    return int((progress.get("settings") or {}).get("review_batch_size") or DEFAULT_BATCH)


def exam_date_of(progress: Dict[str, Any]) -> Optional[dt.date]:
    exam = progress.get("exam") or {}
    return parse_date(exam["date"]) if exam.get("date") else None


def kp_index(progress: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {kp["id"]: kp for kp in progress.get("knowledge_points", [])}


def get_kp(progress: Dict[str, Any], kp_id: str) -> Dict[str, Any]:
    kp = kp_index(progress).get(kp_id)
    if kp is None:
        raise ToolError("unknown knowledge point id: %s" % kp_id)
    return kp


# --------------------------------------------------------------------------
# Scheduling (references/spaced-repetition.md)
# --------------------------------------------------------------------------

def outcome_of(attempt: Dict[str, Any]) -> Optional[str]:
    """pass / fuzzy / fail, or None for attempts that don't affect the schedule."""
    if attempt.get("phase") not in SCORED_PHASES:
        return None
    hint = attempt.get("hint_level") or 0
    result = attempt.get("result")
    if hint >= 3:
        return "fail"
    if result in PASS_RESULTS:
        return "pass" if hint <= 1 else "fuzzy"
    if result in FUZZY_RESULTS:
        return "fuzzy"
    return "fail"


def is_high_confidence_error(attempt: Dict[str, Any]) -> bool:
    return attempt.get("result") == "incorrect" and attempt.get("confidence") == 3


def _sort_key(indexed: Tuple[int, Dict[str, Any]]) -> Tuple[str, int]:
    idx, attempt = indexed
    return (attempt.get("at", ""), idx)


def replay_kp(kp: Dict[str, Any], intervals: List[int], exam_date: Optional[dt.date] = None) -> None:
    """Recompute schedule state of one knowledge point from its attempt history."""
    attempts = kp.get("attempts") or []
    ordered = [a for _, a in sorted(enumerate(attempts), key=_sort_key)]
    kp["attempts"] = ordered
    if not any(outcome_of(a) for a in ordered):
        if not ordered:
            return
        # Only diagnostics and teaching checks: nothing scheduled yet.
        kp.update({"leitner_box": 0, "next_review": None, "mastery": "not_assessed"})
        kp.pop("last_reviewed", None)
        kp.pop("priority_flag", None)
        if kp.get("status") in ("skipped_known", "planned"):
            kp["status"] = "active"
        return

    box = 0
    mastery = "not_assessed"
    priority = False
    last_day: Optional[dt.date] = None
    next_review: Optional[dt.date] = None
    status = kp.get("status", "active")
    if status in ("skipped_known", "planned"):
        status = "active"
    outcomes_by_day: Dict[dt.date, List[str]] = defaultdict(list)
    promoting_pass_days: List[dt.date] = []

    for attempt in ordered:
        outcome = outcome_of(attempt)
        if outcome is None:
            continue
        day = parse_date(attempt["at"])
        earlier = outcomes_by_day[day]
        first_today = not earlier
        earlier_bad = any(o != "pass" for o in earlier)

        if outcome == "pass":
            if first_today:
                if attempt["phase"] == "verify_known":
                    box = max(box, 2)
                    status = "skipped_known"
                else:
                    box = min(5, box + 1)
                priority = False
                promoting_pass_days.append(day)
            else:
                box = max(box, 1)
            mastery = "fuzzy" if earlier_bad else "solid"
        elif outcome == "fuzzy":
            box = max(1, box - 1)
            mastery = "fuzzy"
        else:
            box = 1
            mastery = "weak"
            if is_high_confidence_error(attempt):
                priority = True

        next_review = day + dt.timedelta(days=intervals[box - 1])
        if exam_date is not None:
            cap = exam_date - dt.timedelta(days=1)
            if day < cap < next_review:
                next_review = cap
        last_day = day
        outcomes_by_day[day].append(outcome)

        if attempt["phase"] == "plain_talk_recall":
            kp["plain_talk_used"] = True
            kp["plain_talk_recall_result"] = TO_RECALL_RESULT[attempt["result"]]

    kp["leitner_box"] = box
    kp["next_review"] = next_review.isoformat() if next_review else None
    kp["last_reviewed"] = last_day.isoformat() if last_day else None
    kp["mastery"] = mastery
    if priority:
        kp["priority_flag"] = True
    else:
        kp.pop("priority_flag", None)
    if status != "active" or "status" in kp:
        kp["status"] = status

    for err in kp.get("errors") or []:
        err_day = parse_date(err["at"])
        err["resolved"] = any(d > err_day for d in promoting_pass_days)


def refresh_weak_points(progress: Dict[str, Any]) -> None:
    """weak_points = points that are weak, fuzzy or flagged; keeps existing notes."""
    notes = {w["kp_id"]: w.get("note", "") for w in progress.get("weak_points", [])}
    weak = []
    for kp in progress.get("knowledge_points", []):
        if kp.get("priority_flag") or kp.get("mastery") in ("weak", "fuzzy"):
            entry = {"kp_id": kp["id"]}
            note = notes.get(kp["id"]) or _auto_note(kp)
            if note:
                entry["note"] = note
            weak.append(entry)
    progress["weak_points"] = weak


def _auto_note(kp: Dict[str, Any]) -> str:
    open_errors = [e for e in kp.get("errors") or [] if not e.get("resolved")]
    if open_errors:
        last = open_errors[-1]
        return last.get("question") or last["error_type"]
    return ""


def recompute(progress: Dict[str, Any]) -> Dict[str, Any]:
    intervals = intervals_of(progress)
    exam_date = exam_date_of(progress)
    for kp in progress.get("knowledge_points", []):
        replay_kp(kp, intervals, exam_date)
    refresh_weak_points(progress)
    return progress


def touch(progress: Dict[str, Any], day: dt.date) -> None:
    current = progress.get("updated")
    if not current or parse_date(current) < day:
        progress["updated"] = day.isoformat()


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def validate_progress(progress: Any, lenient: bool = False) -> List[Issue]:
    issues = SchemaValidator(PROGRESS_SCHEMA).validate(progress)
    if lenient:
        for issue in issues:
            if issue.code == "unknown_field":
                issue.severity = "warning"
    if not isinstance(progress, dict):
        return issues
    version = str(progress.get("schema_version", ""))
    if version and version.split(".")[0] != SCHEMA_MAJOR:
        issues.append(Issue("error", "$.schema_version", "unsupported major version %s" % version))
    if any(i.severity == "error" for i in issues):
        return issues
    issues.extend(_semantic_issues(progress))
    return issues


def _semantic_issues(progress: Dict[str, Any]) -> List[Issue]:
    out: List[Issue] = []
    intervals = intervals_of(progress)
    if any(b <= a for a, b in zip(intervals, intervals[1:])):
        out.append(Issue("error", "$.settings.leitner_intervals_days", "intervals must increase", "semantic"))

    for path, value in _iter_dates(progress):
        try:
            parse_date(value)
        except ToolError:
            out.append(Issue("error", path, "not a real calendar date: %s" % value, "semantic"))
    if any(i.severity == "error" for i in out):
        return out

    seen = set()
    for i, kp in enumerate(progress["knowledge_points"]):
        base = "$.knowledge_points[%d]" % i
        if kp["id"] in seen:
            out.append(Issue("error", base + ".id", "duplicate id %s" % kp["id"], "semantic"))
        seen.add(kp["id"])
        box, nxt = kp["leitner_box"], kp["next_review"]
        if box > 0 and nxt is None:
            out.append(Issue("error", base, "leitner_box %d needs a next_review date" % box, "semantic"))
        if box == 0 and nxt is not None:
            out.append(Issue("warning", base, "box 0 (unscheduled) but next_review is set", "semantic"))
        if kp.get("status") == "skipped_known" and box == 0:
            out.append(Issue("warning", base, "skipped_known but never scheduled", "semantic"))
        contested = kp["knowledge_type"] == "contested"
        for j, att in enumerate(kp["attempts"]):
            apath = "%s.attempts[%d]" % (base, j)
            if att["result"] in COHERENCE_RESULTS and att.get("confidence") is not None:
                out.append(Issue("warning", apath, "confidence is only for right/wrong questions", "semantic"))
            if att["result"] in COHERENCE_RESULTS and not contested:
                out.append(Issue("warning", apath, "coherence result on a non-contested point", "semantic"))
            if (att["phase"] in SCORED_PHASES and att["result"] == "incorrect"
                    and not att.get("error_type") and (att.get("hint_level") or 0) < 3):
                out.append(Issue("warning", apath, "incorrect answer without error_type", "semantic"))
        expected = copy.deepcopy(kp)
        replay_kp(expected, intervals, exam_date_of(progress))
        for field in ("leitner_box", "next_review", "mastery"):
            if kp["attempts"] and expected.get(field) != kp.get(field):
                out.append(Issue(
                    "warning", "%s.%s" % (base, field),
                    "stored %r but the attempt history gives %r (run `recompute` to fix)"
                    % (kp.get(field), expected.get(field)), "drift"))

    ids = {kp["id"] for kp in progress["knowledge_points"]}
    for i, weak in enumerate(progress.get("weak_points", [])):
        if weak["kp_id"] not in ids:
            out.append(Issue("error", "$.weak_points[%d]" % i, "unknown kp_id %s" % weak["kp_id"], "semantic"))
    for i, ov in enumerate(progress.get("user_overrides", [])):
        if ov.get("kp_id") and ov["kp_id"] not in ids:
            out.append(Issue("warning", "$.user_overrides[%d]" % i, "unknown kp_id %s" % ov["kp_id"], "semantic"))
    return out


_DATE_KEYS = {"created", "updated", "date", "at", "next_review", "last_reviewed", "exported_at"}


def _iter_dates(node: Any, path: str = "$") -> Iterable[Tuple[str, str]]:
    if isinstance(node, dict):
        for key, value in node.items():
            sub = "%s.%s" % (path, key)
            if key in _DATE_KEYS and isinstance(value, str):
                yield sub, value
            else:
                yield from _iter_dates(value, sub)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from _iter_dates(item, "%s[%d]" % (path, i))


def _validate_with_dates(schema: str, doc: Any) -> List[Issue]:
    issues = SchemaValidator(schema).validate(doc)
    if any(i.severity == "error" for i in issues) or not isinstance(doc, dict):
        return issues
    for path, value in _iter_dates(doc):
        try:
            parse_date(value)
        except ToolError:
            issues.append(Issue("error", path, "not a real calendar date: %s" % value, "semantic"))
    return issues


def validate_export(export: Any) -> List[Issue]:
    return _validate_with_dates(EXPORT_SCHEMA, export)


def validate_grading(grading: Any) -> List[Issue]:
    return _validate_with_dates(GRADING_SCHEMA, grading)


# --------------------------------------------------------------------------
# Creating, recording, merging
# --------------------------------------------------------------------------

def new_kp(kp_id: str, title: str, importance: str, knowledge_type: str,
           secondary: Optional[List[str]] = None) -> Dict[str, Any]:
    kp: Dict[str, Any] = {
        "id": kp_id, "title": title, "importance": importance, "knowledge_type": knowledge_type,
        "status": "active", "mastery": "not_assessed", "leitner_box": 0, "next_review": None,
        "attempts": [], "errors": [],
    }
    if secondary:
        kp["secondary_types"] = list(secondary)
    return kp


def new_progress(topic: str, day: dt.date, language: Optional[str] = None) -> Dict[str, Any]:
    progress: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "profile": "full", "topic": topic,
        "created": day.isoformat(), "updated": day.isoformat(),
        "settings": {"leitner_intervals_days": list(DEFAULT_INTERVALS),
                     "review_batch_size": DEFAULT_BATCH, "interleaving": "auto"},
        "knowledge_points": [], "weak_points": [],
    }
    if language:
        progress["language"] = language
    return progress


def _error_entry_for(attempt: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if attempt.get("phase") not in SCORED_PHASES or not attempt.get("error_type"):
        return None
    if attempt.get("result") not in ("incorrect", "partial", "dont_know", "incoherent", "partly_coherent"):
        return None
    entry = {
        "at": attempt["at"], "error_type": attempt["error_type"],
        "high_confidence": is_high_confidence_error(attempt),
        "remedy": DEFAULT_REMEDY[attempt["error_type"]], "resolved": False,
    }
    if attempt.get("question"):
        entry["question"] = attempt["question"]
    return entry


def _same_error(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    return (a["at"] == b["at"] and a["error_type"] == b["error_type"]
            and a.get("question", "") == b.get("question", ""))


def add_error(kp: Dict[str, Any], entry: Dict[str, Any]) -> None:
    errors = kp.setdefault("errors", [])
    if not any(_same_error(entry, e) for e in errors):
        errors.append(entry)


def _attempt_signature(a: Dict[str, Any]) -> Tuple[Any, ...]:
    return (a.get("at"), a.get("phase"), a.get("result"), a.get("hint_level") or 0,
            a.get("confidence"), a.get("error_type"))


def same_attempt(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    if a.get("id") and b.get("id"):
        return a["id"] == b["id"]
    if _attempt_signature(a) != _attempt_signature(b):
        return False
    qa, qb = a.get("question"), b.get("question")
    return not (qa and qb and qa != qb)


def add_attempt(kp: Dict[str, Any], attempt: Dict[str, Any]) -> bool:
    """Append unless an equivalent attempt exists. Returns True if added."""
    attempts = kp.setdefault("attempts", [])
    for existing in attempts:
        if same_attempt(existing, attempt):
            for key, value in attempt.items():
                existing.setdefault(key, value)
            return False
    attempts.append(attempt)
    return True


def record_attempt(progress: Dict[str, Any], kp_id: str, attempt: Dict[str, Any]) -> Dict[str, Any]:
    kp = get_kp(progress, kp_id)
    attempt = {k: v for k, v in attempt.items() if v is not None or k == "confidence"}
    if attempt.get("confidence") is None:
        attempt.pop("confidence", None)
    attempt.setdefault("hint_level", 0)
    if not attempt.get("id"):
        attempt["id"] = "%s-%d" % (kp_id, len(kp.get("attempts") or []) + 1)
        while any(a.get("id") == attempt["id"] for a in kp.get("attempts") or []):
            attempt["id"] += "x"
    add_attempt(kp, attempt)
    entry = _error_entry_for(attempt)
    if entry:
        add_error(kp, entry)
    replay_kp(kp, intervals_of(progress), exam_date_of(progress))
    refresh_weak_points(progress)
    touch(progress, parse_date(attempt["at"]))
    return kp


def _union_list(a: Optional[List[Any]], b: Optional[List[Any]]) -> List[Any]:
    out = list(a or [])
    for item in b or []:
        if item not in out:
            out.append(item)
    return out


def merge_progress(base: Dict[str, Any], other: Dict[str, Any]) -> Dict[str, Any]:
    if base.get("topic") != other.get("topic"):
        raise ToolError("topics differ (%r vs %r); refusing to merge" % (base.get("topic"), other.get("topic")))
    merged = copy.deepcopy(base)
    index = kp_index(merged)
    for okp in other.get("knowledge_points", []):
        kp = index.get(okp["id"])
        if kp is None:
            merged["knowledge_points"].append(copy.deepcopy(okp))
            continue
        for att in okp.get("attempts") or []:
            add_attempt(kp, copy.deepcopy(att))
        for err in okp.get("errors") or []:
            add_error(kp, copy.deepcopy(err))
        if okp.get("feynman") and (not kp.get("feynman") or okp["feynman"]["at"] > kp["feynman"]["at"]):
            kp["feynman"] = copy.deepcopy(okp["feynman"])
        if okp.get("plain_talk_used"):
            kp["plain_talk_used"] = True
        for key in ("mnemonics", "methods_selected", "secondary_types"):
            if okp.get(key):
                kp[key] = _union_list(kp.get(key), okp[key])
        for key, value in okp.items():
            if key not in kp:
                kp[key] = copy.deepcopy(value)

    for key in ("sessions", "user_overrides"):
        if other.get(key):
            merged[key] = _union_list(merged.get(key), copy.deepcopy(other[key]))
    for key in ("settings", "exam", "language", "created"):
        if key not in merged and key in other:
            merged[key] = copy.deepcopy(other[key])
    if other.get("created") and merged.get("created") and other["created"] < merged["created"]:
        merged["created"] = other["created"]
    notes = {w["kp_id"]: w.get("note") for w in other.get("weak_points", [])}
    for weak in merged.get("weak_points", []):
        if not weak.get("note") and notes.get(weak["kp_id"]):
            weak["note"] = notes[weak["kp_id"]]
    for weak in other.get("weak_points", []):
        if not any(w["kp_id"] == weak["kp_id"] for w in merged["weak_points"]):
            merged["weak_points"].append(copy.deepcopy(weak))
    if other.get("profile") == "full" or merged.get("profile") == "full":
        merged["profile"] = "full"
    if other.get("updated"):
        touch(merged, parse_date(other["updated"]))
    return recompute(merged)


def import_session(progress: Optional[Dict[str, Any]], export: Dict[str, Any]) -> Dict[str, Any]:
    exported_day = parse_date(export["exported_at"])
    if progress is None:
        progress = new_progress(export["topic"], exported_day, export.get("language"))
    else:
        progress = copy.deepcopy(progress)
    index = kp_index(progress)
    for definition in export.get("knowledge_points", []):
        if definition["id"] not in index:
            kp = new_kp(definition["id"], definition["title"], definition["importance"],
                        definition["knowledge_type"], definition.get("secondary_types"))
            progress["knowledge_points"].append(kp)
            index[kp["id"]] = kp
    missing = sorted({a["kp_id"] for a in export["attempts"] if a["kp_id"] not in index})
    if missing:
        raise ToolError("export refers to unknown knowledge points: %s" % ", ".join(missing))
    default_source = export.get("source", "html")
    for raw in export["attempts"]:
        attempt = {k: v for k, v in raw.items() if k != "kp_id"}
        attempt.setdefault("source", default_source)
        attempt.setdefault("hint_level", 0)
        kp = index[raw["kp_id"]]
        if add_attempt(kp, attempt):
            entry = _error_entry_for(attempt)
            if entry:
                add_error(kp, entry)
    for kp_id in export.get("plain_talk_viewed_kp_ids", []):
        if kp_id in index:
            index[kp_id]["plain_talk_used"] = True
    if not progress.get("knowledge_points"):
        raise ToolError("no knowledge points to import")
    touch(progress, exported_day)
    return recompute(progress)


def apply_grading(progress: Dict[str, Any], grading: Dict[str, Any]) -> Tuple[Dict[str, Any], int, List[str]]:
    """Apply the coach's grades to the attempts with matching ids. Returns (progress, changed, unmatched ids)."""
    progress = copy.deepcopy(progress)
    by_id = {}
    for kp in progress.get("knowledge_points", []):
        for attempt in kp.get("attempts") or []:
            if attempt.get("id"):
                by_id[attempt["id"]] = (kp, attempt)
    changed, unmatched = 0, []
    for grade in grading["grades"]:
        found = by_id.get(grade["attempt_id"])
        if not found:
            unmatched.append(grade["attempt_id"])
            continue
        kp, attempt = found
        bad = grade["result"] not in PASS_RESULTS
        error_type = (grade.get("error_type") or attempt.get("error_type")) if bad else None
        note = grade.get("feedback") or None
        if (attempt.get("coach_graded") and attempt["result"] == grade["result"]
                and attempt.get("note") == note and attempt.get("error_type") == error_type):
            continue
        old_entry = _error_entry_for(attempt)
        if old_entry:
            kp["errors"] = [e for e in kp.get("errors", []) if not _same_error(e, old_entry)]
        attempt["result"] = grade["result"]
        attempt["coach_graded"] = True
        attempt.pop("self_assessed", None)
        for key, value in (("note", note), ("error_type", error_type)):
            if value:
                attempt[key] = value
            else:
                attempt.pop(key, None)
        entry = _error_entry_for(attempt)
        if entry:
            add_error(kp, entry)
        if not kp.get("errors"):
            kp.pop("errors", None)
        changed += 1
    return recompute(progress), changed, unmatched


def _is_empty(value: Any) -> bool:
    return value is None or value is False or (isinstance(value, (list, dict, str)) and not value)


def to_compact(progress: Dict[str, Any]) -> Dict[str, Any]:
    tiers = schema_tiers()

    def keep(obj: Dict[str, Any], tier_map: Dict[str, str], required: Iterable[str]) -> Dict[str, Any]:
        out = {}
        for key, value in obj.items():
            if tier_map.get(key, "extension") != "core":
                continue
            if key not in required and _is_empty(value):
                continue
            out[key] = value
        return out

    compact = keep(progress, tiers["top"], ("weak_points",))
    compact["profile"] = "core"
    compact["knowledge_points"] = []
    for kp in progress["knowledge_points"]:
        ckp = keep(kp, tiers["kp"], ("next_review", "attempts"))
        ckp["attempts"] = [keep(a, tiers["attempt"], ()) for a in kp.get("attempts") or []]
        compact["knowledge_points"].append(ckp)
    return compact


# --------------------------------------------------------------------------
# Queries and statistics
# --------------------------------------------------------------------------

def due_items(progress: Dict[str, Any], day: dt.date, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    rows = []
    for kp in progress["knowledge_points"]:
        if kp.get("status") in UNSCHEDULED_STATUSES or not kp.get("next_review"):
            continue
        nxt = parse_date(kp["next_review"])
        if nxt > day:
            continue
        rows.append({
            "kp_id": kp["id"], "title": kp["title"], "mastery": kp["mastery"],
            "priority_flag": bool(kp.get("priority_flag")), "importance": kp["importance"],
            "knowledge_type": kp["knowledge_type"], "leitner_box": kp["leitner_box"],
            "next_review": kp["next_review"], "days_overdue": (day - nxt).days,
        })
    rows.sort(key=lambda r: (0 if r["priority_flag"] else 1, MASTERY_ORDER.get(r["mastery"], 9),
                             -r["days_overdue"], IMPORTANCE_ORDER.get(r["importance"], 9)))
    cap = batch_size_of(progress) if limit is None else limit
    return rows[:cap] if cap > 0 else rows


def schedule(progress: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = [{"kp_id": kp["id"], "title": kp["title"], "next_review": kp.get("next_review"),
             "leitner_box": kp["leitner_box"], "mastery": kp["mastery"],
             "priority_flag": bool(kp.get("priority_flag"))}
            for kp in progress["knowledge_points"] if kp.get("status") not in UNSCHEDULED_STATUSES]
    rows.sort(key=lambda r: (r["next_review"] is None, r["next_review"] or "", 0 if r["priority_flag"] else 1))
    return rows


def _scored(progress: Dict[str, Any]) -> Iterable[Tuple[Dict[str, Any], Dict[str, Any]]]:
    for kp in progress["knowledge_points"]:
        for att in kp.get("attempts") or []:
            if att.get("phase") in SCORED_PHASES:
                yield kp, att


def _summarise(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(rows)
    durations = [r["duration_sec"] for r in rows if isinstance(r.get("duration_sec"), int)]
    return {
        "attempts": n,
        "accuracy": round(sum(SCORE[r["result"]] for r in rows) / n, 3) if n else None,
        "mean_hint_level": round(sum(r.get("hint_level") or 0 for r in rows) / n, 2) if n else None,
        "timed_attempts": len(durations),
        "mean_duration_sec": round(sum(durations) / len(durations), 1) if durations else None,
        "total_duration_sec": sum(durations) if durations else None,
    }


def method_stats(progress: Dict[str, Any]) -> List[Dict[str, Any]]:
    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for kp, att in _scored(progress):
        groups[(kp["knowledge_type"], att.get("method") or "unspecified")].append(att)
    return [dict({"knowledge_type": k, "method": m}, **_summarise(rows)) for (k, m), rows in sorted(groups.items())]


def interaction_stats(progress: Dict[str, Any]) -> List[Dict[str, Any]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for _, att in _scored(progress):
        groups[att.get("interaction") or "unspecified"].append(att)
    return [dict({"interaction": i}, **_summarise(rows)) for i, rows in sorted(groups.items())]


def error_stats(progress: Dict[str, Any]) -> List[Dict[str, Any]]:
    counts: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "unresolved": 0, "high_confidence": 0})
    for kp in progress["knowledge_points"]:
        for err in kp.get("errors") or []:
            row = counts[err["error_type"]]
            row["total"] += 1
            row["unresolved"] += 0 if err.get("resolved") else 1
            row["high_confidence"] += 1 if err.get("high_confidence") else 0
    rows = [dict({"error_type": t}, **c) for t, c in counts.items()]
    rows.sort(key=lambda r: (-r["total"], r["error_type"]))
    return rows


def high_confidence_errors(progress: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for kp, att in _scored(progress):
        if is_high_confidence_error(att):
            rows.append({"kp_id": kp["id"], "title": kp["title"], "at": att["at"],
                         "question": att.get("question", ""), "error_type": att.get("error_type"),
                         "still_flagged": bool(kp.get("priority_flag"))})
    rows.sort(key=lambda r: (not r["still_flagged"], r["at"]))
    return rows


def calibration(progress: Dict[str, Any]) -> Dict[str, Any]:
    levels: Dict[int, List[float]] = defaultdict(list)
    for _, att in _scored(progress):
        if att.get("confidence") in (1, 2, 3) and att["result"] not in COHERENCE_RESULTS:
            levels[att["confidence"]].append(SCORE[att["result"]])
    by_level = {str(c): {"answers": len(v), "accuracy": round(sum(v) / len(v), 3)} for c, v in sorted(levels.items())}
    total = sum(len(v) for v in levels.values())
    verdict = "insufficient_data"
    if total >= 5:
        verdict = "calibrated"
        hi, lo = levels.get(3, []), levels.get(1, [])
        over = len(hi) >= 3 and sum(hi) / len(hi) < 0.75
        under = len(lo) >= 3 and sum(lo) / len(lo) > 0.6
        if over and under:
            verdict = "mixed"
        elif over:
            verdict = "overconfident"
        elif under:
            verdict = "underconfident"
    return {"rated_answers": total, "by_confidence": by_level, "verdict": verdict}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _print_table(rows: List[Dict[str, Any]], columns: List[str]) -> None:
    if not rows:
        print("(none)")
        return
    widths = {c: max(_width(c), *(_width(_cell(r.get(c))) for r in rows)) for c in columns}
    print("  ".join(_pad(c, widths[c]) for c in columns).rstrip())
    for row in rows:
        print("  ".join(_pad(_cell(row.get(c)), widths[c]) for c in columns).rstrip())


def _width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def _pad(text: str, width: int) -> str:
    return text + " " * (width - _width(text))


def _cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else ""
    return str(value)


def _emit(args: argparse.Namespace, data: Any, columns: Optional[List[str]] = None) -> None:
    if args.json or columns is None:
        print(dump_json(data), end="")
    else:
        _print_table(data, columns)


def _save(args: argparse.Namespace, progress: Dict[str, Any], default_path: Optional[str]) -> None:
    if getattr(args, "dry_run", False):
        print(dump_json(progress), end="")
        return
    target = args.out or default_path
    if not target:
        print(dump_json(progress), end="")
        return
    write_json(target, progress)
    print("wrote %s" % target, file=sys.stderr)


def _load_valid(path: str, lenient: bool = True) -> Dict[str, Any]:
    progress = load_json(path)
    errors = [i for i in validate_progress(progress, lenient=lenient) if i.severity == "error"]
    if errors:
        raise ToolError("%s is not a valid progress file:\n  %s" % (path, "\n  ".join(map(repr, errors[:10]))))
    return progress


def cmd_validate(args: argparse.Namespace) -> int:
    data = load_json(args.file)
    fmt = data.get("format") if isinstance(data, dict) else None
    if fmt == EXPORT_FORMAT:
        issues, kind = validate_export(data), "session export"
    elif fmt == GRADING_FORMAT:
        issues, kind = validate_grading(data), "grading"
    else:
        issues, kind = validate_progress(data, lenient=args.lenient), "progress file"
    errors = [i for i in issues if i.severity == "error"]
    if args.json:
        print(dump_json({"kind": kind, "valid": not errors, "issues": [i.as_dict() for i in issues]}), end="")
    else:
        for issue in issues:
            print(repr(issue))
        print("%s: %s (%d errors, %d warnings)" % (
            kind, "VALID" if not errors else "INVALID", len(errors), len(issues) - len(errors)))
    return 1 if errors else 0


def cmd_due(args: argparse.Namespace) -> int:
    progress = _load_valid(args.file)
    rows = due_items(progress, today_or(args.date), args.limit)
    _emit(args, rows, ["kp_id", "title", "mastery", "priority_flag", "days_overdue", "next_review"])
    return 0


def cmd_schedule(args: argparse.Namespace) -> int:
    progress = _load_valid(args.file)
    _emit(args, schedule(progress), ["next_review", "kp_id", "title", "leitner_box", "mastery", "priority_flag"])
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    progress = _load_valid(args.file)
    attempt = {
        "at": args.at or today_or(args.date).isoformat(), "phase": args.phase, "result": args.result,
        "hint_level": args.hint, "confidence": args.confidence, "error_type": args.error_type,
        "question": args.question, "question_format": args.question_format, "method": args.method,
        "interaction": args.interaction, "duration_sec": args.duration, "source": "file", "note": args.note,
    }
    if args.result in COHERENCE_RESULTS:
        attempt["confidence"] = None
    kp = record_attempt(progress, args.kp, attempt)
    print("%s -> box %s, mastery %s, next review %s%s" % (
        kp["id"], kp["leitner_box"], kp["mastery"], kp["next_review"],
        ", PRIORITY" if kp.get("priority_flag") else ""), file=sys.stderr)
    _save(args, progress, args.file)
    return 0


def cmd_recompute(args: argparse.Namespace) -> int:
    progress = _load_valid(args.file)
    _save(args, recompute(progress), args.file)
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    merged = merge_progress(_load_valid(args.base), _load_valid(args.other))
    _save(args, merged, args.base)
    return 0


def cmd_import_session(args: argparse.Namespace) -> int:
    export = load_json(args.export)
    errors = [i for i in validate_export(export) if i.severity == "error"]
    if errors:
        raise ToolError("invalid session export:\n  %s" % "\n  ".join(map(repr, errors[:10])))
    progress = _load_valid(args.progress) if args.progress and os.path.exists(args.progress) else None
    _save(args, import_session(progress, export), args.progress)
    return 0


def cmd_apply_grading(args: argparse.Namespace) -> int:
    grading = load_json(args.grading)
    errors = [i for i in validate_grading(grading) if i.severity == "error"]
    if errors:
        raise ToolError("invalid grading:\n  %s" % "\n  ".join(map(repr, errors[:10])))
    progress, changed, unmatched = apply_grading(_load_valid(args.progress), grading)
    if unmatched and not changed and len(unmatched) == len(grading["grades"]):
        raise ToolError("no grade matches an attempt in %s (import the session export first?): %s"
                        % (args.progress, ", ".join(unmatched)))
    print("applied %d grade(s)%s" % (changed, "; unmatched: " + ", ".join(unmatched) if unmatched else ""),
          file=sys.stderr)
    _save(args, progress, args.progress)
    return 0


def cmd_compact(args: argparse.Namespace) -> int:
    compact = to_compact(_load_valid(args.file))
    if args.out:
        write_json(args.out, compact, compact=True)
        print("wrote %s" % args.out, file=sys.stderr)
    else:
        print(dump_json(compact, compact=True))
    return 0


def cmd_new(args: argparse.Namespace) -> int:
    day = today_or(args.date)
    progress = new_progress(args.topic, day, args.language)
    for spec in args.kp:
        parts = spec.split("|")
        if len(parts) not in (4, 5):
            raise ToolError("--kp expects 'id|title|importance|knowledge_type[|secondary,types]': %s" % spec)
        secondary = [s for s in parts[4].split(",") if s] if len(parts) == 5 else None
        progress["knowledge_points"].append(new_kp(parts[0], parts[1], parts[2], parts[3], secondary))
    errors = [i for i in validate_progress(progress) if i.severity == "error"]
    if errors:
        raise ToolError("invalid knowledge points:\n  %s" % "\n  ".join(map(repr, errors)))
    if args.out and os.path.exists(args.out) and not args.force:
        raise ToolError("%s exists; use --force to overwrite" % args.out)
    _save(args, progress, None)
    return 0


def _stats_cmd(fn, columns):
    def run(args: argparse.Namespace) -> int:
        _emit(args, fn(_load_valid(args.file)), columns)
        return 0
    return run


def cmd_calibration(args: argparse.Namespace) -> int:
    result = calibration(_load_valid(args.file))
    if args.json:
        print(dump_json(result), end="")
    else:
        print("rated answers: %d, verdict: %s" % (result["rated_answers"], result["verdict"]))
        for level, row in result["by_confidence"].items():
            print("  confidence %s: %d answers, accuracy %.0f%%" % (level, row["answers"], row["accuracy"] * 100))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="progress_tool.py", description="closebook progress tool")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, help_text: str, file_arg: bool = True) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_text, description=help_text)
        if file_arg:
            p.add_argument("file", help="progress JSON file")
        p.add_argument("--json", action="store_true", help="machine-readable output")
        return p

    p = add("validate", "validate a progress file, a session export or a grading block")
    p.add_argument("--lenient", action="store_true", help="treat unknown fields as warnings")
    p.set_defaults(func=cmd_validate)

    p = add("due", "list items due for review, in priority order")
    p.add_argument("--date", help="today's date, YYYY-MM-DD (default: system date)")
    p.add_argument("--limit", type=int, help="max items (default: settings.review_batch_size; 0 = all)")
    p.set_defaults(func=cmd_due)

    p = add("schedule", "list every point with its next review date")
    p.set_defaults(func=cmd_schedule)

    p = add("record", "record one attempt and update the schedule (writes the file)")
    p.add_argument("--kp", required=True)
    p.add_argument("--phase", required=True, choices=["diagnostic", "teach_check", "verify_known", "retest", "review",
                                                      "synthesis", "plain_talk_recall", "project"])
    p.add_argument("--result", required=True, choices=sorted(SCORE))
    p.add_argument("--hint", type=int, default=0, choices=[0, 1, 2, 3])
    p.add_argument("--confidence", type=int, choices=[1, 2, 3])
    p.add_argument("--error-type", choices=sorted(DEFAULT_REMEDY))
    p.add_argument("--question")
    p.add_argument("--question-format")
    p.add_argument("--method")
    p.add_argument("--interaction")
    p.add_argument("--duration", type=int, help="measured seconds (don't estimate)")
    p.add_argument("--note")
    p.add_argument("--date", help="attempt date YYYY-MM-DD (default: today)")
    p.add_argument("--at", help="full ISO timestamp (overrides --date)")
    p.add_argument("--out", help="write here instead of in place")
    p.add_argument("--dry-run", action="store_true", help="print result, don't write")
    p.set_defaults(func=cmd_record)

    p = add("recompute", "replay all attempts and rebuild schedule state")
    p.add_argument("--out")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_recompute)

    p = add("merge", "merge another progress file (e.g. a compact chat export) into BASE", file_arg=False)
    p.add_argument("base")
    p.add_argument("other")
    p.add_argument("--out", help="default: overwrite BASE")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_merge)

    p = add("import-session", "merge a session export (e.g. from the HTML page) into PROGRESS", file_arg=False)
    p.add_argument("progress", help="progress file (created if missing)")
    p.add_argument("export", help="session export JSON")
    p.add_argument("--out")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_import_session)

    p = add("apply-grading", "apply the coach's grading of exported answers to PROGRESS", file_arg=False)
    p.add_argument("progress", help="progress file that already contains the graded attempts")
    p.add_argument("grading", help="closebook-grading JSON")
    p.add_argument("--out")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_apply_grading)

    p = add("compact", "print the compact core-only version for chat use")
    p.add_argument("--out")
    p.set_defaults(func=cmd_compact)

    p = add("new", "create a progress file", file_arg=False)
    p.add_argument("--topic", required=True)
    p.add_argument("--kp", action="append", default=[], required=True,
                   help="'id|title|importance|knowledge_type[|secondary,types]' (repeatable)")
    p.add_argument("--language")
    p.add_argument("--date")
    p.add_argument("--out")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_new)

    p = add("high-confidence-errors", "list confident wrong answers")
    p.set_defaults(func=_stats_cmd(high_confidence_errors,
                                   ["kp_id", "at", "error_type", "still_flagged", "question"]))
    p = add("error-stats", "count errors by cause")
    p.set_defaults(func=_stats_cmd(error_stats, ["error_type", "total", "unresolved", "high_confidence"]))
    p = add("method-stats", "performance by knowledge type and method")
    p.set_defaults(func=_stats_cmd(method_stats, ["knowledge_type", "method", "attempts", "accuracy",
                                                  "mean_hint_level"]))
    p = add("interaction-stats", "performance and time by interaction form")
    p.set_defaults(func=_stats_cmd(interaction_stats, ["interaction", "attempts", "accuracy", "mean_hint_level",
                                                       "timed_attempts", "mean_duration_sec"]))
    p = add("calibration", "confidence vs. accuracy")
    p.set_defaults(func=cmd_calibration)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ToolError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
