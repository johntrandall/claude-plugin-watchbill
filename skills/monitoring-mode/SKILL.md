---
name: monitoring-mode
type: procedure
description: "How a session behaves once its work is delivered and only a watch keeps it alive: write the watch contract (probe, exit condition, deadline, alert or note, cadence), pick the mechanism, stay silent on no-op ticks, back off, escalate once, stop polling what only a person can clear, check your own context, and end the watch cleanly. Auto-invoke when arming a Monitor, loop, wakeup or cron after finishing the main work, on every tick or re-arm of such a watch, and when ending one. Writing the watcher script itself is watchbill:watchers; which shelf is watchbill:herdr-workspace-placement."
tags: [agents, monitoring, watch, herdr, watchbill]
---
> Where a global skill disagrees with the watchbill plugin on a decided point, the plugin's rules win (list: `watchbill:watchbill`, top).


# Monitoring mode

A session is in **monitoring mode** when its deliverable is handed over and the only thing keeping
it alive is a watch. Where it sits is `watchbill:herdr-workspace-placement`; how to write the
watcher is `watchbill:watchers`; this skill is what the session does while it watches. A parked
watchbill builder is a special case: it stays in its system's workspace with `👁`
(`watchbill:builder`).

An observer attached to a live run (a monitor on a running job) is working, not monitoring; it
moves only if a follow-up watch remains after the run. Housekeeping, a finished task, or waiting
on the human is not a watch.

## 1. Write the contract first
Before arming anything, write these five lines where the human and you both see them (the
project README or tracker, a card comment, your last message):
1. **What is watched**, and the exact probe (command, tool call, file).
2. **The exit condition**, as an observable ("RSS flat over about 40 refreshes", "30 clean days").
   A watch without one never closes.
3. **The deadline**: a date or tick count after which you stop, report and hand back.
4. **Alert or note:** what interrupts the human (the alert channels in the session context) and
   what only gets a log line. Decide now, not on the first anomaly.
5. **Cadence**, matched to how fast the watched thing changes.

Put the cadence and next check in the tab label (`… · recheck Thu 08:47`) and move to the shelf
in the same turn.

## 2. Pick the mechanism
| Need | Mechanism |
|---|---|
| A shell one-liner decides it | `Monitor` with a real description: one line per anomaly plus a backoff heartbeat, never one per poll. It expires after at most 30 minutes; keep baselines in a state file and re-arm. For many hours, a wakeup tick that runs the script once is cheaper. |
| Claude must judge (a tool query, a comparison) | `ScheduleWakeup` or `CronCreate` |
| A deadline more than 7 days out, or a daily check for weeks | The configured scheduler (session context). A session cron expires after 7 days. With no scheduler, keep the session watch, tell the human once, and keep the 7-day limit in view. Never restart a scheduler that is stopped: it may be stopped on purpose. |
| Waiting on a person other than the human, or a delivery | Not monitoring: a WAIT shelf |

**Exactly one watcher.** After every re-arm, list your monitors and stop the stale copy. Keep the
script and its state somewhere durable (the project and a state directory), never only in a
scratchpad or `/tmp`, which get swept.

## 3. Each tick
- **No change means silence:** `noop: true`, no message, no log line unless the contract asks.
- **Light, then full:** a tick runs the cheap probe; investigate fully only when it shows a change.
- **Back off when quiet** (double the interval per clean cycle up to a cap); reset on an anomaly.
- **Classify "new" before alarming:** a first appearance gets a note and a closer look.
- **Track, don't pin:** compare against what should be true now, not a value fixed at arm time; a
  deliberate upgrade must not become a false alarm.
- **Check your own context every tick** (`watchbill context`). At the cost band, offer a handoff;
  at 85 %, hand off by two-party relief (`watchbill:handoff-session`): the successor re-arms from
  your state file, and you keep the watch until it runs `relieve`. If a scheduler is configured,
  you may graduate the watch to it instead. A wakeup must never land on a full context.
- **Don't become a message sink:** before you run out, tell every session that messages you where
  to send instead, or close, so their sends fail loudly.
- **Re-arms are silent bookkeeping.** Respect a configured headroom check: wait or skip the tick.

## 4. Escalate once, then stop polling what cannot change
- Escalate once, with the unblock spelled out (device, command, click), in the message, the tab
  label (`herdr pane report-metadata`) and the card.
- **If the watched thing is blocked on a person, stop the watch** on the second identical tick:
  delete the cron or stop the monitor, write one summary, then close or move back to the project
  shelf with a note of what restarts the watch.
- An escalation that is someone else's job is routed, not watched: hand it over and confirm
  receipt (`notify_when_idle`, then check the reply). An anomaly bigger than your watch gets its
  own card; your watch does not quietly grow to own it.

## 5. End the watch
On the exit condition, the deadline, or the human's word:
1. Stop every mechanism you armed and verify none is left running.
2. Write the outcome against the contract (met, not met, abandoned and why) where the contract
   lives, and on the card.
3. Clear the badge and state label and **leave the MONITORING shelf in the same turn**. A finished
   watch left on the shelf advertises a watch nobody performs.
4. Take exactly one path and say which: results delivered and nothing to review → closeout and
   self-shutdown; something to review or decide → `herdr-lifecycle label review` (`✓`) and back to
   the project shelf.

Anti-patterns: no exit condition · a line per poll · re-reporting a blocker only a person can
clear · a stopped watch still on the shelf · a watcher out of context that still accepts messages
· a pinned expected value · two watchers after a re-arm · a multi-week check held in a live session
· a watching session that also orchestrates (it belongs on its project shelf).

Claim confidence: Observed, from transcripts of sessions that watched well, not controlled tests.
