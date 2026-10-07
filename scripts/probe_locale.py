#!/usr/bin/env python3
"""probe_locale: locale, timezone and encoding posture of this host.

Sorting, number formatting and case folding change with LC_* - measure first.
"""
from __future__ import annotations

import argparse
import datetime
import locale
import os
import time
try:
    import tzlocal
except ImportError:
    tzlocal = None

from _common import emit, first_line, not_linux, run


def zones():
    out = {}
    out["TZ_env"] = os.environ.get("TZ", "(unset)")
    out["etc_timezone"] = first_line(
        os.path.realpath("/etc/localtime").split("/")[-1]) if os.path.exists(
        "/etc/localtime") else "missing"
    code, text, _ = run(["timedatectl", "show", "-p", "Timezone"])
    out["timedatectl"] = text.split("=")[-1] if code == 0 else "unavailable"
    return out


def encodings():
    out = {}
    out["preferred_encoding"] = locale.getpreferredencoding(False)
    out["LANG"] = os.environ.get("LANG", "(unset)")
    code, text, _ = run(["locale", "-a"])
    lines = [x for x in text.splitlines() if x.strip()] if code == 0 else []
    out["locales_installed"] = len(lines)
    out["has_C_UTF8"] = str(any(x.startswith("C.UTF-8") for x in lines))
    return out


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--json", action="store_true")
    args = argp.parse_args()
    result = {}
    result.update(zones())
    result.update(encodings())
    result["utc_offset"] = time.strftime("%z")
    result["dst"] = bool(time.daylight)
    result["now_local"] = datetime.datetime.now().isoformat(timespec="seconds")
    result["now_utc"] = datetime.datetime.now(
        datetime.timezone.utc).isoformat(timespec="seconds")
    try:
        result["tz_name"] = tzlocal.get_localzone_name() if tzlocal else "tzlocal-absent"
    except Exception as exc:  # tzlocal optional on minimal images
        result["tz_name"] = "error:%s" % type(exc).__name__
    return emit(not_linux(result), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
