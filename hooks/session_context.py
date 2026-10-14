#!/usr/bin/env python3
"""watchbill session context (SessionStart: startup, resume, clear, compact).

Prints, as session context, the resolved configuration (watchbill config), the overlay file
and, for a seat, its primer: who it is, its brief, the paths it owns, its launcher of record.
After a compaction the primer comes back, so a seat never forgets which seat it is.

Who is a seat: WATCHBILL_SEAT / WATCHBILL_SEAT_NAME (set by `herdr-lifecycle spawn --seat`),
else the handoff ledger's spawn or relieve row for this session id or its Claude name.

Silent unless the session is a seat, a watchbill plugin agent, works inside a watchbill
system (a repository with dev-docs/owners.yaml), or runs an eval case that pins the
configuration (an EVAL_WATCHBILL_* variable): other projects get nothing.
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
sys.path.insert(0, BIN)
sys.path.insert(0, HERE)
import watchbill_config as config  # noqa: E402
import ownership_warn as ownership  # noqa: E402


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, path)
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader))
    loader.exec_module(mod)
    return mod


def git_top(d):
    try:
        out = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                             timeout=5)
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def seat_of_session(hl, sid, events):
    """(seat kind, agent name, ledger row) from the environment, else the ledger."""
    seat, name = os.environ.get("WATCHBILL_SEAT", ""), os.environ.get("WATCHBILL_SEAT_NAME", "")
    if not name and sid:
        name = (hl.registry().get(sid) or {}).get("name") or ""
    row = hl.seat_row(events, sid, name) if (sid or name) else None
    if row and not seat:
        seat = row.get("seat") or ""
        name = name or row.get("name") or row.get("receiver_name") or ""
    return seat, name, row


def brief_of(seat_name, row, system, wb):
    """The seat's brief: WATCHBILL_BRIEF, the ledger row's brief, else the roster's Brief column."""
    if os.environ.get("WATCHBILL_BRIEF"):
        return os.environ["WATCHBILL_BRIEF"]
    if row and row.get("brief"):
        return row["brief"]
    readme = os.path.join(system, "README.md") if system else ""
    if readme and os.path.isfile(readme):
        base = wb.HO.sub("", seat_name)
        for r in wb.roster(wb.read_text(readme)):
            if r["name"] in (seat_name, base) and r.get("brief"):
                b = os.path.expanduser(r["brief"])
                return b if os.path.isabs(b) else os.path.join(system, b)
    return ""


def owned_paths(system, ids):
    """[(owners key, globs)] whose key is one of this seat's identities."""
    path = os.path.join(system, "dev-docs", "owners.yaml") if system else ""
    if not path or not os.path.isfile(path):
        return None
    try:
        owners, shared = ownership.load_owners(path)
    except Exception:
        return None
    return [(k, g) for k, g in owners.items() if k in ids], shared


def primer(seat, name, row, system, source, hl, wb, events, sid):
    lines = [f"You are {name or 'an unnamed session'}, the {seat} seat"
             + (f" of the system in {system}." if system else ".")]
    brief = brief_of(name, row, system, wb)
    if brief:
        lines.append(f"Your brief: {brief}. " + ("Context was compacted: re-read it, and the system README, "
                                                 "before your next step." if source == "compact"
                                                 else "Read it before you act if you have not."))
    else:
        lines.append(f"No brief is recorded for you (spawn --brief, the ledger, the roster's Brief column): "
                     f"ask your launcher or {config.get('human_name')} for it.")
    ids = list(dict.fromkeys([seat] + (ownership.name_identities(name) if name else [])))
    own = owned_paths(system, ids)
    if own is None:
        lines.append("The system has no dev-docs/owners.yaml: write only what your brief assigns.")
    else:
        mine, shared = own
        if mine:
            lines.append("You own (dev-docs/owners.yaml): " + "; ".join(f"{k}: {', '.join(g)}" for k, g in mine)
                         + (f". Anyone may write: {', '.join(shared)}." if shared else "."))
        else:
            lines.append("No owners.yaml entry names you (" + ", ".join(ids) + "): every path another seat owns "
                         "is not yours to write.")
    if row:
        lines.append(f"Launched by {row.get('launched_by') or 'unrecorded'}; accountable now: "
                     f"{hl.accountable_now(events, sid, name) or row.get('accountable') or 'unrecorded'}.")
    return lines


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        data = {}
    sid = data.get("session_id") or os.environ.get("CLAUDE_SESSION_ID") or ""
    cwd = data.get("cwd") or os.getcwd()
    source = data.get("source") or ""
    agent_type = data.get("agent_type") or ""
    hl = load("herdr_lifecycle", os.path.join(BIN, "herdr-lifecycle"))
    events = hl.read_ledger(hl.ledger_path())
    seat, name, row = seat_of_session(hl, sid, events)
    system = os.environ.get("WATCHBILL_SYSTEM") or (row or {}).get("cwd") or ""
    system = git_top(system) if system and os.path.isdir(system) else ""
    if not system:
        top = git_top(cwd)
        system = top if top and os.path.isfile(os.path.join(top, "dev-docs", "owners.yaml")) else ""
    if not (seat or system or agent_type.startswith("watchbill:") or config.eval_pinned()):
        return 0
    lines = ["watchbill configuration (resolved at session start; `watchbill config --explain` shows the "
             "sources):"] + ["- " + l for l in config.summary_lines()]
    opath, otext = config.overlay_text()
    if opath:
        lines += ["", f"Overlay rules ({opath}):", otext.strip()]
    if seat:
        wb = load("watchbill_tool", os.path.join(BIN, "watchbill"))
        lines += ["", "Seat primer:"] + ["- " + l for l in primer(seat, name, row, system, source, hl, wb, events, sid)]
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": "\n".join(lines)}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:  # a context hook must never stop a session from starting
        print(json.dumps({"systemMessage": f"watchbill session context failed: {error}"}))
        sys.exit(0)
