# Collaborating with a session in another workspace

**What this is:** the rule for one seat depending on a session outside its own system (another
system's architect, a design session), and the `herdr-lifecycle collab` records that back it.
**For:** any seat about to ask, wait on, or be asked by such a session, and any seat handing off or
closing out while one exists.

**The rule:** when you depend on another session, write it down where both of you and your
successors will find it, and read the other side's rules before you approach.

## Why a record, not just messages

Four things end a session's memory of a conversation, and only one leaves a trace:

| Transition | Session id | Name | Memory of the thread | Leaves a record |
|---|---|---|---|---|
| Handoff (`x` → `x-ho2`) | new | `-hoN` | gone | yes: the lifecycle ledger |
| `/clear` | new | unchanged | gone | no |
| Restore (reboot, resume) | same | same | kept | no |
| Compaction | same | same | partial | no |

(`/clear` keeping the name is documented in Claude Code's changelog, not tested here.) A thread
held only in conversation can disappear with no signal to the other side. The **record** is the
load-bearing part: after a handoff the origin remembers the thread but no longer owns the work, and
the successor owns the work but has never seen the thread. Only the record can say where you are.

## Before you approach a session you have not worked with

Read its system's `dev-docs/watch.md` or README first: that is where the rules you are about to
break are written (an architect once landed on another system's repo and left it red; the rule
against it was in that repo's `watch.md`). Find its address with `herdr-lifecycle siblings --all`,
which prints the tab label beside the address; never guess an address from a label. A pane's
STATUS (`idle`, `done`) says what it is doing this second, not whether it is a party to your work:
consult a peer whose STATUS reads `done` like any other.

## Recording it

**Hold only when your gate or your exit depends on the other side's action**: a commit you need
before your gate can close, an answer your design waits on. Never for an FYI, a feedback round, or a
request answered in the same sitting; never between seats of one system (the roster and the launcher
of record already tie them; `collab open` refuses); never on a sub-agent (not a session; its spawner
tracks it). The session that needs the other (the **holder**) opens a thread:

```
herdr-lifecycle collab open <peer> --for "<what you need>" --record <file or commit> \
  [--outstanding "<what is still open>"] [--protocol <what to read before approaching it>]
```

`open` prints the line to send the peer now (so it does not learn of the hold only when it tries to
exit) and the peer's own rules to read first. The holder also writes the edge into a file it keeps (a parked architect's `watch.md`, a README, a
brief), with three lines: who holds whom and for what, the **release** condition anyone can check,
and the **record**. `herdr-lifecycle siblings` shows "held by <holder>" and "holds <peer>".

- **Waiting on the peer's answer:** `herdr-lifecycle label waiting --to <peer>` (`⏳ … → <peer>`).
  No other glyph: a hold where nobody is waiting needs none.
- **A check-in:** `collab ping <peer> --question "<one line>"` records it; then send the message.
  Nothing pings on a timer.
- **Release** is the holder's alone, and one record per direction: `collab release <peer>`, or the
  holder's own closeout (`herdr-lifecycle closed`), which releases what it held. The held side never
  negotiates to be let go. **Silence is never release:** a quiet holder may be mid-work or waiting
  on the human.

## Two duties

**Handing off.** `herdr-lifecycle handoff` prints the open threads (`open_collaborations`) with a
line to send each peer. Put every one in the briefing with its record and release condition, and
send each peer that line: your successor's name, and that it has not seen the exchange.

**Parking.** `herdr-lifecycle park` lists the holds you still have: a parked seat lives for days, so
release what you no longer need before you park.

**Closing out or exiting.** `herdr-lifecycle collab status` exits 0 when nobody holds you, 1 when a
live holder has not released, 2 when a holder is not running and has not released. On 1, ask it
("may I close? what remains?"); if it stays silent, label yourself `herdr-lifecycle label human
--reason "collaborator silent: <peer>"` and ask the human. `herdr-lifecycle exit` (plain or
`--done`) refuses on 1; `--force` is the human's override. On 2 it proceeds, records the release as
`holder-gone` and prints the holder's record: a holder that died at a usage limit must not keep a
session open for days, and if it is restored, its own record says what it needed and it opens the
thread again. Leave a dated note in your record when you close while a thread is open.

## What the records cannot see

- **A `/clear` drops the thread.** It starts a new session id under the same name and writes nothing
  to the ledger (documented in Claude Code's changelog, not tested here). After the holder clears,
  the held side reads it as not running (code 2) and may exit; after the held side clears, it is no
  longer held. Either side that clears opens the thread again from its record.
- **A fork** remembers the whole thread but is a new session with no row: it holds nothing and
  cannot release. Release from the session that opened the thread, or its successor.

## When the peer may have changed under you

If its address now has a higher `-hoN`, you are writing to a historian: fine for history questions,
which are its job, but the work has moved and the successor has not seen your exchange. Cite the
record instead of referring back. After a peer's `/clear` the same is true with no trace at all.
