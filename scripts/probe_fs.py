#!/usr/bin/env python3
"""probe_fs: case sensitivity, filesystem type, inotify limits, umask.

WSL/drvfs, NFS and vfat differ from ext4 - measure, do not assume.
"""
from __future__ import annotations

import argparse
import os
import shutil
import tempfile

from _common import emit, not_linux, read_text, run


def case_sensitive(path):
    work = tempfile.mkdtemp(prefix="lde-fs-", dir=path)
    try:
        upper = os.path.join(work, "CASE.TXT")
        with open(upper, "w", encoding="utf-8") as handle:
            handle.write("x")
        return str(os.path.exists(os.path.join(work, "case.txt")))
    except OSError:
        return "error"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def fs_type(path):
    code, text, _ = run(["stat", "-f", "-c", "%T", path], timeout=10)
    if code == 0 and text:
        return text.splitlines()[0]
    code, text, _ = run(["df", "-T", path], timeout=10)
    parts = text.split()
    if code == 0 and len(parts) >= 7:
        return parts[6]
    return "unknown"


def symlink_support(path):
    work = tempfile.mkdtemp(prefix="lde-ln-", dir=path)
    try:
        target = os.path.join(work, "t")
        with open(target, "w", encoding="utf-8") as handle:
            handle.write("x")
        link = os.path.join(work, "l")
        os.symlink(target, link)
        return "yes"
    except OSError:
        return "no"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--path", default=os.getcwd())
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    path = os.path.abspath(args.path)
    result = {"path": path, "fs_type": fs_type(path),
              "umask": "",
              "case_sensitive": case_sensitive(path),
              "symlink": symlink_support(path)}
    result["umask"] = "%03o" % (0o077 & ~os.umask(0o022))
    os.umask(0o022)
    for key, label in (("max_user_watches", "inotify_watches"),
                       ("max_user_instances", "inotify_instances"),
                       ("fs.file-max", "file_max")):
        code, text, _ = run(["sysctl", "-n", key], timeout=10)
        result[label] = text.splitlines()[0] if code == 0 and text else "unknown"
    result["fd_max_system"] = read_text(
        "/proc/sys/fs/file-max", 64).strip() or "unknown"
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
