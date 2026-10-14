"""The human's hold switch (a module; `watchbill hold <path>` reports it).

While a hold file exists at a vault's root, every watchbill writer refuses to write under it:
the hold_guard hook denies Edit, Write, MultiEdit, NotebookEdit and recognised shell writes,
and criticmarkup.py refuses every write. The human creates the file from any device and
deletes it to release the hold; agents never create or delete it.

Two names are accepted. `.watchbill-hold` is the canonical one. `watchbill-hold.md` is a
visible note, because Obsidian cannot create a dotfile and its own Sync does not carry
hidden files, so a hold set from a phone needs a visible name.

The search starts at the target and walks up to the first folder that holds `.obsidian` or
`.git` (the vault or repository root), or to the home folder.
"""
import os
import time

HOLD_NAMES = (".watchbill-hold", "watchbill-hold.md")


def hold_for(path):
    """The hold file governing `path`, or ''."""
    p = os.path.abspath(os.path.expanduser(path or "."))
    d = p if os.path.isdir(p) else os.path.dirname(p)
    home = os.path.expanduser("~")
    while True:
        for name in HOLD_NAMES:
            f = os.path.join(d, name)
            if os.path.isfile(f):
                return f
        parent = os.path.dirname(d)
        if (os.path.isdir(os.path.join(d, ".obsidian")) or os.path.exists(os.path.join(d, ".git"))
                or d == home or parent == d):
            return ""
        d = parent


def describe(hold):
    """One line about a hold file: where it is and since when."""
    try:
        since = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(hold)))
    except OSError:
        since = "unknown"
    return f"{hold} (set {since})"


def refusal(path, hold):
    return (f"watchbill: the human's hold switch is on: {describe(hold)}. No writer may change "
            f"{path} while it exists. Wait until the human deletes it; do not remove it yourself.")
