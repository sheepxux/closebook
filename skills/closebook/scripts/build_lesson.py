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
import ast
import json
import math
import os
import re
import sys
from typing import Any, Callable, Dict, List

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
    "graph": {"contested", "factual"},
    "numeric": {"contested"},
    "order_steps": {"contested"},
    "code_trace": {"contested", "factual"},
    "terminal": {"contested", "judgment"},
}

# Expression grammar shared with the page (assets/lesson-template.html, compileExpr):
# numbers, variables, + - * / ^ (or **), parentheses, implicit multiplication (2x, 3(x+1)),
# the functions below and the constants pi and e.
FUNCS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan, "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sqrt": math.sqrt, "abs": abs, "exp": math.exp, "ln": math.log, "log": math.log10,
    "floor": math.floor, "ceil": math.ceil, "round": round, "min": min, "max": max, "pow": math.pow,
}
CONSTS = {"pi": math.pi, "e": math.e}
_TOKEN = re.compile(r"\s*(?:(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)|([A-Za-z_][A-Za-z0-9_]*)|(\*\*|[-+*/^(),×÷−·]))")


def compile_expr(src: str, names: List[str]) -> Callable[[Dict[str, float]], float]:
    """Compile an expression into a function of a name -> value dict. Raises ValueError."""
    tokens, pos, src = [], 0, str(src)
    while pos < len(src):
        if src[pos:].strip() == "":
            break
        m = _TOKEN.match(src, pos)
        if not m or m.end() == pos:
            raise ValueError("unexpected %r" % src[pos:].strip()[:10])
        num, ident, op = m.groups()
        if num is not None:
            tokens.append(("n", float(num)))
        elif ident is not None:
            tokens.append(("id", ident))
        else:
            tokens.append(("op", {"**": "^", "×": "*", "÷": "/", "−": "-", "·": "*"}.get(op, op)))
        pos = m.end()
    i = 0

    def is_op(v: str) -> bool:
        return i < len(tokens) and tokens[i] == ("op", v)

    def expect(v: str) -> None:
        nonlocal i
        if not is_op(v):
            raise ValueError("expected %s" % v)
        i += 1

    def starts_factor() -> bool:
        return i < len(tokens) and (tokens[i][0] in ("n", "id") or tokens[i] == ("op", "("))

    def expr():
        nonlocal i
        left = term()
        while is_op("+") or is_op("-"):
            op = tokens[i][1]
            i += 1
            a, b = left, term()
            left = (lambda a, b: lambda env: a(env) + b(env))(a, b) if op == "+" else (lambda a, b: lambda env: a(env) - b(env))(a, b)
        return left

    def term():
        nonlocal i
        left = unary()
        while True:
            if is_op("*") or is_op("/"):
                op = tokens[i][1]
                i += 1
                a, b = left, unary()
                left = (lambda a, b: lambda env: a(env) * b(env))(a, b) if op == "*" else (lambda a, b: lambda env: a(env) / b(env))(a, b)
            elif starts_factor():
                a, b = left, power()
                left = (lambda a, b: lambda env: a(env) * b(env))(a, b)
            else:
                return left

    def unary():
        nonlocal i
        if is_op("-"):
            i += 1
            a = unary()
            return lambda env: -a(env)
        if is_op("+"):
            i += 1
            return unary()
        return power()

    def power():
        nonlocal i
        base = atom()
        if is_op("^"):
            i += 1
            ex = unary()
            return lambda env: base(env) ** ex(env)
        return base

    def atom():
        nonlocal i
        if i >= len(tokens):
            raise ValueError("unexpected end")
        kind, val = tokens[i]
        i += 1
        if kind == "n":
            return lambda env: val
        if kind == "op" and val == "(":
            inner = expr()
            expect(")")
            return inner
        if kind == "id":
            if val in FUNCS and is_op("("):
                i += 1
                args = [expr()]
                while is_op(","):
                    i += 1
                    args.append(expr())
                expect(")")
                fn = FUNCS[val]
                return lambda env: fn(*[a(env) for a in args])
            if val in CONSTS:
                c = CONSTS[val]
                return lambda env: c
            if val in names:
                return lambda env: env[val]
            raise ValueError("unknown name %r" % val)
        raise ValueError("unexpected %r" % val)

    fn = expr()
    if i != len(tokens):
        raise ValueError("unexpected %r" % (tokens[i][1],))
    return fn


