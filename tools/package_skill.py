#!/usr/bin/env python3
"""Package skills/closebook into the one upload-ready ZIP (Python 3.8+, standard library only).

    python3 tools/package_skill.py            # writes dist/closebook.zip
    python3 tools/package_skill.py --check    # list what would be packaged, write nothing

The ZIP is the upload package for chat apps (claude.ai, ChatGPT, Gemini Apps). Its
root is the `closebook/` folder (required by claude.ai). It leaves out development
files (evals, caches, macOS metadata) and two things some chat apps refuse:
`agents/openai.yaml` (`.yaml` isn't on Gemini's upload list) and `assets/` (the
HTML page template: ChatGPT's skill scan refuses any file containing JavaScript,
checked 2026-11-01). Installs that copy the `skills/closebook` directory (Codex
CLI/IDE, Claude Code, Gemini CLI, Hermes) keep both. Timestamps are fixed so the
same sources always produce the same bytes.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile
from typing import List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(ROOT, "skills", "closebook")
DIST = os.path.join(ROOT, "dist")
NAME = "closebook"
EXCLUDED_DIRS = {"evals", "__pycache__", ".git"}
UPLOAD_SKIPS = {"agents", "assets"}
JUNK = re.compile(r"(^\._|^\.DS_Store$|\.pyc$|^Thumbs\.db$|~$)")
FIXED_TIME = (2026, 1, 1, 0, 0, 0)
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def collect(skip_dirs=()) -> List[str]:
    files = []
    for dirpath, dirnames, filenames in os.walk(SKILL_DIR):
        rel_dir = os.path.relpath(dirpath, SKILL_DIR)
        dirnames[:] = sorted(d for d in dirnames
                             if d not in EXCLUDED_DIRS and not d.startswith(".")
                             and os.path.normpath(os.path.join(rel_dir, d)) not in skip_dirs)
        for name in sorted(filenames):
            if JUNK.search(name):
                continue
            files.append(os.path.normpath(os.path.join(rel_dir, name)))
    return files


def check_frontmatter() -> None:
    with open(os.path.join(SKILL_DIR, "SKILL.md"), encoding="utf-8") as fh:
        text = fh.read()
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise SystemExit("SKILL.md has no frontmatter")
    keys = set(re.findall(r"^([A-Za-z][\w-]*):", match.group(1), re.M))
    if keys - ALLOWED_KEYS:
        raise SystemExit("frontmatter keys not accepted everywhere: %s" % sorted(keys - ALLOWED_KEYS))
    name = re.search(r"^name:\s*(\S+)", match.group(1), re.M)
    if not name or name.group(1) != NAME:
        raise SystemExit("frontmatter name must be %r" % NAME)


def write_zip(path: str, files: List[str]) -> int:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in files:
            info = zipfile.ZipInfo("%s/%s" % (NAME, rel.replace(os.sep, "/")), FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if rel.endswith(".py") else 0o644) << 16
            with open(os.path.join(SKILL_DIR, rel), "rb") as fh:
                zf.writestr(info, fh.read())
    os.replace(tmp, path)
    return os.path.getsize(path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Package the closebook skill")
    parser.add_argument("--check", action="store_true", help="list files only")
    parser.add_argument("--out", default=DIST, help="output directory (default: dist/)")
    args = parser.parse_args(argv)
    check_frontmatter()
    builds = [("closebook.zip", collect(skip_dirs=UPLOAD_SKIPS))]
    for filename, files in builds:
        if args.check:
            print("%s (%d files)" % (filename, len(files)))
            for rel in files:
                print("  " + rel)
            continue
        size = write_zip(os.path.join(args.out, filename), files)
        print("wrote %s: %d files, %.1f KB" % (os.path.join(args.out, filename), len(files), size / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
