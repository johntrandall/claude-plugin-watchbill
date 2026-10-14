---
name: paper-trails
type: convention
description: "Who records what, where, and when in a watchbill system: the seat that holds the why writes it at action time, tools stamp clocks and counts, build events are Watchbill-Event commit trailers, every item carries the rules SHA it ran under, every decision of the human is recorded where its item lives and in the decisions file, approvals are single-use, a message is a doorbell not a record, one fact has one home, intent before and outcome after any unrepeatable action, append never rewrite, and how to answer a status question from records. Auto-invoke before writing a ledger line, process line, run manifest, decision record, registry entry, handoff brief or memory note in a multi-agent system, or when asked 'where is this recorded' or 'where are we on X' (start with watchbill status)."
tags: [agents, records, audit, watchbill]
---
# Paper trails

Full rule, the situations and the ownership table: `references/trails.md`. Build events are
commit trailers; there is no separate change ledger. Inside a watchbill system these rules win
over any other skill that disagrees.

## The eight principles
1. **The seat that holds the why writes it, when it holds it.** Builder: rules and their history.
   Steward: item outcomes. Lead: its report. Crew: a report to its spawner, nothing else. The
   human's words are quoted with the date, never paraphrased, and live in fields only the human's
   decisions fill.
2. **Tools stamp the clock, the ids and the counts; models write only the why.** A model-typed
   timestamp or count is a defect; enforce it with a failing check.
3. **Write when the action happens.** Closeout summarizes; it never originates.
4. **A message is a doorbell, not a record.** Whoever acts on it writes what it did, where the work
   lives. Test: if the recipient dies and restarts, does it need this? Yes means a record.
5. **One fact, one home.** Git: what changed, and each build event as a trailer. Item record:
   the item's state, its decisions and the rules SHA it ran under. System README: the current
   rule and the roster. Decisions file: one line per decision, pointing at its home. Everything
   else points.
6. **Intent before an unrepeatable action, outcome after.** Append; say what remains in the world.
7. **A standing rule is not recorded until something enforces it.** Memory is an inbox.
8. **Record dead ends and exposure windows** as carefully as successes.

## Where things go (the short list)
| What | Home | Writer |
|---|---|---|
| A rule changed | merge commit by `watchbill land` with the why, README in it, trailer `Watchbill-Event: landed` (`watchbill:builder` section 3) | builder |
| Backfilled, verified, verify-failed, cycle closed | commit trailer `Watchbill-Event: <event>` with `Watchbill-Rule` or `Watchbill-Cycle`; the commit-msg hook checks it | builder or its crew |
| An announcement | nothing: a message is FYI; the landed commit is the record | builder |
| Adopting a new rules SHA | run manifest `adopted <sha>`, after the check passed | steward |
| An item's state and outcome | the item record with `rules_sha` (`watchbill rules-sha`), one process line per change with its why | steward, through the tool |
| A guess at an unclear rule | process line starting `ASSUMED:` | whoever guessed |
| A run | run manifest: start, checkpoints, end with counters computed by the subject's tool, never typed; the end line carries `needs_human` (reason class to count), which `watchbill status` reads | steward |
| An escalation | escalation log with reason, later its outcome | spawner |
| A failed run, an abandoned approach | findings doc, written before the fix | builder |
| A lasting decision | README with the human's words and the rejected alternative; a decision record if it crosses systems | builder |
| A decision of the human | where its item lives (item record, Track Changes card, board card, commit), words verbatim with the date; plus one line in `dev-docs/decisions.md` | the seat that asked |
| An approval spent | `Watchbill-Approved: <where recorded>` on the landing that used it; single-use | builder (`watchbill land --approved`) |
| Work waiting on the human | an open entry in the decisions file, or a board card with unblock steps; tab `?` via `label human` | the seat that stopped |
| A handoff and relief | brief committed in the project; `herdr-lifecycle handoff --brief` (origin), `relieve` (receiver), `relief-check` past the deadline; handoff-ledger rows carry `launched_by` and `accountable` | origin, then receiver |
| A spawn | `herdr-lifecycle spawn --seat --brief` (handoff-ledger row with `launched_by`, `accountable`) | spawner |

Commit only your own paths: `git commit -m … -- <paths>`.

## A status question ("where are we on X")
Start with **`watchbill status <system-dir>`**: who has the ball, open decisions, last run,
rules SHA, recent landings with their approvals, cycle state, seats alive, from records only. For
more, read the item records and the run manifest (counts from the tool, never by eye), README
status, the decisions file, board lanes, and `git log` with its `Watchbill-Event` trailers. Cite
each source. Name what is waiting on the human. Do not ask a seat to summarize: a reply is a
message, not a record. Where `status` prints "unknown: <source>", that source is missing: say so
to the human, never "nobody has the ball".
