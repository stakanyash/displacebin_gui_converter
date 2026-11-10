import os
import re
import sys
from datetime import datetime


_BUILD_RE = re.compile(r"^\[(\d{6})([a-z]{1,2})\]$")
_MAX_COUNTER = 702


def _resolve_log_level():
    if any(a in sys.argv for a in ("-debug", "--debug")):
        return "DEBUG"
    return "INFO"


def _letters_to_int(s):
    n = 0
    for ch in s:
        n = n * 26 + (ord(ch) - ord("a") + 1)
    return n


def _int_to_letters(n):
    if n <= 0:
        return ""
    n = min(n, _MAX_COUNTER)
    out = []
    while n > 0:
        n -= 1
        out.append(chr(ord("a") + (n % 26)))
        n //= 26
    return "".join(reversed(out))


def _next_build(current):
    today = datetime.now().strftime("%y%m%d")
    m = _BUILD_RE.match(current) if isinstance(current, str) else None
    if m and m.group(1) == today:
        counter = min(_letters_to_int(m.group(2)) + 1, _MAX_COUNTER)
    else:
        counter = 1
    return f"[{today}{_int_to_letters(counter)}]"


def _persist_build(new_build):
    path = os.path.abspath(__file__)
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
    except OSError as e:
        sys.stderr.write(f"[config] cannot read {path}: {e}\n")
        return

    new_src, n = re.subn(
        r"""^BUILD\s*=\s*['"][^'"]*['"]""",
        f'BUILD = "{new_build}"',
        src,
        count=1,
        flags=re.MULTILINE,
    )
    if n == 0:
        sys.stderr.write(f"[config] BUILD line not found in {path}\n")
        return

    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_src)
        os.replace(tmp, path)
    except OSError as e:
        sys.stderr.write(f"[config] cannot write {path}: {e}\n")
        try:
            os.remove(tmp)
        except OSError:
            pass


LOG_LEVEL = _resolve_log_level()

VERSION = "2.4"
BUILD = "[261110w]"
DGCVER = f"DisplaceGUI_{VERSION}".encode("ascii")

if LOG_LEVEL == "DEBUG" and not getattr(sys, "frozen", False):
    _new_build = _next_build(BUILD)
    _persist_build(_new_build)
    BUILD = _new_build