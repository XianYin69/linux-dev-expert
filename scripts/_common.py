#!/usr/bin/env python3
"""Shared helpers for linux-dev-expert probe and mechanism scripts."""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys

TIMEOUT = 10


def run(argv, timeout=TIMEOUT):
    """Run a command -> (code, stdout, stderr); missing binary -> (-1, '', reason)."""
    exe = shutil.which(argv[0])
    if exe is None:
        return -1, "", "missing:%s" % argv[0]
    try:
        proc = subprocess.run(
            [exe] + list(argv[1:]), capture_output=True, text=True,
            timeout=timeout, errors="replace",
        )
    except subprocess.TimeoutExpired:
        return 124, "", "timeout:%s" % " ".join(argv)
    except OSError as exc:
        return -2, "", "error:%s" % exc
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

def read_text(path, limit=65536):
    """Read a text file; unreadable -> '' (probes report absence, never crash)."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read(limit)
    except OSError:
        return ""


def kv_parse(text):
    out = {}
    for line in text.splitlines():
        if "=" in line:
            key, _, val = line.partition("=")
            out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def first_line(text):
    for line in (text or "").splitlines():
        if line.strip():
            return line.strip()
    return ""


def cache_dir():
    base = os.environ.get("LINUX_DEV_EXPERT_CACHE")
    if not base:
        root = os.environ.get("XDG_CACHE_HOME") or os.path.join(
            os.path.expanduser("~"), ".cache")
        base = os.path.join(root, "linux-dev-expert")
    os.makedirs(base, exist_ok=True)
    return base


def skill_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def not_linux(result):
    """Tag a probe result with host applicability (Linux-only facts degrade here)."""
    host = platform.system().lower()
    result["host_platform"] = host
    result["applicable"] = host == "linux"
    if not result["applicable"]:
        result["note"] = "run on the Linux host or WSL distro for real facts"
    return result


def emit(result, as_json=False):
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    for key in sorted(result):
        print("%s=%s" % (key, result[key]))
    return 0


def die(msg, code=2):
    print("error: %s" % msg, file=sys.stderr)
    raise SystemExit(code)
