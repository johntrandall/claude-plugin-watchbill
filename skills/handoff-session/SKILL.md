---
name: handoff-session
type: procedure
description: "Starting a successor or an independent Claude session in its own herdr tab: when to offer a handoff (85 % context, or the cost band), releasing what only you hold, the briefing, spawning with herdr-lifecycle, the fork variant that carries your history, verifying the spawn, relabelling and announcing, and stepping back. Auto-invoke when context nears 85 % or about 400K tokens, or when asked to hand off, fork, or start a new session for a task."
tags: [agents, handoff, herdr, watchbill]
---
> Where a global skill disagrees with the watchbill plugin on a decided point, the plugin's rules win (list: `watchbill:watchbill`, top).


# Handoff session

A **handoff** starts a new top-level session in its own tab with a briefing and clean context; it
answers to the human, not to you. A **fork** is the same with your conversation copied in. For an
answer that comes back to you, use a sub-agent instead (`watchbill:multi-agent-routing`). In a
watchbill system a seat's handoff is two-party relief (`skills/steward/references/handoff.md`):
follow that for the order of steps and use this skill for the mechanics.

## 1. When to offer one
- **Offer a handoff at the cost band** (`handoff_offer_tokens`, shown in your session context;
  default about 400K tokens), in one short message: where you are, what is left, and that the
  handoff includes the small closeout subset in section 2. Every turn re-reads the whole context,
  so a large window costs more each turn.
- **At 85 % of your context, hand off** (`handoff_hard_percent`): this is the hard line, not an
  offer. In away mode, hand off without asking. A good briefing needs real context; at 95 % there
  is none left. Read the figure from the status line or `watchbill context`, never guess.
- Handoff or fork: fork only when the receiver needs this conversation and your context is small
  (under about 20 %). Otherwise distil a briefing; it gives better context than a raw transcript.

## 2. Release what only you hold (before the briefing)
Only a top-level session the human talks to hands off; never a sub-agent, fork or teammate.
Budget: a handful of tool calls. Everything about the work's outcome (verify, scans, push, report)
belongs to the receiver's closeout, which covers the whole chain.
1. **Commit your own hunks, path-scoped** (`git commit -m … -- <paths>`). List any uncommitted
   change you cannot attribute in the briefing; never commit it blind, never discard it.
2. **Teammates and browsers:** shut your teammates down (choose "Exit and stop tasks", never
   "Move to background"); close the browser tabs you opened.
3. **Into the briefing:** your open tasks, the URL of every shared card you claimed, your anchor
   links if your setup keeps them, the historians in this chain, and every open collaboration
   (`herdr-lifecycle handoff` prints them as `open_collaborations`, each with its record and the
   line to send that peer: your successor's name, and that it has not seen the exchange;
   `watchbill:watchbill` section 2, its collaboration reference). Do not re-read the cards now;
   the receiver has the budget for that.
4. If your setup keeps a session memory, write its summary now. Add one dated paragraph to the
   project README or log: what you did, what you learned, what is left.

## 3. The briefing
Durable work gets a briefing **in the project**, committed (`herdr-lifecycle handoff --brief`
requires that for a seat). Only a one-shot question may use a temporary file. The briefing
points at the project README; it does not copy it, and it never tells the receiver to create a
`HANDOFF.md` as the project's main document. Template:

```markdown
# Task: <title>
## Take over from the origin (first, before any work)
- Cards: <URLs>. Re-read each, comment done/left, point its restore trail at your session id. It stays in progress.
- Anchors: <links>. Register each on your own status line, then tell the origin.
- Tasks: create these in your task list, then message the origin "adopted: <ids>": <subject + full description, by id>
## Historians in this chain
- <name> — <session id> (oldest first; carry forward on every further handoff)
## Why, what was rejected, what the human cares about
<decisions with their reasons; options tried or rejected and why; the human's stated preferences.
Write them here: transcripts get cleaned up, so pointing at one fails.>
## The work
<state, open items, gotchas, file paths, commit SHAs>
## Completion
1. Verify with an independent verifier sub-agent; record what was verified.
2. Run your closeout; it covers the whole chain.
3. Before self-shutdown: `herdr-lifecycle closed`, then message each historian it prints.
4. If you hand off again, do section 2 instead and copy the historian list with yourself added.
```

## 4. Spawn
```bash
herdr-lifecycle spawn <name> --new-tab --tab-label "<label>" --cwd <dir> -- \
  --model <model> --permission-mode auto \
  --append-system-prompt-file <briefing> 'Read the briefing and start with its first section.'
```
- **A tab, not a pane.** Pass `--new-tab`; without it `spawn` splits your pane. A pane is only for
  something short-lived and paired with you (a teammate, a watched sub-agent, a process). A seat
  uses `spawn --seat …` (`watchbill:watchbill`).
