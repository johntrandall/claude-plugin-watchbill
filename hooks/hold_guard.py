#!/usr/bin/env python3
"""watchbill hold guard (PreToolUse: Edit, Write, MultiEdit, NotebookEdit, Bash).

DENIES a write under a folder whose vault or repository root holds the human's hold switch
(`.watchbill-hold` or `watchbill-hold.md`, see bin/watchbill_hold.py). Shell writes are found
the way the ownership hook finds them (redirections, tee, cp, mv, rm, trash, sed -i, ...).
Deleting the hold file is a write under the hold, so it is denied too: only the human
releases a hold. It applies in every project: the file is explicit, and a check costs a
few stat calls.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bin"))
sys.path.insert(0, HERE)
import watchbill_hold as hold  # noqa: E402
from ownership_warn import FILE_TOOLS, bash_write_targets  # noqa: E402


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    tool, tool_input = data.get("tool_name", ""), data.get("tool_input") or {}
    cwd = data.get("cwd") or os.getcwd()
    if tool in FILE_TOOLS:
        targets = [tool_input.get(FILE_TOOLS[tool], "")]
    elif tool == "Bash":
        targets = bash_write_targets(str(tool_input.get("command") or ""))
    else:
        return 0
    for raw in targets:
        if not raw:
            continue
        path = os.path.join(cwd, os.path.expanduser(raw))
        h = hold.hold_for(path)
        if h:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                     "permissionDecisionReason": hold.refusal(raw, h)}}))
            return 0
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
