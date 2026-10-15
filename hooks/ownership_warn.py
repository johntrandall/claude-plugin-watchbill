#!/usr/bin/env python3
"""watchbill ownership hook (council S1, WARN mode in 0.2).

PreToolUse hook for Edit, Write, MultiEdit, NotebookEdit and Bash. It finds the
target paths of a write, reads the system's owners file (`dev-docs/owners.yaml` at
the repository root) and prints a warning when a path belongs to another seat.

It NEVER blocks in 0.2: every path through this script exits 0 and never returns a
permission decision. A repository with no owners file gets no output at all.

Owners file format (YAML; a plain subset is parsed if PyYAML is missing):

    version: 1
    owners:                       # seat, agent type or agent name -> path globs
      architect: [README.md, dev-docs/**, .claude-plugin/**]
      watchbill-rules-agents: [agents/**, hooks/**, skills/**, evals/**]
    shared: [dev-docs/runs/**]    # anyone may write these

Who is writing: every identity the session has, so an owners key may name a seat
kind (`architect`) or an agent name (`events-rules-sync`) and the rightful owner is never
warned. The identities: WATCHBILL_SEAT (the seat kind `spawn --seat` sets) and
WATCHBILL_SEAT_NAME (its agent name); the hook input's `agent_type` (a plugin agent
such as `watchbill:architect` counts as `architect`); and the herdr agent name from
`herdr-lifecycle whoami`. An agent name also stands for its `-hoN` origin and for its
seat kind (from the handoff ledger's spawn row, else from the name's shape). A path no
owner lists is not checked, and the identity is looked up only when a target path has
an owner (so a read-only Bash call costs no whoami).

Read old, write new (0.4.0): a seat kind also stands for its 0.3 name and back, so an
owners key `builder` or `build-lead` still names the architect or a rules lead, and a
seat started before the rename (WATCHBILL_SEAT=builder) still owns an `architect` key.
"""
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys

OWNERS_RELATIVE_PATH = os.path.join("dev-docs", "owners.yaml")
FILE_TOOLS = {"Edit": "file_path", "Write": "file_path", "MultiEdit": "file_path",
              "NotebookEdit": "notebook_path"}


