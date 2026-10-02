import json, re, sys

# The fix: strip the byte order mark (EF BB BF, which Python decodes as U+FEFF) before parsing.
raw = sys.stdin.read().lstrip("﻿")
try:
    data = json.loads(raw)
except Exception:
    sys.exit(0)

msg = data["last_assistant_message"]
bad = re.findall(r"`((?![A-Za-z]:)[\w.-]+\\[^`]+)`", msg)
if bad:
    print(json.dumps({"decision": "block",
                      "reason": f"Use absolute paths, not: {bad[0]}"}))
