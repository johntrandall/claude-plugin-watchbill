# Watchers: choosing the mechanism, the planned shared tool, the open gaps

The rest of the pattern behind `watchbill:watchers`, which states the contract and who watches
what. Where this page and the skill disagree, the skill wins.

## 1. Choosing the mechanism

- **One finding, then act:** Bash `run_in_background` with a one-shot script. About zero idle cost.
- **A stream within a sitting:** Monitor, printing only findings and a backed-off heartbeat. Re-arm
  silently at the cap.
- **A periodic judgment:** ScheduleWakeup (up to an hour) or CronCreate (session-scoped, 7-day
  expiry).
- **Must outlive the session:** a scheduler **heartbeat** action (one that catches up after
  sleep; a routine that drops missed fires is weaker), with a gate that skips it while a live seat
  is watching. Only if the configured `scheduler` provides one; otherwise a seat that would rely
  on it says so in its README roster.
- **No agent needed:** a reactor service (a launch agent or systemd unit). Agent-waking watchers
  never survive a reboot.
- **Never** type notices into a seat's pane unless they are rare and carry their own opt-out.

## 2. The shared tool: `watchbill-watch` (planned)

One CLI in the plugin's `bin/`, with adapters:

```
watchbill-watch <adapter> <targets…> --name N [--settle S] [--interval I] [--timeout T]
                [--report-existing] [--json]
adapters: files (mtime), frontmatter (named fields), marks (review marks by author),
          pane-metric (context %), http-diff (remote list with a seen ledger), process (liveness)
```

The engine owns the loop, settle window, seen-state, cap, exit codes and the liveness registry.
Start from `cmd_watch` in the obsidian-track-changes-agent tool, the only existing watcher with all of baseline,
seen-set, settle and the hazard exit. Existing watchers migrate to it one at a time.

## 3. Gaps nobody has solved

1. **Dead-watcher detection.** Seats have died with a "live" watch on their tab, and a dead
   session still accepts messages. The liveness registry plus a check by the owner is the
   proposed answer.
2. **Telling the human's frontmatter edit from an agent's.** Fields carry no author, so a board
   watcher cannot tell a drag from a backfill. Only review marks are signed.
3. **"Is the human active right now"**, so a sweep pauses while they sort. No tested signal
   exists; the hold file is the explicit switch.
4. **Sources reachable only through an MCP** (boards, mail, calendar): no cheap shell poll.
5. **Waking one idle session from a daemon**, addressed and context-cheap.
6. **Other devices:** a sync service can defeat every settle window. The human's hold file and
   `watchbill check-note` after an outside change are the guard; whether the hold file itself
   syncs depends on the sync service (a dotfile may not; `watchbill-hold.md` is the visible
   alternative).
7. **Notification cost per session** is unmeasured.
