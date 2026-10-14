---
name: historian
type: procedure
description: "How a handed-off origin (tab ↪) behaves and ends: stay idle in the project workspace answering history questions, redirect new work to the head of the chain, never poll, exit only when herdr-lifecycle historian-check allows it or the human says so, the exit steps, the proxy historian for an origin out of context, and what the head owes its historians at closeout. Auto-invoke after you hand off, when a historian receives a message, or when the head of a chain closes out."
tags: [agents, handoff, historian, herdr, watchbill]
---
> Where a global skill disagrees with the watchbill plugin on a decided point, the plugin's rules win (list: `watchbill:watchbill`, top).


# Historian

After a session-scoped handoff (`watchbill:handoff-session`) the origin is a **historian**: it
holds the history behind the briefing and does no more work on the task. **Only a top-level
session the human talks to is a historian.** Never run any step here from a sub-agent, fork or
teammate: they inherit the lead's session id, so `herdr-lifecycle whoami` answers with the lead's
pane, and an exit would close the lead.

## 1. While waiting
- **Stay idle in your project workspace.** Not on a WAIT or MONITORING shelf: `siblings` and
  `announce_to` are workspace-scoped, and the `↪` glyph already shows the state.
- **Answer history questions** from context. **Redirect new work** to the head of the chain (the
  highest `-hoN`) in one line.
- **Never poll in your own context:** no wakeups, no re-armed monitors, no "are you done?"
  messages. You may arm one zero-context backstop right after the handoff, in the background:
  `until herdr-lifecycle historian-check --quiet; do sleep 600; done`.

## 2. When to exit
The head's closing message wakes you; it is not proof. Run `herdr-lifecycle historian-check`:

| Exit code | Meaning | Action |
|---|---|---|
| 0 | Every head of your chain finished its closeout, or (standing chains: builder, steward, standing lead, advisor) the successor ran `relieve` | Exit (section 3) |
| 1 | A head is still live | Keep waiting |
| 2 | A head is gone without closing out | **Do not exit.** Tell the human in one line and wait for their word: you may now hold the best context on the work |
| 3 | Not a historian, or task-scoped | Not your exit |

Never exit on silence, on a timer, on herdr's `done` status (that only means a turn ended), or
because the chain moved to a further `-hoN` (wait for the new head). The human's word always
suffices (`exit --force`).

## 3. Exit steps (no re-scan)
1. Answer, or explicitly decline, any pending question.
2. `git status --porcelain -- <paths you touched>`: list anything there to the human; never
   commit it blind.
3. No teammates left; delete leftover tasks.
4. Fill the Pairs row's "Historian exited" (`<date>, head closed` or `<date>, human`); clear the
   anchor links your setup keeps.
5. Last action: `herdr-lifecycle exit --relabel-shared` (`--force` only on the human's word). It
   resolves your pane from your session id, never from `$HERDR_PANE_ID`, relabels a tab shared
   with a live receiver, and types `/exit` into your own pane. End the turn.

`claude --resume <your session id>` revives you later; the Pairs row keeps the id.

## 4. Proxy historian
If the origin ran out of context ("Prompt is too long" on every turn) it cannot do any of this.
The session cleaning up tells the human, tries one `/compact` in the origin's pane if they agree
(typing into a pane is right for a TUI command), and otherwise closes that one pane by id
(`herdr pane close <pane>`; never close a whole workspace, which ends every agent in it). It then
answers history questions from the origin's transcript and records `proxy: <its name>` in the
Pairs row.

## 5. What the head owes its historians
At its own closeout, **before** self-shutdown, the head runs `herdr-lifecycle closed` (it records
the close and prints the historians to tell), then sends each one message. A head that skips this
leaves its historians waiting until the human steps in. Liveness is "does the pane still exist",
not "is the pid alive": pids are reused.
