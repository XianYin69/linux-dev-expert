#!/usr/bin/env python3
"""probe_caps: effective capabilities, LSM state and privilege posture.

Decide capability-based降权 before ever proposing sudo - see root权限约束.
"""
from __future__ import annotations

import argparse
import os

from _common import emit, first_line, not_linux, read_text, run


def ids():
    getuid = getattr(os, "getuid", None)
    geteuid = getattr(os, "geteuid", None)
    return (getuid() if getuid else "n/a", geteuid() if geteuid else "n/a")


def caps(pid):
    for line in read_text("/proc/%s/status" % pid, 16384).splitlines():
        if line.startswith("CapEff:"):
            raw = line.split(":", 1)[1].strip()
            return raw, bool(int(raw, 16)) if raw else False
    return "unknown", False


def decode(pid):
    code, text, _ = run(["capsh", "--decode=%s" % _capeff(pid)], timeout=15)
    if code != 0:
        return "capsh-unavailable"
    return first_line(text.split("=", 1)[-1]) if "=" in text else first_line(text)


def _capeff(pid):
    raw, _ = caps(pid)
    return raw if raw != "unknown" else "0"


def lsm():
    out = {}
    code, text, _ = run(["getenforce"])
    out["selinux"] = first_line(text) if code == 0 else "absent"
    code, text, _ = run(["aa-status"])
    out["apparmor"] = "present" if code in (0, 1) else "absent"
    code, text, _ = run(["seccomp-filter"])
    out["seccomp_tools"] = "unknown"
    return out


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--pid", default=str(os.getpid()))
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    raw, any_cap = caps(str(args.pid))
    result = {"pid": args.pid, "cap_eff": raw, "privileged": str(any_cap),
              "uid": ids()[0], "euid": ids()[1],
              "capabilities": decode(str(args.pid))}
    result.update(lsm())
    code, text, _ = run(["sysctl", "-n", "kernel.yama.ptrace_scope"])
    result["ptrace_scope"] = first_line(text) if code == 0 else "unknown"
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
