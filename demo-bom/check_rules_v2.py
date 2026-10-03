import json, re, sys

# Read bytes, decode as UTF-8, then strip every leading byte order mark (EF BB BF, U+FEFF).
# sys.stdin.read() would decode a Windows pipe with the system code page, where the mark is three other characters.
raw = sys.stdin.buffer.read().decode("utf-8").lstrip("\ufeff")
try:
    data = json.loads(raw)
except Exception:
    sys.exit(0)

msg = data["last_assistant_message"]
bad = re.findall(r"`((?![A-Za-z]:)[\w.-]+\\[^`]+)`", msg)
if bad:
    print(json.dumps({"decision": "block",
                      "reason": f"Use absolute paths, not: {bad[0]}"}))
