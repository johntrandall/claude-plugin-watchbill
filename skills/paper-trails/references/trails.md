# Paper trails: the ownership table and the situations

The full rule behind `watchbill:paper-trails`, which states the eight principles and the short
list. Build events are `Watchbill-Event` commit trailers: there is no change ledger, no
announce-and-ack and no pause. Where this page and the skill disagree, the skill wins.

## 1. Who owns which trail

| Trail (where) | Architect | Steward | Lead | Crew | Historian | Human |
|---|---|---|---|---|---|---|
| Commits with session trailer (git) | rules, README, briefs | item records it changed | its files | its files, `REPORT:` in body | — | — |
| System README: current rules, roster | **owns** | reads | reads | — | — | approves |
| Decisions file `dev-docs/decisions.md`: one line per decision, open questions | lines for the decisions it asked | lines for the decisions it asked | — | — | — | answers, accepts |
| Build events: `Watchbill-Event` commit trailers (git) | **owns** (landed, verified, verify-failed, cycle-closed; `Watchbill-Approved` on a landing) | — | lands with them when its brief says so | backfill: `backfilled` | — | — |
| Cycle folder `dev-docs/runs/<cycle>/{briefs,reports}` | briefs, gate table | — | its report | report saved by spawner | — | — |
| Findings doc (what failed, ranked; rejected approaches) | **owns** | — | contributes | — | — | reads |
| Item record: status, note, decisions, one process line per change with its why | defines the schema and the check | **owns** | its items | lines its tool writes | — | its own decision fields |
| Run manifest: start, checkpoint, end with computed counters | reads, trends | **owns** (through the tool) | its runs | — | — | — |
| Escalation log | reads | supplies reason, records outcome | same | — | — | — |
| Shared board card: status + comments | its card | its cards | its card | — | — | sets Accepted |
| Watch contract `dev-docs/watch.md` | **owns** when parked | — | — | — | — | reads |
| Handoff ledger | via `herdr-lifecycle` | same | same | — | marks its exit | — |
| Memory notes (any cross-session memory) | pointers to decisions, Verified fixes | pointers only | pointers only | — | only new, substantive answers | — |

## 2. Where things go, by situation

