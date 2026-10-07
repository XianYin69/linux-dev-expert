#!/usr/bin/env python3
"""advice_compose: assemble leaf knowledge + checklist into one answer skeleton.

Output is a draft with evidence slots; unfilled slots must stay marked 未取证.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from _common import skill_root

TREE = os.path.join(skill_root(), "asset", "knowledge_tree.json")


def read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--leaf", required=True, help="knowledge tree leaf id")
    argp.add_argument("--host", default="(未探测)", help="detected target host")
    args = argp.parse_args()
    tree = json.loads(read(TREE))
    leaf = next((x for x in tree["leaves"] if x["id"] == args.leaf), None)
    if leaf is None:
        print("error: unknown leaf %s" % args.leaf)
        print("known: %s" % ", ".join(x["id"] for x in tree["leaves"]))
        return 2
    print("# 答复骨架 · %s" % leaf["id"])
    print("\n## 环境事实（须实测）\n- 目标主机：%s\n- 待填：os-release / PID1 / 包管理器 / 版本"
          % args.host)
    print("\n## 判据（来自 %s）\n%s" % (leaf["knowledge"],
                                       read(os.path.join(skill_root(),
                                                         leaf["knowledge"]))))
    print("\n## 交付检查（来自 %s）\n%s" % (leaf["checklist"],
                                          read(os.path.join(skill_root(),
                                                            leaf["checklist"]))))
    print("\n## 取证命令\n- 运行：%s" % "、".join(leaf["probes"]))
    print("\n## 出处\n- %s" % "、".join(leaf["sources"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
