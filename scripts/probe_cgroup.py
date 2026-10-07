#!/usr/bin/env python3
"""probe_cgroup: cgroup v1/v2 layout, controllers and the limits on this process.

Container limits come from here, not from `nproc` - see toolchain-build-cross.
"""
from __future__ import annotations

import argparse
import os

from _common import emit, first_line, not_linux, read_text, run


def unified():
    text = read_text("/proc/mounts", 8192)
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[1] == "/sys/fs/cgroup":
            return parts[2]
    return "not-mounted"


def read_limit(path):
    if os.path.exists(path):
        return first_line(read_text(path, 128)) or "empty"
    return "absent"


def v2():
    base = "/sys/fs/cgroup"
    out = {}
    out["controllers"] = read_limit(base + "/cgroup.controllers")
    out["memory_max"] = read_limit(base + "/memory.max")
    out["memory_current"] = read_limit(base + "/memory.current")
    out["cpu_max"] = read_limit(base + "/cpu.max")
    out["pids_max"] = read_limit(base + "/pids.max")
    out["self_cgroup"] = read_limit("/proc/self/cgroup")
    return out


def v1():
    out = {}
    pairs = {
        "mem_limit": "/sys/fs/cgroup/memory/memory.limit_in_bytes",
        "cpu_shares": "/sys/fs/cgroup/cpu/cpu.shares",
        "nproc": "/sys/fs/cgroup/pids/pids.max",
    }
    for key, path in pairs.items():
        out[key] = read_limit(path)
    return out


def cpu_quota():
    out = {}
    code, text, _ = run(["nproc"])
    out["nproc_visible"] = first_line(text) if code == 0 else "unknown"
    try:
        out["sched_affinity"] = len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        out["sched_affinity"] = "unsupported"
    return out


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    version = unified()
    result = {"hierarchy": version}
    result.update(cpu_quota())
    if version == "cgroup2fs":
        result.update(v2())
    else:
        result.update(v1())
        result.update({"memory_max": read_limit(
            "/sys/fs/cgroup/memory/memory.limit_in_bytes")})
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
