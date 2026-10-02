# claude-code-stop-hook-full-path

A Claude Code **Stop hook** that makes Claude show the full file path. When Claude's last reply names a file by a short path such as `episode/clip-01.mp4`, the hook blocks the reply and Claude answers again with the absolute path, for example `/home/dev/proj/episode/clip-01.mp4`.

It is one Python file with no dependencies. It runs the same on Windows, Linux and macOS (macOS is untested by me).

This is the code from the video "Claude Code hooks: make Claude show the full file path (Stop hook, Windows and Linux)" on The Kilted Dev.

## What it flags

Only paths **inside backticks** that contain a `/` or `\` and end in a file extension, and that are not already absolute.

| Reply contains | Flagged? |
|---|---|
| `` `episode/clip-01.mp4` `` | yes |
| `` `episode\clip-01.mp4` `` | yes |
| `` `src/{a,b}.ts` `` (brace shorthand) | yes |
| `` `./src/app.ts` `` | yes |
| `` `/home/dev/proj/episode/clip-01.mp4` `` | no (absolute) |
| `` `C:\proj\episode\clip-01.mp4` `` | no (absolute) |
| `` `~/proj/app.ts` `` | no (home) |
| `` `clip-01.mp4` ``, `` `anthropics/claude-code` `` | no (no folder, or no extension) |
| episode/clip-01.mp4 outside backticks | no |

If the hook has already blocked once in the same turn (`stop_hook_active` is true) it lets Claude stop, so it can never loop.

## Install

1. Put `stop_hook_full_path.py` somewhere permanent and note its **absolute** path.
2. Add a Stop hook to `.claude/settings.json` in your project (copy `settings.example.json`). On Windows use `python "C:/Users/you/hooks/stop_hook_full_path.py"`; on Linux or macOS use `python3 /home/you/hooks/stop_hook_full_path.py`.
3. Check it: `python stop_hook_full_path.py --selftest` prints `all self-tests passed`.

It works best with a line in `CLAUDE.md` such as `Always give absolute paths, never relative ones.` The rule asks, the hook enforces.

## The three mistakes from the video

1. **A silent failure on Windows (byte order mark).** In Windows PowerShell 5.1, once the pipe encoding is UTF-8 (`$OutputEncoding = [System.Text.Encoding]::UTF8`), the first bytes Python reads from a piped file are `EF BB BF`, not `7B 22` (`{"`). `json.loads` fails on them, and a hook that catches that error and exits cleanly looks fine while it never blocks anything. Whether you see it depends on the setup. In my interactive recording the default pipe sent plain bytes and the UTF-8 setting added the mark. In a non-interactive `powershell.exe -NoProfile -File` run on the same machine, the default pipe already sent it once and the UTF-8 setting sent it **twice** (`EF BB BF EF BB BF`). Python's `utf-8-sig` codec strips only one, so this hook strips every leading `U+FEFF` itself. Run `peek.py` to see what your own pipe sends. Try it in `demo-bom/`:
   ```powershell
   $OutputEncoding = [System.Text.Encoding]::UTF8
   Get-Content payload.json | python peek.py            # the bytes Python receives
   Get-Content payload.json | python check_rules_v1.py  # prints nothing: silently broken
   Get-Content payload.json | python check_rules_v2.py  # prints the block decision
   ```
2. **The wrong output field.** I first printed `systemMessage`. Claude Code shows that to you, but it is not what sends Claude back to try again. A Stop hook must print `{"decision": "block", "reason": "..."}`; the `reason` is what Claude reads.
3. **The missed case (brace shorthand).** `src/{a,b}.ts` is one short path, but a path pattern that allows no braces or commas never matches it. The segment pattern here allows them, and the self-test has the case.

## Linux demo

`demo-linux/` is the container used for the Linux recording: Claude Code on `node:22-slim`, the hook mounted read-only at `/hook`, and a `/home/dev/proj/episode` folder of six empty files. The commands are at the top of `demo-linux/Dockerfile`. You need your own Claude Code login (kept in a named volume); the hook is the only thing under test.

## Limits

- It checks the **last assistant message** only, not tool output.
- A path without backticks is never flagged, so it only helps while Claude formats paths as code.
- macOS is untested.

## Licence

MIT. See `LICENSE`.
