#!/usr/bin/env python3
"""probe_toolchain: compiler / builder / pkg-config versions and sanitizer support.

Reproducible-build claims must cite the versions reported here.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile

from _common import emit, first_line, not_linux, run

TOOLS = (
    "cc", "gcc", "g++", "clang", "clang++", "ld", "ar", "make", "cmake", "meson",
    "ninja", "pkg-config", "autoconf", "libtool", "strip", "readelf", "objdump",
    "qemu-aarch64", "aarch64-linux-gnu-gcc", "arm-linux-gnueabihf-gcc",
    "musl-gcc", "x86_64-linux-musl-gcc",
)


def versions():
    out = {}
    for name in TOOLS:
        if shutil.which(name) is None:
            continue
        code, text, _ = run([name, "--version"])
        if code != 0:
            code, text, _ = run([name, "-version"])
        out[name] = first_line(text) if code == 0 else "present-but-failed"
    return out


def glibc_version():
    code, text, _ = run(["ldd", "--version"])
    line = first_line(text)
    if code == 0 and line:
        return line.split()[-1]
    return "unknown"


def sanitizer_flags():
    """Compile a trivial TU with each sanitizer; report what the toolchain accepts."""
    src = "int main(void){return 0;}\n"
    results = {}
    with tempfile.TemporaryDirectory(prefix="lde-toolchain-") as work:
        path = os.path.join(work, "t.c")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(src)
        exe = os.path.join(work, "t")
        for san in ("address", "undefined", "thread", "memory", "leak"):
            cc = shutil.which("cc") or shutil.which("gcc")
            if cc is None:
                results[san] = "no-compiler"
                continue
            cmd = [cc, "-fsanitize=%s" % san, "-g", "-O0", path, "-o", exe]
            try:
                proc = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=60, errors="replace")
            except subprocess.TimeoutExpired:
                results[san] = "timeout"
                continue
            except OSError as exc:
                results[san] = "error:%s" % exc
                continue
            results[san] = "ok" if proc.returncode == 0 else "rejected"
    return results


def pkg_config_env():
    return {
        "PKG_CONFIG_PATH": os.environ.get("PKG_CONFIG_PATH", "(unset)"),
        "PKG_CONFIG_SYSROOT_DIR": os.environ.get("PKG_CONFIG_SYSROOT_DIR", "(unset)"),
    }


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--sanitizers", action="store_true",
                      help="probe sanitizer acceptance (compiles a trivial TU)")
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    result = versions()
    result["glibc"] = glibc_version()
    result.update(pkg_config_env())
    if args.sanitizers:
        for key, val in sanitizer_flags().items():
            result["san_%s" % key] = val
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