def _finite_somewhere(fn: Callable[[Dict[str, float]], float], env: Dict[str, float], xs: List[float]) -> bool:
    for x in xs:
        try:
            y = fn(dict(env, x=x))
        except (ArithmeticError, ValueError, TypeError):
            continue
        if isinstance(y, (int, float)) and math.isfinite(y):
            return True
    return False


def _blank_count(item: Dict[str, Any], kind: str) -> int:
    if kind == "compare_table_fill":
        return sum(1 for row in item.get("rows", []) for cell in row.get("cells", []) if cell.get("blank"))
    if kind == "timeline_fill":
        return sum(1 for ev in item.get("events", []) if ev.get("blank"))
    return sum(1 for node in item.get("nodes", []) if node.get("blank"))


CLOZE_BLANK = re.compile(r"\[\[(.*?)\]\]")


def _check_options(options: List[Dict[str, Any]], path: str, err: Callable[[str, str], None]) -> None:
    if sum(1 for o in options if o["correct"]) != 1:
        err(path, "needs exactly one correct option")
    if len({o["text"] for o in options}) != len(options):
        err(path, "duplicate option text")


def _check_params(item: Dict[str, Any], path: str, err: Callable[[str, str], None]) -> List[str]:
    params = item.get("params") or []
    if not params:
        err(path, "needs at least one param (slider)")
    names = []
    for k, p in enumerate(params):
        ppath = "%s.params[%d]" % (path, k)
        if p["name"] in ("x", "pi", "e") or p["name"] in FUNCS:
            err(ppath, "%r is reserved" % p["name"])
        if p["name"] in names:
            err(ppath, "duplicate param %s" % p["name"])
        if not p["min"] < p["max"]:
            err(ppath, "min must be below max")
        elif not p["min"] <= p["value"] <= p["max"]:
            err(ppath, "value is outside min..max")
        names.append(p["name"])
    return names + ["x"]


def _check_range(r: Any, path: str, err: Callable[[str, str], None]) -> bool:
    if not r or r[0] >= r[1]:
        err(path, "needs [min, max] with min < max")
        return False
    return True


def _check_curve(item: Dict[str, Any], names: List[str], env: Dict[str, float], path: str,
                 err: Callable[[str, str], None], warn: Callable[[str, str], None]) -> None:
    ok = _check_range(item.get("x_range"), path + ".x_range", err) & _check_range(item.get("y_range"), path + ".y_range", err)
    try:
        fn = compile_expr(item.get("expr") or "", names)
    except ValueError as exc:
        err(path + ".expr", "bad expression: %s" % exc)
        return
    if ok:
        lo, hi = item["x_range"]
        xs = [lo + (hi - lo) * k / 50 for k in range(51)]
        if not _finite_somewhere(fn, env, xs):
            warn(path + ".expr", "the curve has no finite points in x_range at the starting values")


def _sentences(text: str) -> int:
    return len([s for s in re.split(r"[!?。！？]+|\.(?=\s|$)", text) if s.strip()])


