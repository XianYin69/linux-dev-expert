#!/usr/bin/env python3
"""garbage_collect: audit tmp/ and cache leakage, release staged files on demand.

Red line: caches never live in the skill directory; tmp/ is emptied at wrap-up.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys

from _common import cache_dir, skill_root

STAGED = ("*.tmp", "*.bak", "probe-*.json", "draft-*.md")


def audit(root):
    problems = []
    tmp = os.path.join(root, "tmp")
    staged = []
    if os.path.isdir(tmp):
        for dirpath, _, filenames in os.walk(tmp):
            for name in filenames:
                staged.append(os.path.relpath(os.path.join(dirpath, name), root))
    for name in os.listdir(root):
        if name.endswith((".log", ".pyc")) or name in (".DS_Store",):
            problems.append("stray-file:%s" % name)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "tmp")]
        for name in filenames:
            if name.endswith((".log", ".pyc")) or name.startswith("cache"):
                problems.append("cache-in-skill:%s" %
                                os.path.relpath(os.path.join(dirpath, name), root))
    return problems, staged


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("action", choices=("audit", "release", "clean"), default="audit",
                      nargs="?")
    argp.add_argument("--yes", action="store_true", help="actually move/delete")
    args = argp.parse_args()
    root = skill_root()
    problems, staged = audit(root)
    print("cache dir: %s" % cache_dir())
    for item in staged:
        print("staged: %s" % item)
    for item in problems:
        print("problem: %s" % item)
    if args.action == "release" and staged:
        for item in staged:
            src = os.path.join(root, item)
            dest = os.path.join(root, os.path.basename(item))
            print("%s %s -> %s" % ("release" if args.yes else "would release",
                                   item, os.path.relpath(dest, root)))
            if args.yes:
                shutil.move(src, dest)
    if args.action == "clean":
        tmp = os.path.join(root, "tmp")
        print("%s %s" % ("clean" if args.yes else "would clean", tmp))
        if args.yes and os.path.isdir(tmp):
            shutil.rmtree(tmp, ignore_errors=True)
    print("staged=%d problems=%d" % (len(staged), len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
