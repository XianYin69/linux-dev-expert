#!/usr/bin/env python3
"""probe_systemd: is systemd PID 1, unit state, and unit-file verification.

If systemd is absent do not emit .unit files - see resistance/探测优先约束.
"""
from __future__ import annotations

import argparse
import os

from _common import emit, first_line, not_linux, read_text, run


def pid1():
    comm = first_line(read_text("/proc/1/comm", 64))
    return {"pid1": comm or "unknown", "systemd_pid1": str(comm == "systemd")}


def state():
    out = {}
    code, text, _ = run(["systemctl", "--version"])
    out["systemctl_version"] = first_line(text) if code == 0 else "unavailable"
    code, text, _ = run(["systemctl", "is-system-running"])
    out["system_running"] = text if code in (0, 1) else "unknown"
    code, text, _ = run(["systemctl", "list-units", "--state=failed",
                         "--no-legend", "--plain"])
    out["failed_units"] = str(len([x for x in text.splitlines() if x.strip()])) \
        if code == 0 else "unknown"
    code, text, _ = run(["systemctl", "list-timers", "--no-legend", "--plain"])
    out["timers"] = str(len([x for x in text.splitlines() if x.strip()])) \
        if code == 0 else "unknown"
    return out

def user_scope():
    out = {}
    code, _, _ = run(["systemctl", "--user", "is-system-running"])
    out["user_manager"] = "present" if code in (0, 1, 2) else "absent"
    user = os.environ.get("USER", "")
    if user:
        code, text, _ = run(["loginctl", "show-user", user, "-p", "Linger"])
        out["linger"] = text if code == 0 else "unknown"
    return out


def verify_unit(path):
    if not os.path.exists(path):
        return {"verify": "missing-file", "detail": path}
    code, text, err = run(["systemd-analyze", "verify", path], timeout=30)
    return {"verify": "ok" if code == 0 else "errors",
            "detail": (text or err)[:400] or "no-output"}


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--verify", help="unit file path to check")
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    result = {}
    result.update(pid1())
    result.update(state())
    result.update(user_scope())
    if args.verify:
        for key, val in verify_unit(args.verify).items():
            result[key] = val
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
