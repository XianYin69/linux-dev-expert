#!/usr/bin/env python3
"""penalty: count repeated failures per signature and trip the 10-retry fuse.

Fused -> stop the current approach: roll back or ask the user (惩罚机制).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from _common import cache_dir

PATH = os.path.join(cache_dir(), "penalty.json")
LIMIT = 10


def load():
    if not os.path.exists(PATH):
        return {}
    with open(PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save(data):
    tmp = PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    os.replace(tmp, PATH)


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("action", choices=("bump", "reset", "status"))
    argp.add_argument("--sig", default="general")
    args = argp.parse_args()
    data = load()
    if args.action == "reset":
        data.pop(args.sig, None)
        save(data)
        print("reset %s" % args.sig)
        return 0
    if args.action == "status":
        for key, val in sorted(data.items()):
            print("%s: %d/%d %s" % (key, val.get("count", 0), LIMIT,
                                    "FUSED" if val.get("fused") else ""))
        if not data:
            print("no penalties recorded")
        return 0
    entry = data.get(args.sig, {"count": 0, "fused": False})
    entry["count"] = int(entry.get("count", 0)) + 1
    entry["last"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    entry["fused"] = entry["count"] >= LIMIT
    data[args.sig] = entry
    save(data)
    print("%s: %d/%d" % (args.sig, entry["count"], LIMIT))
    if entry["fused"]:
        print("FUSED - stop retrying: root-cause first, then roll back or ask user")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
