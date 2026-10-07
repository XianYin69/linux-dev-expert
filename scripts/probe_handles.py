#!/usr/bin/env python3
"""probe_handles: fd usage and leak signals for a pid (or this process).

fd growth over time is the primary leak signal - see asset/knowledge/fd-io.
"""
from __future__ import annotations

import argparse
import os

from _common import emit, first_line, not_linux, read_text, run


def limits(pid):
    soft, hard = "unknown", "unknown"
    for line in read_text("/proc/%s/limits" % pid, 8192).splitlines():
        if line.startswith("Max open files"):
            parts = line.split()
            soft, hard = parts[-3], parts[-2]
    return soft, hard


def fd_count(pid):
    path = "/proc/%s/fd" % pid
    try:
        return len(os.listdir(path))
    except OSError:
        return -1


def status(pid):
    text = read_text("/proc/%s/status" % pid, 16384)
    out = {}
    for key in ("State", "Threads", "VmRSS", "FDSize"):
        for line in text.splitlines():
            if line.startswith(key + ":"):
                out[key] = first_line(line.split(":", 1)[1])
                break
    return out


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--pid", default=str(os.getpid()))
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    pid = str(args.pid)
    soft, hard = limits(pid)
    result = {"pid": pid, "fd_open": fd_count(pid), "rlimit_soft": soft,
              "rlimit_hard": hard}
    result.update(status(pid))
    code, text, _ = run(["ls", "-l", "/proc/%s/fd" % pid], timeout=15)
    kinds = {}
    for line in text.splitlines():
        if "->" in line:
            target = line.split("->", 1)[1].strip()
            tag = target.split("[", 1)[0].split("/")[0] or "path"
            kinds[tag] = kinds.get(tag, 0) + 1
    for key in sorted(kinds):
        result["kind_" + key] = kinds[key]
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
