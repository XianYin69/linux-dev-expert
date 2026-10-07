#!/usr/bin/env python3
"""logic_chain: record decisions (from -> to, why) and run pro/con debates.

Storage is the user cache dir, never the skill directory (垃圾回收机制).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from _common import cache_dir

PATH = os.path.join(cache_dir(), "logic_chain.jsonl")


def append(entry):
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("action", choices=("add", "debate", "last", "show"))
    argp.add_argument("--from", dest="frm", default="")
    argp.add_argument("--to", default="")
    argp.add_argument("--why", default="")
    argp.add_argument("--claim", default="")
    argp.add_argument("--pro", nargs="*", default=[])
    argp.add_argument("--con", nargs="*", default=[])
    argp.add_argument("--verdict", default="")
    argp.add_argument("--n", type=int, default=10)
    args = argp.parse_args()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    if args.action == "add":
        append({"ts": stamp, "kind": "step", "from": args.frm, "to": args.to,
                "why": args.why})
        print("recorded step %s -> %s" % (args.frm, args.to))
        return 0
    if args.action == "debate":
        append({"ts": stamp, "kind": "debate", "claim": args.claim,
                "pro": args.pro, "con": args.con, "verdict": args.verdict})
        print("debate recorded: %s (pro=%d con=%d)" % (args.claim[:60],
                                                       len(args.pro), len(args.con)))
        print("verdict is advisory only; final judgement stays with the skill")
        return 0
    if not os.path.exists(PATH):
        print("no logic chain yet at %s" % PATH)
        return 0
    lines = open(PATH, "r", encoding="utf-8").read().splitlines()
    for line in lines[-args.n:]:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
