#!/usr/bin/env python3
"""probe_elf: interpreter, SONAME, RUNPATH, needed libs and glibc symbol needs.

Answers "which library resolves this symbol / is the target glibc new enough".
"""
from __future__ import annotations

import argparse
import os
import re

from _common import emit, not_linux, run

GLIBC = re.compile(r"GLIBC_(\d+\.\d+)")


def sh(name, args, limit=4000):
    code, text, err = run([name] + args, timeout=25)
    return text[:limit] if code == 0 else (err or "unavailable")


def interp(path):
    out = sh("readelf", ["--program-headers", path])
    for line in out.splitlines():
        if "[Requesting program interpreter" in line:
            return line.split("[")[-1].rstrip("]").strip()
    return "static-or-unknown"


def dynamic(path, key):
    out = sh("readelf", ["--dynamic", path])
    for line in out.splitlines():
        if key in line:
            match = re.search(r"\[(.+?)\]", line.split(key, 1)[1])
            if match:
                return match.group(1)
    return "none"


def glibc_need(path):
    out = sh("objdump", ["-T", path])
    versions = set()
    for match in GLIBC.finditer(out):
        versions.add(match.group(1))
    if not versions:
        return "none-detected"
    ranked = sorted(versions, key=lambda v: [int(x) for x in v.split(".")])
    return ranked[-1]


def undefined(path):
    out = sh("ldd", ["-r", path])
    missing = [line.strip() for line in out.splitlines() if "undefined symbol" in line]
    return len(missing), "; ".join(missing[:3])


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("target", nargs="?", default=None)
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    if not args.target:
        return emit({"usage": "probe_elf.py <binary|lib.so>", "run_tests": "self"},
                    args.json)
    path = os.path.abspath(args.target)
    if not os.path.exists(path):
        return emit({"target": path, "error": "missing-file"}, args.json)
    count, detail = undefined(path)
    result = {
        "target": path,
        "file": sh("file", [path], 200).split(":", 1)[-1].strip(),
        "interpreter": interp(path),
        "soname": dynamic(path, "SONAME"),
        "rpath": dynamic(path, "RPATH"),
        "runpath": dynamic(path, "RUNPATH"),
        "needed": dynamic(path, "NEEDED"),
        "max_glibc_needed": glibc_need(path),
        "undefined_symbols": count,
        "undefined_detail": detail,
    }
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
