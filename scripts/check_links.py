#!/usr/bin/env python3
"""check_links: every relative markdown link must resolve inside the skill root.

Red line: dangling links must be 0. Run after any add/move/delete of .md files.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

from _common import skill_root

LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
SKIP = ("http://", "https://", "mailto:", "#", "local://", "sms:")


def md_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "tmp", "__pycache__")]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def check(root):
    bad = []
    total = 0
    for path in md_files(root):
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
        for _, target in LINK.findall(text):
            clean = target.split(" ", 1)[0].strip()
            if not clean or clean.startswith(SKIP):
                continue
            total += 1
            clean = clean.split("#", 1)[0]
            if not clean:
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), clean))
            if not os.path.exists(resolved):
                bad.append("%s -> %s" % (os.path.relpath(path, root), target))
    return total, bad


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--root", default=skill_root())
    argp.add_argument("--dry-run", action="store_true", help="report only (default)")
    args = argp.parse_args()
    total, bad = check(os.path.abspath(args.root))
    print("markdown links checked: %d" % total)
    for line in bad:
        print("DANGLING %s" % line)
    print("dangling: %d" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