def _check_item(kind: str, item: Dict[str, Any], ipath: str,
                err: Callable[[str, str], None], warn: Callable[[str, str], None]) -> None:
    """Per-type rules for one item; also used for the check after a teaching chunk."""
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
        if item.get("params"):
            if not item.get("prompt"):
                err(ipath, "a parameter-lab simulation needs a prompt")
            names = _check_params(item, ipath, err)
            if not item.get("outputs") and not item.get("plot"):
                err(ipath, "simulation needs outputs (readouts) or a plot")
            env = {p["name"]: p["value"] for p in item["params"]}
            for k, o in enumerate(item.get("outputs") or []):
                try:
                    if not _finite_somewhere(compile_expr(o["expr"], names), env, [0.0]):
                        warn("%s.outputs[%d]" % (ipath, k), "expression isn't a finite number at the starting values")
                except ValueError as exc:
                    err("%s.outputs[%d].expr" % (ipath, k), "bad expression: %s" % exc)
            if item.get("plot"):
                _check_curve(item["plot"], names, env, ipath + ".plot", err, warn)
            if not item.get("predict"):
                err(ipath, "simulation needs a predict question: the learner commits before the sliders unlock")
            else:
                _check_options(item["predict"]["options"], ipath + ".predict", err)
        elif not item.get("fallback"):
            err(ipath, "simulation needs params (a parameter lab) or a fallback plain question")
    elif kind == "graph":
        if not item.get("prompt"):
            err(ipath, "graph needs a prompt")
        names = _check_params(item, ipath, err)
        env = {p["name"]: p["value"] for p in item.get("params") or []}
        _check_curve(item, names, env, ipath, err, warn)
        if bool(item.get("target")) == bool(item.get("predict")):
            err(ipath, "graph needs exactly one task: target (match the curve) or predict (answer, then explore)")
        if item.get("target"):
            target = item["target"]
            for p in item.get("params") or []:
                v = target.get(p["name"])
                if not isinstance(v, (int, float)) or isinstance(v, bool):
                    err(ipath + ".target", "needs a number for %s" % p["name"])
                elif not p["min"] <= v <= p["max"]:
                    err(ipath + ".target", "%s = %s is outside the slider range" % (p["name"], v))
            extra = set(target) - {p["name"] for p in item.get("params") or []}
            if extra:
                err(ipath + ".target", "unknown params: %s" % ", ".join(sorted(extra)))
            if all(target.get(p["name"]) == p["value"] for p in item.get("params") or []):
                err(ipath + ".target", "the sliders already start at the target")
        if item.get("predict"):
            _check_options(item["predict"]["options"], ipath + ".predict", err)
    elif kind == "numeric":
        if not item.get("question") or not isinstance(item.get("value"), (int, float)):
            err(ipath, "numeric needs question and value (a number)")
        if not item.get("solution") and not item.get("explanation"):
            warn(ipath, "numeric without solution steps: the learner sees only the final number")
    elif kind == "order_steps":
        steps = item.get("steps") or []
        if not item.get("prompt") or len(steps) < 3:
            err(ipath, "order_steps needs prompt and >= 3 steps")
        pool = steps + (item.get("distractors") or [])
        if len(set(pool)) != len(pool):
            err(ipath, "steps and distractors must all be different (identical items can't be told apart)")
        for k, alt in enumerate(item.get("alternatives") or []):
            if sorted(alt) != sorted(steps):
                err("%s.alternatives[%d]" % (ipath, k), "must use exactly the same items as steps")
    elif kind == "cloze_passage":
        text = item.get("text") or ""
        blanks = CLOZE_BLANK.findall(text)
        if not blanks or not item.get("prompt"):
            err(ipath, "cloze_passage needs a prompt and text with at least one [[answer]] blank")
        for b in blanks:
            if not [v for v in b.split("|") if v.strip()]:
                err(ipath, "empty blank [[]] in text")
    elif kind == "code_trace":
        code = item.get("code") or ""
        lines = len(code.split("\n"))
        if not code or not item.get("prompt") or not item.get("trace") or not item.get("questions"):
            err(ipath, "code_trace needs prompt, code, trace and questions")
        for k, step in enumerate(item.get("trace") or []):
            if step["line"] > lines:
                err("%s.trace[%d]" % (ipath, k), "line %d is past the end of the code (%d lines)" % (step["line"], lines))
    elif kind == "terminal":
        if not item.get("prompt") or not item.get("commands"):
            err(ipath, "terminal needs prompt and commands")


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
        chunks = teach.get("chunks") or []
        block = [teach.get("example", ""), teach.get("principle", "")] + teach.get("steps", [])
        if chunks and any(block):
            err(base + ".teach", "use either chunks or example/principle/steps, not both")
        elif len(" ".join(block).split()) > 180 or len("".join(block)) > 450:
            warn(base + ".teach", "teaching block is long; keep it to about 150 words (one example + one principle), "
                                  "or split it into chunks with checks")
        item_ids = set()
        for j, item in enumerate(kp["items"]):
            ipath = "%s.items[%d]" % (base, j)
            if item["id"] in item_ids:
                err(ipath + ".id", "duplicate item id %s" % item["id"])
            item_ids.add(item["id"])
            _check_item(kind, item, ipath, err, warn)
        if len(chunks) > 3:
            warn(base + ".teach.chunks", "more than 3 chunks; split the point into two points")
        if chunks and lesson.get("mode") == "review":
            warn(base + ".teach.chunks", "teaching chunks are shown only in learn mode")
        for c, chunk in enumerate(chunks):
            cpath = "%s.teach.chunks[%d]" % (base, c)
            text = [chunk["explain"], chunk.get("example", ""), chunk.get("analogy", ""), chunk.get("analogy_limit", "")]
            text += [s["do"] + " " + s.get("why", "") for s in chunk.get("worked") or []]
            if len(" ".join(text).split()) > 220 or len("".join(text)) > 500:
                warn(cpath, "chunk is long; one idea in about 80-200 words (400 Chinese characters), or split it")
            if chunk.get("analogy") and not chunk.get("analogy_limit"):
                err(cpath, "every analogy needs analogy_limit (where the comparison breaks)")
            if chunk.get("analogy") and ktype == "factual":
                warn(cpath, "factual point with an analogy; exact wording matters more than a comparison")
            if any(not s.get("why") for s in chunk.get("worked") or []):
                warn(cpath + ".worked", "worked steps without a why are a recipe; give each step its reason")
            check = chunk["check"]
            if check["id"] in item_ids:
                err(cpath + ".check.id", "duplicate item id %s (checks share ids with the point's items)" % check["id"])
            item_ids.add(check["id"])
            _check_item(chunk["check_type"], check, cpath + ".check", err, warn)

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


