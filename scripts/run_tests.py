#!/usr/bin/env python3
"""run_tests: compile every script, smoke-run each probe, check md line limits.

Exit non-zero on any failure; used by the 整体审查 step.
"""
from __future__ import annotations

import glob
import os
import py_compile
import subprocess
import sys

from _common import cache_dir, skill_root

LIMIT = 50


def compile_all(root):
    bad = []
    for path in glob.glob(os.path.join(root, "scripts", "*.py")):
        try:
            py_compile.compile(path, doraise=True, cfile=os.path.join(
                cache_dir(), os.path.basename(path) + ".check"))
        except py_compile.PyCompileError as exc:
            bad.append("%s: %s" % (os.path.basename(path), exc.msg.splitlines()[0]))
    return bad


def md_limits(root):
    bad = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "tmp", "__pycache__")]
        for name in filenames:
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, "r", encoding="utf-8") as handle:
                count = sum(1 for _ in handle)
            if count > LIMIT:
                bad.append("%s=%d" % (os.path.relpath(path, root), count))
    return bad


def smoke(root):
    bad = []
    for path in sorted(glob.glob(os.path.join(root, "scripts", "probe_*.py"))):
        proc = subprocess.run([sys.executable, "-B", path, "--json"],
                              capture_output=True, text=True, timeout=90)
        if proc.returncode != 0:
            bad.append("%s rc=%d %s" % (os.path.basename(path), proc.returncode,
                                        (proc.stderr or "").strip()[:120]))
    return bad


def main():
    root = skill_root()
    print("skill root: %s" % root)
    results = {
        "compile": compile_all(root),
        "md_over_50_lines": md_limits(root),
        "probe_smoke": smoke(root),
    }
    failed = 0
    for key, items in results.items():
        print("%s: %s" % (key, "ok" if not items else "FAIL"))
        for item in items:
            print("   - %s" % item)
        failed += len(items)
    print("total problems: %d" % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
