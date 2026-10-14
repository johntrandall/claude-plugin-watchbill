---
name: role-relaunch
type: procedure
description: "Replacing a running role session (one with an agent definition) with a fresh one started from that definition: when (its definition or hooks changed, it was started without --agent or -n, or its context is full outside a watchbill relief), the handoff note and kickoff kept in the project, spawning with --agent and a unique name, marking the handoff, retitling and re-sorting tabs, the roster. Auto-invoke on 'relaunch a role', 'definition changed, the running tab is stale', or a role started without --agent or -n."
tags: [agents, handoff, herdr, agent-definition, watchbill]
---
> Where a global skill disagrees with the watchbill plugin on a decided point, the plugin's rules win (list: `watchbill:watchbill`, top).


# Role relaunch

A running session never re-reads its agent definition: frontmatter `hooks:` and `tools:` apply
only to a session started with `--agent <role>`. This skill replaces a role session with one
started from its definition. It adds to `watchbill:handoff-session` (briefing, announcement,
historian) and does not repeat it. **In a watchbill system**, a seat at 85 % context hands off by
two-party relief (`skills/steward/references/handoff.md`); use this skill only to replace a seat
for another reason, and spawn seats with `spawn --seat`.

## When
- **Its definition or hooks changed.** Relaying the new rule by message is a stopgap; relaunch at
  the role's next natural break.
- **It was started without `--agent` or without `-n`.** Its address is derived and can collide,
  and none of its definition's hooks are active.
- **Context at about 85 %** in a multi-role workspace that is not a watchbill system. The
  orchestrator is the backstop: it reads each tab's status line
  (`herdr pane read <pane> --lines 30 | grep -oE '[0-9.]+k/[0-9.]+m \([0-9]+%\)'`).

## Preconditions
1. The definition (`.claude/agents/<role>.md`, or the plugin agent) exists and its YAML parses. A
   role that lives only in a scratchpad briefing cannot be restarted: write the definition first.
2. The human has OK'd this relaunch.
3. **The receiver's name.** If the outgoing session has the role name, use
   `herdr-lifecycle next-name <name>` (`<name>-ho2`). If its address was derived, use the bare
   role name, not `<derived>-ho2`.

## Steps
1. **The outgoing session writes its handoff note** at
   `<project>/dev-docs/handoffs/YYYY-MM-DD-<role>-handoff.md` (the briefing template in
   `watchbill:handoff-session`), plus its session id and transcript path. Its last step re-checks
   the open list against what happened while it wrote (`git log --since=<start>`,
   `herdr tab list --workspace <ws>`), drops what closed, and marks the rest "verify before
   acting". It commits with a pathspec and checks `git show --stat HEAD`: the index is shared, so a
   commit can carry another session's files.
2. **The orchestrator writes the kickoff** at `<project>/dev-docs/handoffs/YYYY-MM-DD-<role>-kickoff.md`,
   about 30 lines: who it replaces (session id and address, now the historian), the read order
   (definition, shared skill, handoff note, the role's README), the first task, the orchestrator's
   address, the 85 % rule. Commit it. **Never in `/tmp` or a scratchpad**: those vanish with the
   spawning session.
3. **Spawn** in its own tab, with its model:
   ```bash
   herdr-lifecycle spawn <receiver> --new-tab --tab-label "<label>" --cwd <project> -- \
     --model <model> --agent <role> --permission-mode auto \
     --append-system-prompt-file <project>/dev-docs/handoffs/YYYY-MM-DD-<role>-kickoff.md \
     'Read the kickoff, your agent definition and the handoff note, then tell <orchestrator> you are up.'
   ```
   `spawn` adds `-n <receiver>` itself and refuses a live name. If a headroom check is configured
   and refuses, override only with the human's OK.
4. **Verify:** `herdr-lifecycle siblings` lists it with no collision; `ps -axo pid,args | grep -- '-n <receiver>'`
   shows `--agent <role>`; it messages the orchestrator. If silent, read its pane: it may be on a
   dialog.
5. **Mark the handoff** from the outgoing session: `herdr-lifecycle handoff <receiver> --dry-run`,
   then without `--dry-run`. Send the announcement and the historian offer
   (`watchbill:handoff-session` section 6). Run it only from the outgoing top-level session: a
   sub-agent inherits its parent's session id and would relabel the parent's tab. If the outgoing
   session cannot act, the orchestrator runs
   `herdr-lifecycle label handed-off --tab <outgoing pane> --to <receiver>` and gives the receiver
   the transcript path.
6. **Retitle and re-sort:** the project's label format, the historian with its glyph first; the
   orchestrator at index 0, roles in order, historians last
   (`watchbill:herdr-workspace-placement` section 3). Rename after the last move.
7. **Update the roster** (the README's roles table or the run log): role, tab, address, agent
   definition, date; the old session marked historian, with its session id so it can be resumed.
8. **The historian ends itself once `herdr-lifecycle historian-check` allows it** (`watchbill:historian`), or when the human says so. If its exit dialog
   names a background shell, inspect it first (`pgrep -lfP <claude pid>`): it may be a watcher
   another role relies on. If unsure, ask the human.

## Lessons
| Lesson | Why |
|---|---|
| Kickoffs and handoff notes live in `<project>/dev-docs/handoffs/` | `/tmp` files vanished, so roles could not restart |
| Name every session at birth | derived names collided |
| Re-check the open list against `git log` before committing the note | items closed while the note was written |
| A definition change reaches a running tab only by relaunch | hooks and tools bind at start |
| Relabel after every tab move | moves reset labels |
| `git show --stat HEAD` after a pathspec commit | a shared index raced |
| Inspect a background shell before choosing "stop" at exit | another role relied on it |
