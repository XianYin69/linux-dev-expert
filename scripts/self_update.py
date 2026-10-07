#!/usr/bin/env python3
"""self_update: the only write channel for the skill body (tmp mirror -> release).

Flow: stage in tmp/ -> compare -> release --yes. resistance/ files are protected.
"""
from __future__ import annotations

import argparse
import difflib
import os
import shutil
import sys

from _common import skill_root

PROTECTED = ("resistance",)


def staged(root):
    tmp = os.path.join(root, "tmp")
    out = []
    if not os.path.isdir(tmp):
        return out
    for dirpath, _, filenames in os.walk(tmp):
        for name in filenames:
            full = os.path.join(dirpath, name)
            out.append(os.path.relpath(full, tmp).replace("\\", "/"))
    return out


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("action", choices=("stage", "compare", "release", "clean"))
    argp.add_argument("--yes", action="store_true")
    args = argp.parse_args()
    root = skill_root()
    items = staged(root)
    if args.action == "stage":
        print("staged in tmp/: %d" % len(items))
        for item in items:
            print("  %s" % item)
        return 0
    if args.action == "clean":
        for item in items:
            path = os.path.join(root, "tmp", item)
            print("%s %s" % ("drop" if args.yes else "would drop", item))
            if args.yes:
                os.remove(path)
        return 0
    for item in items:
        src = os.path.join(root, "tmp", item)
        dest = os.path.join(root, item)
        rel = os.path.relpath(dest, root)
        if any(rel.startswith(p) for p in PROTECTED):
            print("SKIP protected constraint file: %s" % rel)
            continue
        old = open(dest, "r", encoding="utf-8").read().splitlines() \
            if os.path.exists(dest) else []
        new = open(src, "r", encoding="utf-8").read().splitlines()
        diff = list(difflib.unified_diff(old, new, rel, rel, lineterm="", n=1))
        print("=== %s (%s)" % (rel, "changed" if diff else "identical"))
        for line in diff[:20]:
            print(line)
        if args.action == "release" and args.yes and diff:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(src, dest)
            print("released: %s" % rel)
    if args.action == "release" and not args.yes:
        print("dry-run only: add --yes to write (不得静默写盘)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
