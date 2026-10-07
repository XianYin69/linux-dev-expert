#!/usr/bin/env python3
"""probe_tracing: availability of strace/ltrace/perf/eBPF/valgrind and BTF.

Pick the取证 tool from this report, never from memory of what "usually" exists.
"""
from __future__ import annotations

import argparse
import glob

from _common import emit, first_line, not_linux, read_text, run

TOOLS = ("strace", "ltrace", "perf", "bpftrace", "bt", "valgrind", "gdb",
         "systemtap", "stap", "trace-cmd", "lttng", "eu-stack", "pmap")


def tools_present():
    out = {}
    for name in TOOLS:
        code, text, _ = run([name, "--version"], timeout=15)
        if code == -1:
            code, text, _ = run([name, "-V"], timeout=15)
        out[name] = first_line(text) if code not in (-1, -2) else "missing"
    return out


def bpf_support():
    result = {}
    result["btf"] = "present" if glob.glob("/sys/kernel/btf/vmlinux") else "absent"
    config = read_text("/proc/config.gz", 4096) or ""
    if not config:
        paths = sorted(glob.glob("/boot/config-*"), reverse=True)
        config = read_text(paths[0], 200000) if paths else ""
    for key in ("CONFIG_BPF_SYSCALL", "CONFIG_KPROBES", "CONFIG_PERF_EVENTS",
                "CONFIG_FTRACE_SYSCALLS"):
        result[key.lower()] = "y" if ("%s=y" % key) in config else \
            ("m" if ("%s=m" % key) in config else "unset-or-unknown")
    code, text, _ = run(["sysctl", "-n", "kernel.perf_event_paranoid"])
    result["perf_event_paranoid"] = first_line(text) if code == 0 else "unknown"
    code, text, _ = run(["sysctl", "-n", "kernel.kptr_restrict"])
    result["kptr_restrict"] = first_line(text) if code == 0 else "unknown"
    code, text, _ = run(["sysctl", "-n", "kernel.unprivileged_bpf_disabled"])
    result["unprivileged_bpf"] = first_line(text) if code == 0 else "unknown"
    return result


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    result = tools_present()
    result.update(bpf_support())
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