_TRACE_BUILTINS = {
    "abs", "all", "any", "bool", "chr", "dict", "divmod", "enumerate", "float", "int", "len", "list",
    "max", "min", "ord", "pow", "print", "range", "reversed", "round", "set", "sorted", "str", "sum", "tuple", "zip",
}
_TRACE_METHODS = {
    "append", "extend", "insert", "pop", "remove", "clear", "reverse", "sort", "count", "index", "copy",
    "get", "keys", "values", "items", "update", "add", "discard", "union", "intersection", "difference",
    "split", "join", "strip", "lstrip", "rstrip", "lower", "upper", "replace", "startswith", "endswith",
}
_TRACE_AST = {
    "Module", "Expr", "Assign", "AugAssign", "Name", "Load", "Store", "Constant", "Num", "Str", "NameConstant",
    "List", "Tuple", "Set", "Dict", "Subscript", "Slice", "Index", "ExtSlice", "BinOp", "UnaryOp", "BoolOp",
    "Compare", "IfExp", "Add", "Sub", "Mult", "Div", "FloorDiv", "Mod", "Pow", "UAdd", "USub", "Not",
    "And", "Or", "Eq", "NotEq", "Lt", "LtE", "Gt", "GtE", "Is", "IsNot", "In", "NotIn", "BitAnd", "BitOr",
    "BitXor", "LShift", "RShift", "Invert", "If", "For", "While", "Break", "Continue", "Pass", "FunctionDef",
    "arguments", "arg", "Return", "Call", "keyword", "Attribute", "ListComp", "SetComp", "DictComp", "comprehension",
    "JoinedStr", "FormattedValue",
}


def check_python_subset(code: str) -> None:
    """Reject unsupported constructs before executing the small teaching subset.

    This is deliberately not a general-purpose Python sandbox. No imports, I/O
    except captured print(), reflection, classes, attribute chains or deletion.
    """
    if len(code) > 50000:
        raise ToolError("unsupported Python trace: code is longer than 50000 characters")
    tree = ast.parse(code)
    nodes = list(ast.walk(tree))
    if len(nodes) > 2000:
        raise ToolError("unsupported Python trace: more than 2000 syntax nodes")
    functions = {node.name for node in nodes if isinstance(node, ast.FunctionDef)}
    for node in nodes:
        reason = None
        if type(node).__name__ not in _TRACE_AST:
            reason = type(node).__name__
        elif isinstance(node, ast.Name) and node.id.startswith("_"):
            reason = "private/dunder names"
        elif isinstance(node, ast.arg) and (node.arg.startswith("_") or node.annotation is not None):
            reason = "private arguments or annotations"
        elif isinstance(node, ast.FunctionDef) and (
                node.name.startswith("_") or node.decorator_list or node.returns is not None):
            reason = "private functions, decorators or annotations"
        elif isinstance(node, ast.Attribute) and (
                not isinstance(node.value, ast.Name) or node.attr not in _TRACE_METHODS or not isinstance(node.ctx, ast.Load)):
            reason = "only listed container/string methods on a simple variable are supported"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id not in _TRACE_BUILTINS | functions:
                    reason = "call to %s" % node.func.id
            elif not isinstance(node.func, ast.Attribute):
                reason = "indirect function calls"
            if any(kw.arg is None or kw.arg.startswith("_") or kw.arg == "file" for kw in node.keywords):
                reason = "keyword expansion, private keywords or print(file=...)"
        elif isinstance(node, ast.comprehension) and node.is_async:
            reason = "async comprehensions"
        if reason:
            raise ToolError("unsupported Python trace at line %s: %s; use a small pure teaching example and check other code manually"
                            % (getattr(node, "lineno", "?"), reason))


