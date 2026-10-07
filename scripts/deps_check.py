#!/usr/bin/env python3
"""deps_check: validate dependence/deps.json against the source_url red line.

Every entry needs name/source_url/license/version/install/checked_at;
local skills must exist on disk; software entries need an upstream URL.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from _common import skill_root

REQUIRED = ("name", "source_url", "license", "version", "install", "checked_at")
SKILLS_ROOT = os.path.normpath(os.path.join(skill_root(), os.pardir))


def validate(entry):
    problems = []
    for field in REQUIRED:
        if not str(entry.get(field, "")).strip():
            problems.append("missing-field:%s" % field)
    url = str(entry.get("source_url", ""))
    kind = entry.get("type", "skill")
    if url.startswith("local://"):
        target = os.path.join(SKILLS_ROOT, url[len("local://"):])
        if not os.path.isdir(target):
            problems.append("local-skill-absent:%s" % target)
    elif kind == "software" and not url.startswith(("http://", "https://", "ftp://")):
        problems.append("software-needs-upstream-url")
    elif not url:
        problems.append("empty-source_url")
    return problems


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--file", default=os.path.join(skill_root(), "dependence",
                                                    "deps.json"))
    args = argp.parse_args()
    if not os.path.exists(args.file):
        print("error: deps.json not found at %s" % args.file)
        return 2
    with open(args.file, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    entries = data.get("dependencies", [])
    if not entries:
        print("error: no dependencies declared")
        return 2
    failed = 0
    for entry in entries:
        problems = validate(entry)
        tag = "OK  " if not problems else "FAIL"
        print("%s %-22s %s" % (tag, entry.get("name", "?"),
                               entry.get("source_url", "-")))
        for problem in problems:
            print("     - %s" % problem)
        failed += bool(problems)
    print("dependencies: %d, failing: %d" % (len(entries), failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
