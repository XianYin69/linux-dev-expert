#!/usr/bin/env python3
"""probe_pkg: which package manager exists, and how to query/install on this host.

Never emit an install command for a family that was not detected here.
"""
from __future__ import annotations

import argparse
import shutil

from _common import emit, first_line, not_linux, run

MANAGERS = ("apt-get", "apt", "dnf", "yum", "rpm", "dpkg", "apk", "pacman", "zypper")

QUERY = {
    "apt-get": "apt-cache policy {pkg}",
    "apt": "apt list --installed {pkg}",
    "dnf": "dnf repoquery --installed {pkg}",
    "yum": "yum list installed {pkg}",
    "apk": "apk info -e {pkg}",
    "pacman": "pacman -Qi {pkg}",
    "zypper": "zypper info {pkg}",
}

INSTALL = {
    "apt-get": "DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends",
    "dnf": "dnf -y --setopt=install_weak_deps=False install",
    "yum": "yum -y --setopt=install_weak_deps=False install",
    "apk": "apk add --no-cache",
    "pacman": "pacman -Syu --noconfirm",
    "zypper": "zypper --non-interactive install",
}


def detected():
    found = {}
    for name in MANAGERS:
        if shutil.which(name):
            found[name] = "present"
    return found


def arch_info():
    out = {}
    code, text, _ = run(["dpkg", "--print-architecture"])
    if code == 0:
        out["deb_arch"] = first_line(text)
        code2, foreign, _ = run(["dpkg", "--print-foreign-architectures"])
        out["deb_foreign_arch"] = foreign.replace("\n", ",") if code2 == 0 else ""
    code3, rpm_arch, _ = run(["rpm", "--eval", "%{_arch}"])
    if code3 == 0:
        out["rpm_arch"] = first_line(rpm_arch)
    return out


def query(pkg, managers):
    for name in ("apt-get", "dnf", "yum", "apk", "pacman", "zypper"):
        if name in managers and name in QUERY:
            cmd = QUERY[name].format(pkg=pkg).split()
            code, text, err = run(cmd, timeout=25)
            return {"tool": name, "code": code, "output": first_line(text) or err}
    return {"tool": "none", "code": -1, "output": "no query tool detected"}


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--pkg", help="query one package name on this host")
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    managers = detected()
    result = {"managers": ",".join(sorted(managers)) or "none"}
    result.update(arch_info())
    for name, cmd in INSTALL.items():
        if name in managers:
            result["install_template"] = cmd
            break
    if args.pkg:
        got = query(args.pkg, managers)
        result["query_tool"] = got["tool"]
        result["query_code"] = got["code"]
        result["query_output"] = got["output"]
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