_TRACE_RUNNER = r'''
import builtins, io, json, sys
try:
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
except (ImportError, ValueError, OSError):
    pass
class Output(io.StringIO):
    def write(self, s):
        if self.tell() + len(s) > 131072:
            raise RuntimeError("more than 128 KiB of output")
        return super().write(s)
events, out, snapshot_size, frames = [], Output(), 0, []
def visible(frame):
    cursor = frame
    while cursor is not None and cursor.f_code.co_filename == "<lesson>":
        if cursor.f_code.co_name in ("<listcomp>", "<setcomp>", "<dictcomp>", "<genexpr>"):
            return False
        cursor = cursor.f_back
    return frame.f_code.co_filename == "<lesson>"
def snap(frame):
    global snapshot_size
    d = {}
    for k, v in list(frame.f_locals.items()):
        if k.startswith("_") or callable(v):
            continue
        try:
            # Freeze mutable containers now, not when the entire run is serialized.
            d[k] = [json.loads(json.dumps(v)), repr(v)]
        except (TypeError, ValueError):
            d[k] = [None, repr(v)]
    snapshot_size += len(json.dumps(d))
    if snapshot_size > 2 * 1024 * 1024:
        raise RuntimeError("more than 2 MiB of variable snapshots")
    return d
def tracer(frame, event, arg):
    if not visible(frame):
        return None
    if event == "call":
        frames.append(frame)  # Keep frame ids distinct across successive calls.
    if event in ("line", "return"):
        if len(events) > 5000:
            sys.settrace(None)
            raise RuntimeError("more than 5000 steps")
        ev = {"line": frame.f_lineno if event == "line" else None, "frame": id(frame), "vars": snap(frame), "out": len(out.getvalue())}
        caller = frame.f_back
        if event == "return" and caller is not None and visible(caller):
            ev["caller"] = [id(caller), caller.f_lineno, snap(caller)]
        events.append(ev)
    return tracer
request = json.loads(sys.stdin.read())
code = compile(request["code"], "<lesson>", "exec")
safe_builtins = {name: getattr(builtins, name) for name in request["builtins"]}
real, error = sys.stdout, None
sys.stdout = out
sys.settrace(tracer)
try:
    exec(code, {"__name__": "__main__", "__builtins__": safe_builtins})
except BaseException as exc:
    error = "%s: %s" % (type(exc).__name__, exc)
finally:
    sys.settrace(None)
    sys.stdout = real
print(json.dumps({"events": events, "out": out.getvalue(), "error": error}))
'''


