#!/usr/bin/env python3
"""watchbill context band (UserPromptSubmit): when to offer a handoff, and when to hand off.

Reads the session's context size from its transcript (`watchbill context` does the same).
At handoff_offer_tokens (default 400,000) it adds one line telling the seat to offer the
human a handoff, once per crossing; at handoff_hard_percent of context_window_tokens
(default 85 % of 1,000,000) it says "hand off now" on every prompt.

Silent unless the session is a seat (WATCHBILL_SEAT), a watchbill plugin agent, or works
inside a watchbill system (a repository with dev-docs/owners.yaml).
"""
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
BIN = os.path.join(os.path.dirname(HERE), "bin")


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, path)
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader))
    loader.exec_module(mod)
    return mod


def in_scope(cwd, agent_type):
    if (os.environ.get("WATCHBILL_SEAT") or agent_type.startswith("watchbill:")
            or any(k.startswith("EVAL_WATCHBILL_") for k in os.environ)):
        return True
    try:
        out = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                             timeout=5)
    except (OSError, subprocess.SubprocessError):
        return False
    return out.returncode == 0 and os.path.isfile(os.path.join(out.stdout.strip(), "dev-docs", "owners.yaml"))


def state_path(sid):
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.expanduser("~/.local/state/watchbill")
    return os.path.join(base, "context-band", f"{sid}.json")


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    sid, transcript = data.get("session_id") or "", data.get("transcript_path") or ""
    if not sid or not transcript or not in_scope(data.get("cwd") or os.getcwd(), data.get("agent_type") or ""):
        return 0
    name = os.environ.get("WATCHBILL_SEAT_NAME", "")
    if os.environ.get("WATCHBILL_SEAT") and name:
        # A seat whose spawn was blocked at the folder-trust dialog clears its own mark at its first
        # prompt: only a submitted prompt proves the dialog was answered (a session-start hook can
        # run while the dialog is still up, seen 2026-10-16), and only then is the seat working.
        try:
            load("herdr_lifecycle", os.path.join(BIN, "herdr-lifecycle")).clear_blocked_start(sid, name)
        except BaseException:  # labelling must never stop a prompt
            pass
    wb = load("watchbill_tool", os.path.join(BIN, "watchbill"))
    tokens, _ = wb.context_tokens(transcript)
    code, verdict, pct = wb.context_verdict(tokens)
    path = state_path(sid)
    try:
        with open(path) as f:
            last = int(json.load(f).get("code", 0))
    except (OSError, ValueError):
        last = 0
    if code != last:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump({"code": code, "tokens": tokens}, f)
    if code == 2 or code > last:
        human = wb.human()
        text = ({1: f"watchbill context band: {tokens:,} tokens of context. Offer {human} a handoff now (one "
                    f"short message: where you are, what is left, that you can brief a successor); it is a cost "
                    f"offer, not the hard line.",
                 2: f"watchbill context: {pct:.0f} % of the window ({tokens:,} tokens). Hand off now: brief a "
                    f"successor and run `herdr-lifecycle handoff`."})[code]
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