**Building** (the architect's trails)

| Situation | Record |
|---|---|
| Cycle starts | Brief in the cycle folder with the human's request verbatim and the gate: which checks, what "done" means, which outcome numbers the system must emit. The human's yes to the gate recorded where it was given and in the decisions file. |
| A rule change lands | `watchbill land` merges the build branch with the why; README edited in the same merge; trailers `Watchbill-Event: landed`, `Watchbill-Backfill: owed\|none`, `Watchbill-Steward: affected\|unaffected\|none`, and `Watchbill-Approved: <where recorded>` when the change needed the human's approval (the commit-msg hook rejects a `build/*` merge without `landed`). |
| Architect tells the steward | One FYI message listing the files and the landed SHA. No ack, no wait, no pause: the landing happened between the steward's items, and the steward adopts the SHA after its check passes, writing `adopted <sha>` in its run manifest. If the steward is not live, the landed commit is the message. |
| Backfill | Crew writes a process line per record and one commit with `Watchbill-Event: backfilled` and `Watchbill-Rule: <landed sha>`, after its own script count. Records the backfill could not fix go in its report. |
| Verifier finds a problem | Report saved verbatim; a commit with `Watchbill-Event: verify-failed` and `Watchbill-Rule: <sha>`: the **exposure window** runs from that rule to the landed fix whose `Watchbill-Fixes` names it, so the steward knows which items were written under the faulty rule. |
| Lasting design decision | README states it with the human's words and the rejected alternative; a decision record only if it crosses systems; a memory note a pointer. |
| The human states a rule or rejects an approach | The seat the human is talking to records their words that turn, where the decision lives and in the decisions file. The architect promotes the rule into the enforcing text, ideally a check, in the same cycle. A steward forwards the quote to the architect; it never writes rules. |
| A run fails | Findings doc written **before** the fix, causes tagged Verified, Observed or Inferred. |
| An approach is abandoned | Findings doc "rejected": what, why, what remains; the revert commit says why; a memory note of one line so nobody retries it. |
| Gate closes | Gate table with script evidence; commit with `Watchbill-Event: cycle-closed`; README and steward brief updated; the result to the human for review; one message to the steward (SHA, what changed in its brief) and one to the human (paths to the gate table and `watch.md`); the leads the architect spawned are closed; watch contract written before parking. A system with no inbox has no steward: the architect closes out instead of parking. |
| Parked architect sees drift | Dated note in `watch.md` with item ids, only on change; opens a new cycle (not while the human is away). |

**Running** (the steward's trails)

| Situation | Record |
|---|---|
| Picks up an item | Process line naming the authority ("the human moved it to Book"). |
| Completes an item | Status, outcome as observed (not "the tool returned 200"), pointer to the confirmation. Same write as the result. |
| Needs the human | Status, the reason as a countable class (pay, sign-in, consent, invite code), the link, what the human does, what the steward does after. On a board: the needs-human lane with unblock steps. The run manifest's end line carries `needs_human` (class to count, computed by the tool), which `watchbill status` reads. |
| The human decides | Their words verbatim and the date on the item (or its card), on a channel the brief names; one line in the decisions file pointing there. |
| A REQUEST arrives citing an approval | Open the cited place; act only if the words cover this exact change and are not already spent; record on the item which approval it acted under. Otherwise refuse and record why. |
| Escalates | Escalation log line with the reason; the outcome (resolved, failed, the human) added when the report comes back. |
| Prepared hand-off | Note on the item: the tab title, the one action, how to rebuild the tab. The tab itself is not a trail. |
| Fault outside the subject | The brief in the other subject's project folder; affected items marked blocked with the brief's path; on "fixed", verify by observation and write "unblocked: verified by …". |
| Scheduled run with no tab | Run manifest lines only, plus one end-line note listing exceptions. |
| Shared-board item | The card wins for status; the local record links the card. |
| Outbound action as the human | Intent and authority before, outcome and artifact pointer after. |
| The human changes their mind | Append a withdrawal with a cause (the human changed their mind, or the steward misread); say what is still held in the world. |
| Architect lands a rule change (FYI) | Nothing is paused. Before its next item the steward runs its check at the new SHA and writes `adopted <sha>` in its run manifest, or takes no items under it and sends a rule problem. |
| Run lead or steward doubts a rule | It stops applying the rule to new items; message with the rule (file and line), item ids, produced versus expected, a confidence tag; items continued under its own reading carry an `ASSUMED:` process line. |
| A note changed from outside | `watchbill check-note <file>` before writing on top of it; a failure is a hazard: stop and tell the human. |
| Numbers worth trending | The run's end line, computed by the tool from the records: picked, done, needs-human by class, withdrawn by cause, escalated by outcome, errors by class, oldest pending age, pings sent to the human. Each loop step is listed as `ok` or `SKIP(<reason>)`, with the ran/total count computed by the tool. |

**Continuity** (any seat)

| Situation | Record |
|---|---|
| Handoff | Commits first; brief with tasks, cards, anchors, historians; `herdr-lifecycle handoff --brief` (the handoff ledger; the origin owns the seat until the receiver runs `relieve` and sends it the `tell_origin` line; `relief-check` past the deadline). |
| Fork to a new endeavor | Founding brief with a scope guard and the why; a one-line pointer in the origin's project that the work moved. |
| Historian is asked | Nothing by default. If a question comes twice, the head writes the answer into the README. |
| Head closes out | `herdr-lifecycle closed`, one line to each historian; historians record their exit. |
| Crew finishes | Its report; the lead files the verdict. A report is not a trail until filed. |
| Crash, reboot, compaction | Only what was already written survives. On recovery, a dated correction under the dead entry; uncommitted hunks listed, never committed blind. After compaction, the context hook re-primes the seat; re-read the brief, the plan and `git status` before trusting the summary. |
| Put down waiting on the human | An open entry in the decisions file, or a board card with unblock steps. |
| The human asks "where are we on X" | The head seat runs `watchbill status <system-dir>` first, then answers from: item records and run manifest (counts from the tool, never by eye), tab glyph and links, README status, the decisions file, board lanes, run tail, `git log`. It cites sources, names what waits on the human, and does not ask another seat to summarize. Where `status` says "unknown", the source it names is missing: say so rather than "nobody". |
| New system started | README roster under a `Roster` heading: `Seat \| Agent name \| Model \| Effort \| Start \| Brief \| Cwd` (optional `Agent`), as `watchbill restore` reads it. No session ids; `herdr-lifecycle siblings` holds liveness. `dev-docs/decisions.md` created. |
| Two sessions, one git index | Commit only your paths. The commit body names the steward impact. |