def run_python_trace(code: str, timeout: float = 5.0) -> Dict[str, Any]:
    """Run code in a separate interpreter and return one entry per executed line:
    {line, after (variables once the line has run, name -> [json value, repr]), out (text it printed)}."""
    import subprocess
    import tempfile
    check_python_subset(code)
    with tempfile.TemporaryDirectory(prefix="closebook-trace-") as directory:
        proc = subprocess.run([sys.executable, "-I", "-B", "-c", _TRACE_RUNNER],
                              input=json.dumps({"code": code, "builtins": sorted(_TRACE_BUILTINS)}),
                              capture_output=True, text=True, timeout=timeout, cwd=directory)
    if proc.returncode != 0:
        raise ToolError("could not run the code: %s" % proc.stderr.strip().splitlines()[-1:])
    raw = json.loads(proc.stdout)
    events, text = raw["events"], raw["out"]
    steps, seen_frames = [], set()
    for i, ev in enumerate(events):
        if ev["line"] is None:
            if "caller" in ev:
                # "back in the caller": optional step some traces show after a function returns
                fid, line, before = ev["caller"]
                nxt = next((e for e in events[i + 1:] if e["frame"] == fid), None)
                steps.append({"line": line, "before": before, "after": nxt["vars"] if nxt else before,
                              "frame": fid, "out": "", "optional": True})
            continue
        next_index = next((n for n in range(i + 1, len(events)) if events[n]["frame"] == ev["frame"]), None)
        nxt = events[next_index] if next_index is not None else None
        # A call first enters its function. The assignment completes at the
        # optional caller-return entry, which may be merged into the next line.
        enters_function = next_index is not None and next_index > i + 1
        out_end = events[i + 1]["out"] if i + 1 < len(events) else len(text)
        steps.append({"line": ev["line"], "frame": ev["frame"],
                      "before": ev["vars"] if ev["frame"] in seen_frames else {},
                      "after": ev["vars"] if enters_function or nxt is None else nxt["vars"],
                      "out": text[ev["out"]:out_end]})
        seen_frames.add(ev["frame"])
    loop_bodies = {
        node.lineno: (node.body[0].lineno, getattr(node.body[-1], "end_lineno", node.body[-1].lineno))
        for node in ast.walk(ast.parse(code)) if isinstance(node, (ast.For, ast.While))
    }
    for i, step in enumerate(steps):
        if step["line"] not in loop_bodies or step["before"] != step["after"] or step["out"]:
            continue
        following = next((other for other in steps[i + 1:] if other["frame"] == step["frame"]), None)
        first, last = loop_bodies[step["line"]]
        if following is None or (following["line"] != step["line"] and not first <= following["line"] <= last):
            step["optional_loop_exit"] = True
    return {"steps": steps, "out": text, "error": raw["error"]}


def _same_value(claimed: Any, real: List[Any]) -> bool:
    _, shown = real
    # JSON turns tuples into lists and integer dictionary keys into strings.
    # Reconstruct only literal values from the frozen repr to retain Python types.
    try:
        value = ast.literal_eval(shown)
    except (ValueError, SyntaxError):
        return isinstance(claimed, str) and claimed == shown

    def equal(left, right):
        if isinstance(left, (int, float)) and not isinstance(left, bool) and isinstance(right, (int, float)) \
                and not isinstance(right, bool):
            if left == right or isinstance(right, int):
                return left == right  # Integers have no rounding allowance.
            try:
                return abs(left - right) <= 1e-9 * max(1.0, abs(right))
            except OverflowError:
                return False
        if type(left) is not type(right):
            return False
        if isinstance(left, (list, tuple)):
            return len(left) == len(right) and all(equal(a, b) for a, b in zip(left, right))
        if isinstance(left, dict):
            return len(left) == len(right) and all(
                any(type(key) is type(other) and key == other and equal(val, right[other]) for other in right)
                for key, val in left.items())
        if isinstance(left, (set, frozenset)):
            return len(left) == len(right) and all(any(type(a) is type(b) and a == b for b in right) for a in left)
        return left == right

    if isinstance(claimed, str):
        if claimed == shown or (isinstance(value, str) and claimed == value):
            return True
        try:
            claimed = ast.literal_eval(claimed)
        except (ValueError, SyntaxError):
            return False
    return equal(claimed, value)


