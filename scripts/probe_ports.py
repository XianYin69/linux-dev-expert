#!/usr/bin/env python3
"""probe_ports: listening sockets and the process that owns each one.

Use before writing systemd socket activation or firewall rules.
"""
from __future__ import annotations

import argparse
import re

from _common import emit, not_linux, run

LINE = re.compile(r"^(tcp|udp|tcp6|udp6)\s+\S+\s+\S+\s+(\S+)\s")


def parse_ss(text):
    rows = []
    for line in text.splitlines()[1:]:
        match = LINE.match(line)
        if not match:
            continue
        proto, local = match.group(1), match.group(2)
        users = re.search(r"users:\(\(\"([^\"]+)\"", line)
        pid = re.search(r"pid=(\d+)", line)
        rows.append({
            "proto": proto,
            "local": local,
            "port": local.rsplit(":", 1)[-1],
            "process": users.group(1) if users else "-",
            "pid": pid.group(1) if pid else "-",
        })
    return rows


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--port", help="filter one port")
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    code, text, err = run(["ss", "-tulnp"], timeout=20)
    result = {"ss": "ok" if code == 0 else "unavailable"}
    rows = parse_ss(text) if code == 0 else []
    if args.port:
        rows = [r for r in rows if r["port"] == str(args.port)]
    result["listeners"] = len(rows)
    for idx, row in enumerate(rows[:40]):
        result["l%02d" % idx] = "%(proto)s %(local)s %(process)s/%(pid)s" % row
    if code != 0:
        result["detail"] = err[:200] or "ss missing"
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
