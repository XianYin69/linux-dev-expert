#!/usr/bin/env python3
"""process_chain: track the creation/modification flow, interrupts and resume.

Six actions: start / step / interrupt / resume / finish / show.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from _common import cache_dir

PATH = os.path.join(cache_dir(), "process_chain.jsonl")
CREATE = ("初始化", "需求确认", "经验查询", "大纲构建", "分支分析", "脚本构建",
          "知识库构建", "约束编写", "整体审查", "收尾")


def append(entry):
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load():
    if not os.path.exists(PATH):
        return []
    out = []
    for line in open(PATH, "r", encoding="utf-8"):
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("action", choices=("start", "step", "interrupt", "resume",
                                         "finish", "show", "plan"))
    argp.add_argument("--path", default="create", choices=("create", "modify"))
    argp.add_argument("name", nargs="?", default="")
    argp.add_argument("--reason", default="")
    argp.add_argument("--at", default="")
    args = argp.parse_args()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    if args.action == "plan":
        for idx, name in enumerate(CREATE, 1):
            print("%2d %s" % (idx, name))
        return 0
    if args.action == "show":
        done = {e.get("step") for e in load() if e.get("kind") == "step"}
        for name in CREATE:
            print("%s %s" % ("done" if name in done else "TODO", name))
        for entry in load()[-8:]:
            print("  %s" % json.dumps(entry, ensure_ascii=False))
        return 0
    if args.action in ("start", "finish"):
        append({"ts": stamp, "kind": args.action, "path": args.path,
                "name": args.name})
        print("%s recorded (%s)" % (args.action, args.path))
        return 0
    if args.action == "interrupt":
        append({"ts": stamp, "kind": "interrupt", "step": args.at or args.name,
                "reason": args.reason})
        print("interrupt recorded at %s" % (args.at or args.name))
        return 0
    if not args.name:
        print("error: %s needs a step name" % args.action)
        return 2
    append({"ts": stamp, "kind": args.action, "step": args.name})
    print("%s: %s" % (args.action, args.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