def verify_trace(item: Dict[str, Any], timeout: float = 5.0) -> List[str]:
    """Compare a code_trace item's trace with a real run. Python only. Returns problems (empty = matches)."""
    try:
        run = run_python_trace(item.get("code") or "", timeout)
    except Exception as exc:  # timeouts, syntax errors, interpreter failures
        return ["the code didn't run: %s" % exc]
    real, problems, j = run["steps"], [], 0
    if run["error"]:
        problems.append("the code raises %s" % run["error"])
    shown, stale = {}, set()  # what the page's variable table displays so far

    def changes(actual):
        return [name for name, value in actual["after"].items() if actual["before"].get(name) != value]

    def skipped(actual, where, tail=False):
        if actual["out"]:
            problems.append("%s: the trace skips line %d, which prints %r"
                            % (where, actual["line"], actual["out"].rstrip("\n")))
        changed = changes(actual)
        if changed and (not actual.get("optional") or tail):
            problems.append("%s: line %d changes %s; a step that changes it is missing"
                            % (where, actual["line"], ", ".join(changed)))
        elif not actual.get("optional") and not actual.get("optional_loop_exit"):
            problems.append("%s: line %d executes but is missing; only the final unchanged loop check may be omitted"
                            % (where, actual["line"]))

    for k, step in enumerate(item.get("trace") or []):
        while j < len(real) and real[j]["line"] != step["line"]:
            skipped(real[j], "step %d" % (k + 1))
            j += 1
        if j >= len(real):
            problems.append("step %d: line %d doesn't run at this point" % (k + 1, step["line"]))
            return problems
        here = real[j]["after"]
        for name, claimed in (step.get("vars") or {}).items():
            shown[name] = claimed
            if name not in here:
                problems.append("step %d (line %d): no variable %s exists here" % (k + 1, step["line"], name))
            elif not _same_value(claimed, here[name]):
                stale.add(name)
                problems.append("step %d (line %d): %s is %s after this line, the trace says %s"
                                % (k + 1, step["line"], name, here[name][1], json.dumps(claimed, ensure_ascii=False)))
            else:
                stale.discard(name)
        for name in here:
            if name not in shown:
                problems.append("step %d (line %d): the trace omits new variable %s = %s"
                                % (k + 1, step["line"], name, here[name][1]))
        for name, claimed in shown.items():
            if name in here and name not in (step.get("vars") or {}) and name not in stale and not _same_value(claimed, here[name]):
                stale.add(name)
                problems.append("step %d (line %d): the page still shows %s = %s, but it is %s by now (a step that changes it is missing)"
                                % (k + 1, step["line"], name, json.dumps(claimed, ensure_ascii=False), here[name][1]))
        output = real[j]["out"]
        printed = output[:-1] if output.endswith("\n") else output
        if printed != step.get("out", "") or (bool(output) != ("out" in step)):
            problems.append("step %d (line %d): prints %r, the trace says %r" % (k + 1, step["line"], printed, step.get("out") or ""))
        j += 1
    for actual in real[j:]:
        skipped(actual, "the trace ends too early", tail=True)
    displayed_output = "\n".join(step["out"] for step in item.get("trace", []) if "out" in step)
    expected_output = run["out"][:-1] if run["out"].endswith("\n") else run["out"]
    if displayed_output != expected_output:
        problems.append("the page's complete output %r differs from the real output %r" % (displayed_output, expected_output))
    return problems


def check_code(lesson: Dict[str, Any], timeout: float = 5.0) -> List[Issue]:
    """Run supported Python traces; natural-language prediction answers are not inferred."""
    issues = []
    for i, kp in enumerate(lesson.get("knowledge_points") or []):
        if kp.get("interaction_type") != "code_trace":
            continue
        for j, item in enumerate(kp.get("items") or []):
            path = "$.knowledge_points[%d].items[%d]" % (i, j)
            if not re.match(r"(python|py)\s*3?(\.\d+)*$", str(item.get("language", "")).strip().lower()):
                issues.append(Issue("warning", path, "only Python traces can be run; check this one by hand", "code"))
                continue
            for problem in verify_trace(item, timeout):
                issues.append(Issue("error", path + ".trace", problem, "code"))
    return issues


def embed(lesson: Dict[str, Any], template_text: str) -> str:
    # "</" would close the data block early. "<!--" followed later by "<script"
    # puts the HTML parser into a state where the real </script> is ignored and
    # the page script is swallowed, so escape its "<" as a JSON unicode escape.
    payload = json.dumps(lesson, ensure_ascii=False, indent=2).replace("</", "<\\/").replace("<!--", "\\u003c!--")
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
    parser.add_argument("--run-code", action="store_true",
                        help="compatibility flag: Python traces are now checked on every build (5 s limit)")
    args = parser.parse_args(argv)
    try:
        if args.lesson.endswith(".html"):
            with open(args.lesson, encoding="utf-8") as fh:
                lesson = extract(fh.read())
        else:
            lesson = load_json(args.lesson)
        issues = check_lesson(lesson)
        if not any(i.severity == "error" for i in issues):
            issues += check_code(lesson)
        for issue in issues:
            print(repr(issue), file=sys.stderr)
        errors = [i for i in issues if i.severity == "error" or (args.strict and i.severity == "warning")]
        if errors:
            print("lesson data: INVALID (%d errors)" % len(errors), file=sys.stderr)
            return 1
        print("lesson data: VALID (%d warnings)" % len(issues), file=sys.stderr)
        if any(kp.get("interaction_type") == "code_trace" for kp in lesson.get("knowledge_points", [])):
            print("trace check covers supported Python execution steps, variables and output; "
                  "prediction answers and other languages need independent review", file=sys.stderr)
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