def repository_root(start):
    try:
        out = subprocess.run(["git", "-C", start, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def parse_owners_plain(text):
    """Parse the owners subset without PyYAML: top-level keys, one nested mapping
    level, block lists (`- x`) and flow lists (`[a, b]`)."""
    data, top, sub = {}, None, None

    def flow(value):
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            return [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
        return value.strip("'\"")

    for raw in text.splitlines():
        line = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        body = line.strip()
        if body.startswith("- "):
            item = body[2:].strip().strip("'\"")
            target = data[top][sub] if sub is not None else data[top]
            if not isinstance(target, list):
                target = []
                if sub is not None:
                    data[top][sub] = target
                else:
                    data[top] = target
            target.append(item)
            continue
        key, _, value = body.partition(":")
        key = key.strip().strip("'\"")
        if indent == 0:
            top, sub = key, None
            data[top] = flow(value) if value.strip() else {}
        else:
            if not isinstance(data.get(top), dict):
                data[top] = {}
            sub = key
            data[top][sub] = flow(value) if value.strip() else []
    return data


def load_owners_data(path):
    """The whole owners file as a dict (owners, shared, and an optional rules list)."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    try:
        import yaml  # noqa: PLC0415
        return yaml.safe_load(text) or {}
    except ImportError:
        return parse_owners_plain(text)


def load_owners(path):
    data = load_owners_data(path)
    owners = data.get("owners") or {}
    shared = data.get("shared") or []
    owners = {str(k): [str(g) for g in (v if isinstance(v, list) else [v])] for k, v in owners.items()}
    return owners, [str(g) for g in shared]


def glob_matches(pattern, relative_path):
    """fnmatch with `dir/**` meaning everything under dir, and `**/` any depth."""
    if pattern.endswith("/"):
        pattern += "**"
    if pattern.endswith("/**"):
        base = pattern[:-3]
        if relative_path == base or relative_path.startswith(base + "/"):
            return True
    regex = re.escape(pattern).replace(r"\*\*/", "(?:.*/)?").replace(r"\*\*", ".*")
    regex = regex.replace(r"\*", "[^/]*").replace(r"\?", "[^/]")
    return re.fullmatch(regex, relative_path) is not None or fnmatch.fnmatchcase(relative_path, pattern)


def herdr_agent_name():
    if os.environ.get("HERDR_ENV") != "1":
        return None
    try:
        out = subprocess.run(["herdr-lifecycle", "whoami"], capture_output=True, text=True, timeout=3)
        if out.returncode == 0:
            return json.loads(out.stdout).get("claude_name") or None
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return None


SEAT_SHAPES = ((r"-architect(-ho\d+)?$", "architect"), (r"-builder(-ho\d+)?$", "architect"),
               (r"-steward(-ho\d+)?$", "steward"), (r"-rules-", "rules"), (r"-build-", "rules"),
               (r"-run-", "run"), (r"-advisor(-|$)", "advisor"))
# The names one seat kind has had: any one of them in a session's identities brings the rest.
SEAT_SYNONYMS = ({"architect", "builder"}, {"rules", "rules-lead", "build", "build-lead"})


def with_synonyms(names):
    out = list(names)
    for name in names:
        for group in SEAT_SYNONYMS:
            if name in group:
                out += sorted(group)
    return list(dict.fromkeys(out))


def ledger_path():
    return os.environ.get("HERDR_LIFECYCLE_LEDGER") or os.path.expanduser(
        "~/.local/state/herdr-lifecycle/handoffs.jsonl")


def seat_kind_of(name):
    """The seat kind of an agent name: the newest spawn or relieve row naming it in the handoff
    ledger, else the name's shape (`<subject>-architect`, `<subject>-rules-<task>`, ...)."""
    seat = ""
    try:
        with open(ledger_path(), errors="replace") as handle:
            for line in handle:
                if f'"{name}"' not in line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("seat") and (
                        (row.get("event") == "spawn" and row.get("name") == name)
                        or (row.get("event") == "relieve" and row.get("receiver_name") == name)):
                    seat = row["seat"]
    except OSError:
        pass
    if seat:
        return seat
    return next((kind for pattern, kind in SEAT_SHAPES if re.search(pattern, name)), "")


def name_identities(name):
    """An agent name, its -hoN origin, and its seat kind."""
    out = [name]
    origin = re.sub(r"-ho\d+$", "", name)
    if origin != name:
        out.append(origin)
    kind = seat_kind_of(name)
    if kind:
        out.append(kind)
    return out


def identities(hook_input, agent_name=None):
    names = []
    seat = os.environ.get("WATCHBILL_SEAT")
    if seat:
        names.append(seat)
    seat_name = os.environ.get("WATCHBILL_SEAT_NAME")
    if seat_name:
        names += name_identities(seat_name)
    agent_type = hook_input.get("agent_type")
    if agent_type:
        names.append(agent_type)
        if ":" in agent_type:
            names.append(agent_type.split(":", 1)[1])
    agent_name = herdr_agent_name() if agent_name is None else agent_name
    if agent_name:
        names += name_identities(agent_name)
    return with_synonyms(list(dict.fromkeys(names)))


HEREDOC = re.compile(r"(<<-?[ \t]*(['\"]?)(\w+)\2)([^\n]*)\n.*?\n[ \t]*\3[ \t]*(?=\n|$)", re.DOTALL)
REDIRECT = re.compile(r"(?:^|[\s;&|(])\d?>>?\s*([^\s;&|)]+)")


def bash_write_targets(command):
    """Best-effort list of paths a shell command writes. Misses are acceptable in
    WARN mode; false alarms are not, so only clear write forms are recognised. A
    `cd DIR` earlier in the command moves where later relative paths point; after a
    `cd` this hook cannot resolve ($VAR unset here, `cd -`), relative paths are skipped."""
    command = HEREDOC.sub(lambda m: m.group(1) + m.group(4), command)  # a heredoc body is data, not commands
    targets, base = [], ""
    for segment in re.split(r"&&|\|\||;|\|", command):
        found = [m.group(1) for m in REDIRECT.finditer(segment)
                 if m.group(1) not in ("/dev/null", "&1", "&2") and not m.group(1).startswith("&")]
        try:
            words = shlex.split(segment)
        except ValueError:
            words = []
        if words and words[0] == "cd":
            dest = os.path.expandvars(words[1] if len(words) > 1 else "~")
            if base is None or "$" in dest or dest == "-":
                base = None if not os.path.isabs(os.path.expanduser(dest)) or "$" in dest or dest == "-" else dest
            else:
                base = os.path.join(base, os.path.expanduser(dest))
            continue
        if words:
            verb, args = os.path.basename(words[0]), [w for w in words[1:] if not w.startswith("-")]
            if verb == "tee" or verb in ("touch", "mkdir", "rm", "rmdir", "trash", "truncate"):
                found += args
            elif verb in ("cp", "mv", "ln", "install", "rsync") and len(args) >= 2:
                found.append(args[-1])
            elif verb == "sed" and any(w == "-i" or w.startswith("-i") for w in words[1:]):
                found += args[1:]
            elif verb == "git" and len(words) > 1 and words[1] in ("rm", "mv"):
                found += args[1:] if words[1] == "rm" else args[-1:]
        found = [t for t in found if t and "$" not in t and "*" not in t]
        if base is None:  # after a cd we cannot resolve, only absolute paths are known
            targets += [t for t in found if os.path.isabs(os.path.expanduser(t))]
        else:
            targets += [os.path.join(base, t) if base else t for t in found]
    return targets


def main():
    try:
        hook_input = json.load(sys.stdin)
    except ValueError:
        return 0
    cwd = hook_input.get("cwd") or os.getcwd()
    root = repository_root(cwd)
    if not root:
        return 0
    owners_path = os.path.join(root, OWNERS_RELATIVE_PATH)
    if not os.path.isfile(owners_path):
        return 0

    tool = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input") or {}
    if tool in FILE_TOOLS:
        raw_targets = [tool_input.get(FILE_TOOLS[tool], "")]
    elif tool == "Bash":
        raw_targets = bash_write_targets(tool_input.get("command", ""))
    else:
        return 0

    try:
        owners, shared = load_owners(owners_path)
    except Exception as error:  # a broken owners file must never break a tool call
        print(json.dumps({"systemMessage": f"watchbill ownership: cannot read {OWNERS_RELATIVE_PATH}: {error}"}))
        return 0

    real_root = os.path.realpath(root)
    me = None  # resolved on the first owned path only: `herdr-lifecycle whoami` costs about 60 ms
    warnings = []
    for raw in raw_targets:
        if not raw:
            continue
        absolute = os.path.realpath(os.path.join(cwd, os.path.expanduser(raw)))
        if not (absolute == real_root or absolute.startswith(real_root + os.sep)):
            continue  # outside this system: its own owners file governs it
        relative = os.path.relpath(absolute, real_root)
        if any(glob_matches(g, relative) for g in shared):
            continue
        holders = [name for name, globs in owners.items() if any(glob_matches(g, relative) for g in globs)]
        if not holders:
            continue
        if me is None:
            me = identities(hook_input)
        if any(name in holders for name in me):
            continue
        who = ", ".join(me) if me else "an unidentified session"
        warnings.append(f"{relative} is owned by {', '.join(holders)}, not by {who}")

    if warnings:
        text = ("watchbill ownership (WARN, not blocking): " + "; ".join(warnings)
                + ". If this write is outside your brief, stop and ask your launcher or the human.")
        print(json.dumps({
            "systemMessage": text,
            "hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": text},
        }))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # WARN mode: never fail the tool call
        sys.exit(0)
