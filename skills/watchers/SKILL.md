---
name: watchers
type: procedure
description: "Writing or choosing a watcher (what counts as a change, exit codes, seen-state): a watcher detects change and the woken seat acts; exact change definition on structured fields; settle on quiet; seen-state outside the watched tree and /tmp; bounded life with re-arm; exit codes 0 change, 1 timeout, 2 hazard, 3 error; silent on no change; one watcher per target; tested against a known change; script kept in the repo; how to wait for a peer's reply or a relief. Behaviour of a session that is only watching after its work is delivered is `watchbill:monitoring-mode`. Auto-invoke when writing a watcher script, choosing its mechanism, or arming one that waits for a change."
tags: [agents, watching, monitor, watchbill]
---
> Where a global skill disagrees with the watchbill plugin on a decided point, the plugin's rules win (list: `watchbill:watchbill`, top).

# Watchers

Choosing the mechanism, the planned shared tool and the open gaps: `references/pattern.md`. The
shared `watchbill-watch` tool is planned, not built: until it exists, start from
`criticmarkup.py watch` (review marks) or write a one-shot script that follows the contract.

## The contract
1. **Detect only.** The woken seat decides and acts. A change needing no judgment is a reactor
   (a deterministic, idempotent service), not an agent's watch.
2. **State the change definition exactly**, including what it cannot see. Match structured fields
   (an author field, a frontmatter key), never words in text.
3. **Settle on quiet:** about 20 s for notes, about 120 s for board sorting.
4. **Seen-state with a stable key** in `~/.local/state/watchbill/watch/<name>.json`, never in the
   watched tree or `/tmp`. Re-arms then neither repeat nor miss.
5. **State the baseline:** whether existing items count; changes made while unwatched are reported
   at the next arm.
6. **Bounded life** (30 minutes under Monitor); say "re-arm" at the end.
7. **Exit codes:** 0 change (`NEW:` then one line per item), 1 timeout, 2 hazard (stop writing,
   tell the human; e.g. a sync conflict copy, a failed `watchbill check-note`, the human's hold
   file appearing), 3 error.
8. **Silent when nothing changed.** Every printed line costs the woken seat context.
9. **Cannot trigger itself:** disjoint watched and written sets, or its own author filtered.
10. **One watcher per target.** Its liveness belongs in a registry (planned); until then check
    `herdr-lifecycle siblings` before arming.
11. **Test it against a known change** before trusting its silence.
12. **The script lives in the repo**, never a scratchpad.

## Waiting on one thing
- **A peer's reply** to your SendMessage arrives as a message. End your turn and wait; do not
  poll. Waiting on a peer seat is not a WAIT shelf.
- **A condition a shell can test** (a build, a file, a historian's `closed`): a throwaway
  background until-loop. It is exempt from rules 4 and 12, keeps 6 and 8, and carries a deadline
  and an owner. Write what you wait on, and since when, in the run manifest.
- **A relief** (either side): `herdr-lifecycle relief-check` until it exits 0, 2 or 4
  (`skills/steward/references/handoff.md` step 8); the deadline is the configured
  `relief_deadline_minutes`.

## Who watches what, and how
| Seat | Watches | Mechanism |
|---|---|---|
| Steward | inbox, the human's decisions | long-lived Monitor in its own session, persisted seen-state |
| Editor | the human's review marks | one-shot background `criticmarkup.py watch`, re-armed after each finding |
| Parked builder (`👁`, alive) | outcomes and telemetry | the watch contract `dev-docs/watch.md`, a Monitor in its own session |
| Any seat | its own context | the context hook, once per band; `watchbill context` on demand |
| Nobody | deterministic reactions | a reactor service |

**Nothing outlives the session** unless the configured scheduler provides it. With `scheduler`
at `none`, no heartbeat, scheduled fallback or wake exists: a watch dies with its seat. Say so
wherever a seat would rely on one (README roster, `watch.md`, the brief). With a scheduler, the
design is a heartbeat whose gate skips while a live seat watches. Never type notices into a
seat's pane unless rare and opt-out.
