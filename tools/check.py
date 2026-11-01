#!/usr/bin/env python3
"""Run Python, packaging and MCP checks. Browser skips fail unless explicitly excluded."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
BROWSER_MODULE = "test_lesson_page_e2e.py"


def run_command(label, command, *, quiet=False):
    print("\n" + label, flush=True)
    result = subprocess.run(command, cwd=str(ROOT), text=True,
                            stdout=subprocess.PIPE if quiet else None,
                            stderr=subprocess.STDOUT if quiet else None)
    if quiet:
        if result.returncode:
            print(result.stdout, end="")
        else:
            print("Passed.")
    return result.returncode == 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-browser", action="store_true",
                        help="explicitly exclude HTML browser tests; report a partial check")
    args = parser.parse_args(argv)
    os.chdir(str(ROOT))
    npm = shutil.which("npm")
    if npm is None or not (ROOT / "mcp/node_modules").is_dir():
        parser.error("MCP dependencies are missing. Install Node.js 20+ and run npm ci --prefix mcp --loglevel=error first.")
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    tests = ROOT / "tests"
    for path in sorted(tests.glob("test_*.py")):
        if args.skip_browser and path.name == BROWSER_MODULE:
            continue
        suite.addTests(loader.discover(str(tests), pattern=path.name))
    if args.skip_browser:
        print("PARTIAL CHECK: HTML browser tests explicitly excluded (--skip-browser).", flush=True)
    else:
        print("Full check: browser tests must run; any skipped test fails this command.", flush=True)
    # Keep generated test files beside the checkout, including subprocess tests.
    with tempfile.TemporaryDirectory(prefix=".closebook-check-", dir=str(ROOT)) as directory:
        tempfile.tempdir = directory
        for key in ("TMPDIR", "TMP", "TEMP"):
            os.environ[key] = directory
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        python_ok = result.wasSuccessful() and not result.skipped
        if result.skipped:
            print("FAILED: tests were skipped; install their dependencies or explicitly use --skip-browser.", file=sys.stderr)
        package_ok = run_command("Skill package contents", [sys.executable, "tools/package_skill.py", "--check"], quiet=True)
        mcp_ok = run_command("MCP build and tests", [npm, "--prefix", "mcp", "test"])
    passed = python_ok and package_ok and mcp_ok
    print("\n" + ("Partial checks passed; browser validation remains outstanding." if args.skip_browser and passed
                   else "All checks passed." if passed else "Checks failed."))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
