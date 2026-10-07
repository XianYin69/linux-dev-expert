#!/usr/bin/env python3
"""probe_os: distro family, kernel, arch, virtualization and WSL detection.

Evidence for resistance/探测优先约束 (never assume the target distribution).
"""
from __future__ import annotations

import argparse
import os
import platform

from _common import emit, first_line, kv_parse, not_linux, read_text, run

FAMILY = (
    ("debian", "deb"), ("ubuntu", "deb"), ("linuxmint", "deb"),
    ("rhel", "rpm"), ("fedora", "rpm"), ("centos", "rpm"), ("rocky", "rpm"),
    ("alpine", "apk"), ("arch", "pacman"), ("suse", "zypper"), ("opensuse", "zypper"),
)


def os_release():
    data = kv_parse(read_text("/etc/os-release"))
    return {
        "id": data.get("ID", "unknown"),
        "id_like": data.get("ID_LIKE", data.get("ID", "unknown")),
        "version_id": data.get("VERSION_ID", "unknown"),
        "pretty_name": data.get("PRETTY_NAME", "unknown"),
    }


def family_of(id_like):
    low = id_like.lower()
    for token, name in FAMILY:
        if token in low:
            return name
    return "unknown"


def kernel_info():
    code, out, _ = run(["uname", "-rsm"])
    return {
        "kernel_release": platform.release() or "unknown",
        "machine": platform.machine() or "unknown",
        "uname_rsm": out if code == 0 else "unavailable",
        "bits": platform.architecture()[0],
    }


def env_kind():
    code, out, _ = run(["systemd-detect-virt"])
    virt = out if code == 0 else "unknown"
    proc_version = read_text("/proc/version", 2048).lower()
    wsl = "microsoft" in proc_version or "wsl" in platform.release().lower()
    container = os.path.exists("/.dockerenv") or "container=" in read_text(
        "/proc/1/cgroup", 4096)
    return {
        "virtualization": virt,
        "is_wsl": wsl,
        "is_container": container,
        "pid1": first_line(read_text("/proc/1/comm", 64)) or "unknown",
    }


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    rel = os_release()
    result = {}
    result.update(rel)
    result["family"] = family_of(rel["id_like"] + " " + rel["id"])
    result.update(kernel_info())
    result.update(env_kind())
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
