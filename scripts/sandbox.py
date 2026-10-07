#!/usr/bin/env python3
"""sandbox: fixed-path workspace when no target directory was given.

Rule: work in the sandbox, deliver on request, then delete the sandbox.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import time

BASE = os.path.join(os.environ.get("SMS_TMP") or os.path.expanduser("~"),
                    "sandbox-linux-dev-expert")


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("action", choices=("create", "path", "deliver", "destroy"),
                      default="path", nargs="?")
    argp.add_argument("--dest", help="real target directory for delivery")
    args = argp.parse_args()
    if args.action == "path":
        print(BASE)
        return 0
    if args.action == "create":
        os.makedirs(BASE, exist_ok=True)
        print("sandbox ready: %s" % BASE)
        return 0
    if args.action == "deliver":
        if not args.dest:
            print("error: --dest required")
            return 2
        target = os.path.abspath(args.dest)
        if os.path.exists(target) and os.listdir(target):
            print("error: dest not empty: %s" % target)
            return 1
        shutil.copytree(BASE, target, dirs_exist_ok=True)
        print("delivered %s -> %s" % (BASE, target))
        return 0
    if args.action == "destroy":
        if not os.path.isdir(BASE):
            print("nothing to destroy")
            return 0
        stamp = time.strftime("%Y%m%d%H%M%S")
        os.rename(BASE, BASE + ".removed-" + stamp)
        shutil.rmtree(BASE + ".removed-" + stamp, ignore_errors=True)
        print("sandbox destroyed")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
