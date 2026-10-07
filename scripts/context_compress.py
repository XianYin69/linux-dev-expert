#!/usr/bin/env python3
"""context_compress: measure md/script size pressure and suggest what to drop.

Priority order for dropping: red lines > judgement criteria > examples.
"""
from __future__ import annotations

import argparse
import os
import sys

from _common import skill_root

LIMIT = 50
LONG_LINE = 100


def scan(root):
    rows = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "tmp", "__pycache__")]
        for name in filenames:
            path = os.path.join(dirpath, name)
            if not name.endswith((".md", ".py")):
                continue
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    lines = handle.read().splitlines()
            except OSError:
                continue
            over = [i + 1 for i, line in enumerate(lines) if len(line) > LONG_LINE]
            rows.append((os.path.relpath(path, root), len(lines), over))
    return rows


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--budget", type=int, default=2000, help="line budget")
    argp.add_argument("--strict", action="store_true", help="fail on any violation")
    args = argp.parse_args()
    rows = scan(skill_root())
    total = sum(count for _, count, _ in rows)
    print("files=%d lines=%d budget=%d" % (len(rows), total, args.budget))
    bad = 0
    for rel, count, over in sorted(rows, key=lambda r: -r[1]):
        flags = []
        if rel.endswith(".md") and count > LIMIT:
            flags.append("OVER-50")
        if over:
            flags.append("LONG-LINES@%s" % ",".join(map(str, over[:4])))
        if flags:
            bad += 1
            print("%-52s %4d %s" % (rel, count, " ".join(flags)))
    print("violations=%d" % bad)
    if total > args.budget:
        print("hint: drop examples first, then merge leaves; keep red lines intact")
    return 1 if (args.strict and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
