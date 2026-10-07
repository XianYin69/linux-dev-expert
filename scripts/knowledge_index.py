#!/usr/bin/env python3
"""knowledge_index: query the nine-leaf knowledge tree (asset/knowledge_tree.json).

Use to pick the leaf before answering; unknown leaf -> topology question.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from _common import skill_root

TREE = os.path.join(skill_root(), "asset", "knowledge_tree.json")


def load():
    with open(TREE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def find(tree, terms):
    hits = []
    for leaf in tree["leaves"]:
        blob = " ".join([leaf["id"], leaf["title"], leaf["question"],
                         " ".join(leaf.get("sources", []))]).lower()
        score = sum(1 for term in terms if term.lower() in blob)
        if score:
            hits.append((score, leaf))
    hits.sort(key=lambda pair: -pair[0])
    return hits


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("terms", nargs="*", help="keywords to match")
    argp.add_argument("--list", action="store_true")
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    tree = load()
    if args.list or not args.terms:
        for leaf in tree["leaves"]:
            print("%s | %s | %s" % (leaf["id"], leaf["title"], leaf["question"]))
        print("leaves=%d frozen=%s" % (len(tree["leaves"]),
                                       tree.get("topology_frozen")))
        return 0
    hits = find(tree, args.terms)
    if not hits:
        print("no leaf matched; check topology rule in references/知识树.md")
        return 1
    for score, leaf in hits[:5]:
        print("%d  %s" % (score, leaf["id"]))
        print("   knowledge: %s" % leaf["knowledge"])
        print("   checklist: %s" % leaf["checklist"])
        print("   probes: %s" % ", ".join(leaf["probes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
