---
name: herdr-workspace-placement
type: convention
description: "Which herdr workspace (shelf) a session's tab belongs in once its work changes shape, and the order of tabs in a workspace: a session that only monitors shelves itself on the monitoring shelf with the 📡 glyph (`herdr-lifecycle shelve monitoring`), one that only waits on something other than the human shelves itself on a WAIT shelf with ⏳, waiting on the human stays put, historians and parked architects stay put; a shelved session that picks up real work or spawns agents comes back to its own workspace first (`unshelve`; `spawn` does it) and tucks itself away again when it winds down. Auto-invoke when you arm a watch after delivering, when you start waiting on a delivery, an upstream or a machine, when real work reaches a shelved session, before spawning from a shelf, when you take or hand over a lead role, or when sorting other sessions."
tags: [agents, herdr, workspace, placement, watchbill]
---
> Where a global skill disagrees with the watchbill plugin on a decided point, the plugin's rules win (list: `watchbill:watchbill`, top).


# herdr workspace placement

A herdr workspace is a **shelf**. The human scans the sidebar to ask, per shelf, "what is this
group waiting on, and is any of it mine?" A session moves itself the moment its shape changes;
nobody sweeps for it.

**Shelf labels** come from the session context when the human's setup names them. Otherwise use
`MONITORING <SUBJECT>` and `WAIT for <what>` (`WAIT for people`, `WAIT for delivery`,
`WAIT for upstream`, `WAIT for infra`, `WAIT for boot`).

## 1. The rule
- **Only monitoring, not orchestrating → the monitoring shelf, glyph `📡`.** Only monitoring: the
  deliverable is handed over, a watch keeps the session alive, and nothing is pending from the
  human inside it. Not orchestrating: no live teammates, no running sub-agents, no sibling sessions
  waiting on your decisions. Tab agents or handoffs you launched do not count: they answer to the
  human. `📡` means "alive on a shelf, acts itself when its condition fires" (a daily scan, a
  health check); it is not `👁`, the parked architect watching its own system's outcomes from its
  own workspace, and not `⏳`, where someone else moves next.
- **Real work, or a spawn, ends the shelf stay** (the human, 2026-10-15). A shelved session that
  picks up real work, or spawns a sub-agent, a teammate or a sibling, first goes back to its own
  workspace (`herdr-lifecycle unshelve`; `spawn` and `spawn --seat` run it for you), works there,
  and when it winds down to a watch again tucks itself back on the shelf (`shelve` again). The
  shelves hold only sessions that are waiting or listening; the human never finds live work there.
- **Only waiting on something other than the human → its WAIT shelf.** A person other than the
  human, a carrier, an upstream maintainer, a long job, a machine coming back.
- **Waiting on the human is not a WAIT shelf.** The session stays on its project shelf, where the
  human looks for their own open items.
- **Monitoring or waiting is "who moves next".** If someone else moves next, it is WAIT even with a
  watcher armed; if you act when a condition fires, it is monitoring. Move; never fake it with a
  badge.
- **Stay put:** a `↪` historian (`watchbill:historian`); a parked watchbill architect (`👁`, in its
  system's workspace); a coordinator watching its own siblings; any seat of a watchbill system
  while it works.

Move when you arm the watch: you still have the context to write the label. When the watch ends
or real work resumes, come back the same way (`unshelve`) and clear the state badge.

## 2. Recipe
```bash
# only monitoring: the shelf MONITORING <SUBJECT> (created when missing), tab "📡 <topic>"
herdr-lifecycle shelve monitoring --topic "<SUBJECT> <what you watch> (next <when>)" --subject <subject> \
  [--badge "next <when>"]
# only waiting on someone other than the human: the shelf WAIT for <x>, tab "⏳ <topic>"
herdr-lifecycle shelve waiting --topic "<what you wait on>" --for people|delivery|upstream|infra|boot
# an existing shelf by its exact label (the human's setup may name one)
herdr-lifecycle shelve monitoring --topic "…" --shelf "MONITORING INFRA"
# real work again, or before you spawn (spawn does this itself)
herdr-lifecycle unshelve [--topic "<your tab text>"]
```
- `shelve` resolves your own pane from your session id (never `$HERDR_PANE_ID`, which goes stale
  after a move or a restore), finds the shelf by label (a leading `?` and case ignored) or creates
  it, moves the pane into a new tab there (the live process and its scrollback come along; the
  emptied source tab closes itself), writes the glyph-first label again after the move (a move can
  reset a label), and records your home workspace, its label and your cwd in the lifecycle ledger.
  It refuses while `claude` processes you launched still run (`--force` overrides), and refuses a
  second shelve before an `unshelve`.
- `unshelve` moves you back to the recorded home workspace, recreating it with the recorded label
  and cwd when it closed behind you, and relabels the tab active (the `_` lead mark and topic from
  your old label, or `--topic`).
- `--badge` stamps a pane state badge (24 hours is the maximum TTL) for the detail ("next 09:23");
  the shelf and the glyph are the durable signal. Re-stamp it on each re-arm.
- Tab label: `<SUBJECT> <what is watched or awaited>`; the subject prefix lets the human scan a
  mixed shelf. The glyph is set by the command, never typed into `--topic`.

## 3. Tab order inside a workspace
The lead (orchestrator) is the left-most tab, observers next, workers after. A lead tab may start
with `_` while it holds the role; when it hands off, it relabels glyph first without the `_`
(`herdr-lifecycle handoff`) and the successor takes the `_` and index 0. A watchbill system has
its own fixed order (`watchbill:watchbill`); `spawn --seat` places seats. `herdr tab` has no move
command; use the socket:
```bash
printf '%s\n' '{"id":"x","method":"tab.move","params":{"tab_id":"<ws>:<tab>","insert_index":0}}' \
  | nc -U "$HERDR_SOCKET_PATH"
```
A move can reset a label: rename after the last move and check with `herdr tab list`.

## 4. Sorting from the outside
herdr's `agent_status` reads idle for working, waiting and finished panes alike. Read the pane
(`herdr pane read <pane> --source recent-unwrapped --lines 60`; the recap line names what it waits
on), then the transcript tail: a live `Monitor` or a wakeup without `stop` means monitoring; the
last text says who moves next. A process with `--parent-session-id <its id>` children is
orchestrating. Ask a live session to move itself by `SendMessage`; move a pane yourself only when
its session is gone or the human asks for a sort.