- **Name:** a successor is `herdr-lifecycle next-name` (`<you>-ho2`); a new task gets a fresh
  slug. `spawn` passes `-n <name>`, so the herdr name, the Claude address and the title are one
  string, and it refuses a name that is already live.
- **Model, every time**, and never a forbidden model (the session context lists them).
- **Prompt at launch**, never by keystrokes afterwards. Long or quoted text goes in the file.
- **Never launch `claude` from a non-interactive shell string** (`bash -c "claude …"`): it skips
  the shell profile and anything the setup installs there.
- If a headroom check is configured and says no (exit 3), wait. Override only with the human's
  OK and give the reason.

**Fork variant.** Write the scope to a file first: "You are a forked session. Your only task:
<task>. Do not work on anything else; the origin handles the rest. If unsure whether something is
in scope, ask the human." Then:
```bash
herdr-lifecycle spawn <slug> --new-tab --cwd "$PWD" -- --model <model> \
  --resume "$CLAUDE_SESSION_ID" --fork-session --append-system-prompt-file <scope-file>
```
A fork without `-n` takes the parent's name, so two sessions answer to one address; `spawn`
prevents that. To fork from an earlier point, add `--resume-session-at <assistant message uuid>`
(undocumented; check it on your version). Mark your matching tasks handed off. If you only want
the result back, use the Agent tool's `subagent_type: "fork"` instead.

## 5. Verify, then report
- `spawn` prints `{"name", "pane_id"}`; keep the pane id from that output, never find it by
  listing afterwards.
- Session id: `herdr agent get <name> | jq -r '.result.agent.agent_session.value'`.
- `herdr-lifecycle siblings`: listed, no collision note.
- If start reports "blocked during startup", the process may be alive on the folder-trust dialog:
  `herdr pane read <pane> --source recent-unwrapped --lines 40`. Trusting a folder is the human's
  call; do not retry the spawn.
- Report: session id, Claude address, `claude --resume <id>`, pane id, and how it ends (its own
  closeout, or the human runs `herdr pane close <pane>`).

## 6. After the spawn: relabel, announce, step back
1. `herdr-lifecycle handoff <receiver>` (`--brief <path>` for a seat, `--scope task` when you hand
   off one task and keep working). Preview with `--dry-run` first. It relabels your tab
   `↪ <topic> → hoN`, prints the receiver's label, `announce_to` and an `announcement`. Rename the
   receiver's tab to that label.
2. Send the announcement to each `announce_to` session and your launcher, then one message to the
   receiver: "From the origin of your handoff (`<session id>`, tab `↪ <topic> → hoN`). I hold the
   history behind the briefing; ask me anything historical while my tab is open. I will not touch
   the task's files. At your closeout, before self-shutdown, run `herdr-lifecycle closed` and
   message me."
3. Record the pair in the project README's **Pairs** table: `Date | Origin (name, session id) |
   Receiver (name, session id) | Scope | Historian exited`. The ledger has it too; the README row
   outlives both tabs.
4. Delete your copies of the transferred tasks (status `deleted`, not `completed`) once the
   receiver shows them: read its pane footer once (`herdr pane read`), or wait for its
   `adopted:` message. A sent message is not adoption.
5. **Step back.** No edits to the handed-off files. (A watchbill seat runs `handoff --brief` before
   the spawn and keeps the seat until the receiver runs `relieve`: `skills/steward/references/handoff.md`.) A session-scoped origin is now a historian
   (`watchbill:historian`); a task-scoped origin is not.

**Origin already gone** (out of context, or exited before section 6): the message in step 2 would
be false. A live session sends the receiver the origin's transcript path
(`~/.claude/projects/<project-dir>/<session-id>.jsonl`), names itself as the one that answers from
it, and writes the briefing items from the transcript; it lists the origin's uncommitted hunks
rather than committing them.

## 7. The handoff is independent
The launcher never closes a handoff; it ends at its own closeout or when the human closes it. If
you want to launch several agents, collect their results and end them, you want sub-agents or a
crew (`watchbill:lead-and-crew`). To check on one, read it, never type into it:
`herdr agent read <name> --source recent-unwrapped --lines 100`. **Idle is not done:** check the
work itself (commits, files, the task list), not the self-report. Follow-up messages go by
`SendMessage` (`watchbill:multi-agent-routing`).
