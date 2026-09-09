"""PostToolUse warning: a .py file was saved with a syntax error.

Warn, never block. On PostToolUse the tool has already run, and exit 2 only
surfaces stderr to Claude — which is exactly the intended behavior: the edit
stands, the error is visible immediately instead of at the next run.

Deliberately syntax-only. There is no linter, no test suite and no CI in this
repo, and Dell has no admin rights to install one. A hook that shells out to a
missing tool would fail on every edit, and hook errors are non-blocking noise —
which would train everyone to ignore hook output, the one thing that must not
happen to the commit guard next door.
"""

import json
import sys


def main():
    payload = json.load(sys.stdin)
    path = payload.get("tool_input", {}).get("file_path", "")
    if not path.endswith(".py"):
        return

    try:
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
    except OSError:
        return                       # deleted or moved; not our problem

    try:
        compile(source, path, "exec")
    except SyntaxError as err:
        sys.stderr.write(
            f"SYNTAX WARNING {path}:{err.lineno} — {err.msg}. "
            f"The file is saved; fix it before running the gates.\n")
        sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass                         # a warning hook must never be in the way
