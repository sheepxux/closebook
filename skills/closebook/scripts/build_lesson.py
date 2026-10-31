#!/usr/bin/env python3
"""Build a closebook HTML lesson page from lesson JSON (Python 3.8+, standard library only).

    python3 build_lesson.py lesson.json --out lesson.html
    python3 build_lesson.py lesson.json --check          # validate only

Validates against schemas/lesson-data.schema.json, then checks the per-type and
fit rules JSON Schema can't express, then injects the JSON into
assets/lesson-template.html. The page logic is never modified.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from progress_tool import Issue, SchemaValidator, ToolError, load_json  # noqa: E402

SKILL_DIR = os.path.dirname(HERE)
LESSON_SCHEMA = os.path.join(SKILL_DIR, "schemas", "lesson-data.schema.json")
TEMPLATE = os.path.join(SKILL_DIR, "assets", "lesson-template.html")
DATA_BLOCK = re.compile(r'(<script type="application/json" id="lesson-data">)(.*?)(</script>)', re.S)

UNFIT_INTERACTIONS = {
    "mcq": {"judgment", "contested"},
    "flashcard": {"conceptual", "procedural", "judgment", "contested"},
    "simulation": {"contested", "factual"},
}


def _blank_count(item: Dict[str, Any], kind: str) -> int:
    if kind == "compare_table_fill":
        return sum(1 for row in item.get("rows", []) for cell in row.get("cells", []) if cell.get("blank"))
    if kind == "timeline_fill":
        return sum(1 for ev in item.get("events", []) if ev.get("blank"))
    return sum(1 for node in item.get("nodes", []) if node.get("blank"))


def _sentences(text: str) -> int:
    return len([s for s in re.split(r"[!?。！？]+|\.(?=\s|$)", text) if s.strip()])


def check_lesson(lesson: Any) -> List[Issue]:
    issues = SchemaValidator(LESSON_SCHEMA).validate(lesson)
    if any(i.severity == "error" for i in issues) or not isinstance(lesson, dict):
        return issues

    def err(path: str, msg: str) -> None:
        issues.append(Issue("error", path, msg, "lesson"))

    def warn(path: str, msg: str) -> None:
        issues.append(Issue("warning", path, msg, "fit"))

    kp_ids = set()
    for i, kp in enumerate(lesson["knowledge_points"]):
        base = "$.knowledge_points[%d]" % i
        if kp["id"] in kp_ids:
            err(base + ".id", "duplicate id %s" % kp["id"])
        kp_ids.add(kp["id"])
        kind, ktype = kp["interaction_type"], kp["knowledge_type"]
        if ktype in UNFIT_INTERACTIONS.get(kind, set()):
            warn(base, "%s doesn't fit %s points (see references/interaction-fit.md); record the user override if intended"
                 % (kind, ktype))
        if kp.get("method") == "predict_verify" and ktype == "contested":
            warn(base, "predict_verify is never used on contested points")
        teach = kp.get("teach") or {}
        words = len(" ".join([teach.get("example", ""), teach.get("principle", "")] + teach.get("steps", [])).split())
        chars = len("".join([teach.get("example", ""), teach.get("principle", "")] + teach.get("steps", [])))
        if words > 180 or chars > 450:
            warn(base + ".teach", "teaching block is long; keep it to about 150 words (one example + one principle)")
        item_ids = set()
        for j, item in enumerate(kp["items"]):
            ipath = "%s.items[%d]" % (base, j)
            if item["id"] in item_ids:
                err(ipath + ".id", "duplicate item id %s" % item["id"])
            item_ids.add(item["id"])
            if kind == "mcq":
                opts = item.get("options") or []
                if not item.get("question") or len(opts) < 2:
                    err(ipath, "mcq needs question and at least 2 options")
                elif sum(1 for o in opts if o["correct"]) != 1:
                    err(ipath, "mcq needs exactly one correct option")
                if len({o["text"] for o in opts}) != len(opts):
                    err(ipath, "duplicate option text")
            elif kind == "flashcard":
                if not item.get("front") or not item.get("back"):
                    err(ipath, "flashcard needs front and back")
            elif kind == "free_text":
                points = item.get("reference_points") or []
                if not (item.get("prompt") or item.get("question")) or not points:
                    err(ipath, "free_text needs prompt and reference_points")
                elif not any(p.get("required") for p in points):
                    warn(ipath, "no reference point is marked required; grading falls back to all points")
            elif kind == "plain_qa":
                if not item.get("question") or not item.get("answer"):
                    err(ipath, "plain_qa needs question and answer")
            elif kind == "compare_table_fill":
                cols, rows = item.get("columns") or [], item.get("rows") or []
                if not item.get("prompt") or len(cols) < 2 or not rows:
                    err(ipath, "compare_table_fill needs prompt, >= 2 columns and rows")
                for r, row in enumerate(rows):
                    if len(row["cells"]) != len(cols) - 1:
                        err("%s.rows[%d]" % (ipath, r), "needs %d cells (columns minus the label column)" % (len(cols) - 1))
                if rows and not _blank_count(item, kind):
                    err(ipath, "no blank cells to fill")
            elif kind == "timeline_fill":
                if not item.get("prompt") or len(item.get("events") or []) < 2:
                    err(ipath, "timeline_fill needs prompt and >= 2 events")
                elif not _blank_count(item, kind):
                    err(ipath, "no blanks to fill")
            elif kind == "diagram_fill":
                nodes = item.get("nodes") or []
                ids = {n["id"] for n in nodes}
                if not item.get("prompt") or len(nodes) < 2:
                    err(ipath, "diagram_fill needs prompt and >= 2 nodes")
                elif not _blank_count(item, kind):
                    err(ipath, "no blank nodes to predict")
                for e in item.get("edges") or []:
                    if e["from"] not in ids or e["to"] not in ids:
                        err(ipath, "edge %s -> %s refers to an unknown node" % (e["from"], e["to"]))
            elif kind == "simulation":
                if not item.get("fallback"):
                    err(ipath, "simulation items need a fallback plain question (the page shows it instead)")

    for section in ("free_recall", "plain_talk"):
        if section not in lesson:
            continue
        refs = lesson[section].get("reference_points" if section == "free_recall" else "points", [])
        for k, ref in enumerate(refs):
            if ref["kp_id"] not in kp_ids:
                err("$.%s[%d]" % (section, k), "unknown kp_id %s" % ref["kp_id"])

    pt = lesson.get("plain_talk")
    if pt:
        if pt["recall"]["kp_id"] not in kp_ids:
            err("$.plain_talk.recall", "unknown kp_id %s" % pt["recall"]["kp_id"])
        types = {kp["id"]: kp["knowledge_type"] for kp in lesson["knowledge_points"]}
        for k, p in enumerate(pt["points"]):
            path = "$.plain_talk.points[%d]" % k
            if p.get("analogy") and not p.get("analogy_limit"):
                err(path, "every analogy needs analogy_limit (where the comparison breaks)")
            if p.get("analogy") and types.get(p["kp_id"]) == "factual":
                warn(path, "factual point with an analogy; prefer conclusion + example with no_analogy_reason")
            if not p.get("analogy") and not p.get("no_analogy_reason"):
                warn(path, "no analogy and no no_analogy_reason")
            if _sentences(" ".join([p["conclusion"], p.get("analogy", ""), p.get("analogy_limit", ""), p["example"], p["pitfall"]])) > 6:
                warn(path, "plain talk point is longer than 6 sentences")
        if _sentences(pt["summary"]) > 5:
            warn("$.plain_talk.summary", "summary is longer than 5 sentences")
    return issues


def embed(lesson: Dict[str, Any], template_text: str) -> str:
    payload = json.dumps(lesson, ensure_ascii=False, indent=2).replace("</", "<\\/")
    if not DATA_BLOCK.search(template_text):
        raise ToolError("template has no <script type=\"application/json\" id=\"lesson-data\"> block")
    return DATA_BLOCK.sub(lambda m: m.group(1) + "\n" + payload + "\n" + m.group(3), template_text, count=1)


def extract(html_text: str) -> Any:
    match = DATA_BLOCK.search(html_text)
    if not match:
        raise ToolError("no lesson-data block found")
    return json.loads(match.group(2))


def main(argv: List[str] = None) -> int:
    parser = argparse.ArgumentParser(description="Build a closebook lesson page")
    parser.add_argument("lesson", help="lesson JSON (or a built .html to re-check its embedded data)")
    parser.add_argument("--out", help="output HTML path")
    parser.add_argument("--template", default=TEMPLATE)
    parser.add_argument("--check", action="store_true", help="validate only")
    parser.add_argument("--strict", action="store_true", help="treat fit warnings as errors")
    args = parser.parse_args(argv)
    try:
        if args.lesson.endswith(".html"):
            with open(args.lesson, encoding="utf-8") as fh:
                lesson = extract(fh.read())
        else:
            lesson = load_json(args.lesson)
        issues = check_lesson(lesson)
        for issue in issues:
            print(repr(issue), file=sys.stderr)
        errors = [i for i in issues if i.severity == "error" or (args.strict and i.severity == "warning")]
        if errors:
            print("lesson data: INVALID (%d errors)" % len(errors), file=sys.stderr)
            return 1
        print("lesson data: VALID (%d warnings)" % len(issues), file=sys.stderr)
        if args.check:
            return 0
        with open(args.template, encoding="utf-8") as fh:
            html = embed(lesson, fh.read())
        if args.out:
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(html)
            print("wrote %s" % args.out, file=sys.stderr)
        else:
            sys.stdout.write(html)
        return 0
    except (ToolError, json.JSONDecodeError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
