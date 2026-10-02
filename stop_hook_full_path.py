#!/usr/bin/env python3
"""Claude Code Stop hook: when the last reply names a file by a short path, block it and ask for the full path.

Works the same on Windows, macOS and Linux. Reads the Stop-hook JSON payload on stdin and prints
{"decision": "block", "reason": ...} when a reply has a short path, nothing otherwise.
Only paths inside backticks that end in a file extension are checked. A directory without an
extension, or a path outside backticks, is not flagged.
Run `python stop_hook_full_path.py --selftest` to check the cases below.
"""
import json
import re
import sys

TICKS = re.compile(r"`([^`\n]{2,200})`")
# absolute on Windows (C:\ or C:/), POSIX or UNC (leading / or \), home (~), or a URL
ABSOLUTE = re.compile(r"^(?:[A-Za-z]:[\\/]|[\\/]|~|[a-zA-Z][a-zA-Z0-9+.\-]*://)")
SEGMENT = re.compile(r"^[\w.\-{}, ]+$")  # braces and commas allowed: src/{a,b}.ts is one short path
EXTENSION = re.compile(r"\.[A-Za-z0-9]{1,6}$")


def short_paths(text):
    found = []
    for token in TICKS.findall(text):
        token = token.strip()
        if ABSOLUTE.match(token) or not re.search(r"[\\/]", token) or not EXTENSION.search(token):
            continue
        parts = [p for p in re.split(r"[\\/]", token) if p]
        if len(parts) >= 2 and all(SEGMENT.match(p) for p in parts):
            found.append(token)
    return found


def decision(payload):
    if payload.get("stop_hook_active"):
        return None  # already blocked once: let Claude stop rather than loop
    bad = short_paths(payload.get("last_assistant_message") or "")
    if not bad:
        return None
    shown = ", ".join(f"`{p}`" for p in bad[:2]) + (f" (+{len(bad) - 2} more)" if len(bad) > 2 else "")
    return {"decision": "block",
            "reason": f"Full paths only. Your reply has short paths: {shown}. Rewrite them as absolute paths."}


def load(raw):
    # Strip EVERY leading byte order mark: a UTF-8 pipe from Windows PowerShell can send two,
    # and the "utf-8-sig" codec removes only one.
    return json.loads(raw.decode("utf-8").lstrip("﻿"))


def selftest():
    cases = [
        ("`episode/clip-01.mp4`", True),
        ("`/home/dev/proj/episode/clip-01.mp4`", False),
        ("`/Users/dev/proj/episode/clip-01.mp4`", False),
        ("`C:\\proj\\episode\\clip-01.mp4`", False),
        ("`episode\\clip-01.mp4`", True),
        ("`src/{a,b}.ts`", True),
        ("`./src/app.ts`", True),
        ("`~/proj/app.ts`", False),
        ("`clip-01.mp4`", False),
        ("`anthropics/claude-code`", False),
        ("no backticks: episode/clip-01.mp4", False),
    ]
    for text, want in cases:
        got = bool(short_paths(text))
        assert got == want, (text, got, want)
    body = b'{"last_assistant_message": "`episode/a.md`"}'
    for prefix in (b"", b"\xef\xbb\xbf", b"\xef\xbb\xbf\xef\xbb\xbf"):  # none, one BOM, two BOMs
        assert decision(load(prefix + body)), prefix
    assert decision({"stop_hook_active": True, "last_assistant_message": "`a/b.ts`"}) is None
    six = " ".join(f"`episode/f{i}.md`" for i in range(6))
    assert "(+4 more)" in decision({"last_assistant_message": six})["reason"]
    print("all self-tests passed")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    try:
        out = decision(load(sys.stdin.buffer.read()))
    except json.JSONDecodeError:
        return
    if out:
        print(json.dumps(out))


if __name__ == "__main__":
    main()
