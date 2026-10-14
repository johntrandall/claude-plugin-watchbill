---
name: herdr-workspace-placement
type: convention
description: "Which herdr workspace (shelf) a session's tab belongs in once its work changes shape, and the order of tabs in a workspace: a session that only monitors moves itself to the monitoring shelf, one that only waits on something other than the human moves to a WAIT shelf, waiting on the human stays put, historians and parked builders stay put; the verified pane-move recipe and the tab-move call. Auto-invoke when you arm a watch after delivering, when you start waiting on a delivery, an upstream or a machine, when you take or hand over a lead role, or when sorting other sessions."
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
- **Only monitoring, not orchestrating → the monitoring shelf.** Only monitoring: the deliverable
  is handed over, a watch keeps the session alive, and nothing is pending from the human inside it.
  Not orchestrating: no live teammates, no running sub-agents, no sibling sessions waiting on your
  decisions. Tab agents or handoffs you launched do not count: they answer to the human.
- **Only waiting on something other than the human → its WAIT shelf.** A person other than the
  human, a carrier, an upstream maintainer, a long job, a machine coming back.
- **Waiting on the human is not a WAIT shelf.** The session stays on its project shelf, where the
  human looks for their own open items.
- **Monitoring or waiting is "who moves next".** If someone else moves next, it is WAIT even with a
  watcher armed; if you act when a condition fires, it is monitoring. Move; never fake it with a
  badge.
- **Stay put:** a `↪` historian (`watchbill:historian`); a parked watchbill builder (`👁`, in its
  system's workspace); a coordinator watching its own siblings; any seat of a watchbill system
  while it works.

Move when you arm the watch: you still have the context to write the label. When the watch ends
or real work resumes, move back the same way and clear the state label.

## 2. Recipe
Look the shelf up by label every time; workspace ids change on restore.
```bash
LABEL="MONITORING <SUBJECT>"
WS=$(herdr workspace list | python3 -c '
import sys,json; L=sys.argv[1]
ws=[w for w in json.load(sys.stdin)["result"]["workspaces"] if w["label"].lstrip("? ")==L]
print(ws[0]["workspace_id"] if ws else "")' "$LABEL")
[ -n "$WS" ] || WS=$(herdr workspace create --label "$LABEL" --cwd "$PWD" --no-focus \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"]["workspace"]["workspace_id"])')
PANE=$(herdr-lifecycle whoami | python3 -c 'import sys,json;print(json.load(sys.stdin)["pane_id"])')
herdr pane move "$PANE" --new-tab --workspace "$WS" --label "<SUBJECT> <what you watch>" --no-focus
```
- Resolve your own pane from your session id (`herdr-lifecycle whoami`), never from
  `$HERDR_PANE_ID`, which goes stale after a move or a restore. The move keeps the live process
  and its scrollback; the emptied source tab closes itself.
- Re-stamp any state label on the pane afterwards:
  `herdr pane report-metadata <pane> --source <watch> --state-label idle="⏳ watching · <what> (next <when>)" --ttl-ms 86400000`
  (24 hours is the maximum TTL; the shelf is the durable signal).
- Tab label: `<SUBJECT> <what is watched or awaited>`; the subject prefix lets the human scan a
  mixed shelf.

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
