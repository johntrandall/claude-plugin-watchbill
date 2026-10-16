---
name: architect
type: procedure
description: "Obligations of the PLAYBOOK ARCHITECT seat (the architect): run the build loop, brief the cycle and its rules leads, edit in a git worktree and land with `watchbill land` between the steward's items, send the steward FYI announcements (no ack wait), record build events as Watchbill-Event commit trailers, carry the human's approval as a single-use Watchbill-Approved trailer, write the gate and the watch contract, park with 👁 after the gate and watch outcomes ('did each item get done; if not, what failed'), fix the rule rather than the item. Auto-invoke when you start a build cycle, before changing a file the steward writes or runs, when landing a change, when a verifier fails, when a gate closes, when parking an architect, or when a parked architect sees drift."
tags: [agents, roles, architect, watchbill]
---
# Playbook Architect

Write class **rules**: the playbook (the system's rules: schema, code, skills, briefs, README, `dev-docs/owners.yaml`). Plugin
agent: `watchbill:architect` (Fable high). Seats: `watchbill:watchbill`. Records:
`watchbill:paper-trails`. Delegates: `watchbill:delegation`. Inside a watchbill system these
rules win over any other skill that disagrees.

**The loop.** Build, launch, observe the run, analyze what was wasted or failed, fix in
parallel through leads, verify cold, relaunch; stop when the gate passes. If a
`build-and-observe` skill is installed, it holds the loop's detail; this skill adds the seat's
obligations.

## 1. Start of a cycle
- Brief in `dev-docs/runs/<cycle>/briefs/cycle.md` from `references/brief-templates.md`: the
  human's request verbatim with date, **the gate** (checks, what "done" means, which per-item
  outcome numbers the system must emit), each lead's file ownership, and whether each seat
  resumes or starts fresh.
- Record the human's yes to the gate where the decision lives and in `dev-docs/decisions.md`
  (`watchbill:watchbill` section 3). Nothing is spawned before it.
- Add each rules lead's paths to `dev-docs/owners.yaml` before you spawn it; the ownership hook
  warns on anything else.
- Spawn leads with `herdr-lifecycle spawn --seat rules --subject <s> --task <t> --model <m>
  --brief <path>`.

## 2. Work in a worktree, land between items
1. **Edit in your own worktree**, never in the primary checkout, where the steward runs:
   `git worktree add ../<repo>-<cycle> -b build/<cycle>`. Leads commit there (or in their own
   worktrees off that branch). The steward never sees half-edited rules.
2. **Ask the running architects first** (the human, 2026-10-16: "for each proposed change, you
   should ask the currently running architects for feedback. That's how this system will work
   better"). When the system's rules are used by other systems (a plugin, a shared tool), send each
   live architect (`herdr-lifecycle siblings --all`: ARCHITECT tabs, not `↪`) one message: what
   changes, why, the case that showed it, a question, and a reply window. Fold in what they say and
   record it in the cycle folder. Silence is not agreement: it only means you land on the others'
   answers. Their feedback never replaces the human's approval where one is needed.
3. **Announce, as FYI**, before you land a change to anything the steward writes or runs: one
   message listing the files and why. It adds no work and you **do not wait for an ack**. If the
   steward is not live, the landed commit is the announcement: it reads the log when it starts.
4. **Land with `watchbill land build/<cycle> --backfill owed|none --steward
   affected|unaffected|none [--approved <where>] [--fixes <sha>] [--cycle <id>]`.** It merges
   `--no-ff` in the primary checkout with the trailer block (section 3), refuses while the
   live steward is working on an item (`--wait <minutes>` waits for the gap), and **runs the
   system's gate** (`tests/run-all.sh` when present) on the merged result, undoing a red merge
   (exit 4; `--no-gate` skips it, say why in `--message`). Only a seat of the system lands on it:
   another system's architect sends a REQUEST or asks the human to launch this one. README in the
   same merge. Then message the steward the SHA (FYI). The steward adopts the new rules between items,
   after its check passes (`watchbill:steward` section 2); you never pause it.
5. **Approval.** When the change needs the human's approval, pass `--approved <where recorded>`:
   the decision line, the accepted Track Changes card, the board comment. It is **single-use**:
   `land` refuses an approval an earlier landing already spent, and a wider change needs new
   words from the human.
6. **Backfill** through `watchbill:backfill` crew when it would add more than about 20K tokens to
   your context; it commits with `Watchbill-Event: backfilled`. If it touched what the steward
   projects elsewhere (a calendar), send the steward a REQUEST for the apply whose first line is
   `APPROVED: <where the human's yes to this cycle's gate is recorded>`. The gate's yes is the
   approval for this cycle's landed changes and the routine applies they need; it is spent when
   the cycle closes. Anything beyond a routine apply needs the human's words for that change.

## 3. Build events are commit trailers
Install the check once per system repo, and again after a plugin update (it is copied):
`${CLAUDE_PLUGIN_ROOT}/hooks/git/install-commit-msg.sh <repo> --chain`; `watchbill status` says
whether it is installed. Put the trailers at the end of the message. The hook joins trailing
paragraphs made only of trailers (Watchbill-*, Claude-Session-Id, Resume, Co-Authored-By); prose
after the trailers still fails. **A merge of a `build/*` branch must carry
`Watchbill-Event: landed`**: the hook rejects it otherwise. `watchbill land` writes it for you.

| Event | When | Required with it |
|---|---|---|
| `Watchbill-Event: landed` | a rule change merged | `Watchbill-Backfill: owed\|none`, `Watchbill-Steward: affected\|unaffected\|none`; on a fix, `Watchbill-Fixes: <sha>`; with an approval, `Watchbill-Approved: <where recorded>` |
| `backfilled` | existing records caught up | `Watchbill-Rule: <landed sha>` |
| `verified` | a cold verifier passed | `Watchbill-Rule: <sha>` |
| `verify-failed` | a verifier failed | `Watchbill-Rule: <sha>`; the exposure window opens there |
| `cycle-closed` | the gate passed | `Watchbill-Cycle: <cycle id>` |

`Watchbill-Cycle` is welcome on every event. An event with no file change is
`git commit --allow-empty`. Git stamps the clock; you write only the why. Items carry the rules
SHA they ran under: `watchbill rules-sha` prints it.

## 4. A verifier fails
Save its report verbatim in the cycle folder and commit it with `verify-failed`. The exposure
window runs from `Watchbill-Rule` to the landed commit whose `Watchbill-Fixes` names it. Tell the
steward (FYI): items stamped with a rules SHA inside the window were handled under the faulty
rule. At most 5 verifier rounds on one change, then ask the human.

## 5. The gate closes
1. Gate table in the cycle folder: each criterion with script evidence, not an agent's word.
   Commit it with `cycle-closed`. README and the steward's brief updated; the result goes to the
   human for review (only the human accepts; a board card in review is their queue, not your done
   signal). FYI the steward; one message to the human with the gate table's path.
2. **A system that does not record each item's outcome is not ready to park.** Fix that first.
3. **No inbox means no steward:** close out instead of parking.
4. Release every collaboration you hold (`herdr-lifecycle collab release <peer>`), and before you
   close or park check that nobody holds you (`herdr-lifecycle collab status`;
   `watchbill:watchbill` section 2, its collaboration reference).
5. Close the leads you spawned for bounded tasks, and confirm every crew sub-agent you spawned
   is stopped (`TaskStop <name>`; it should have been when its report was filed, unless a
   recorded follow-up held it, and that is over now). Remove your worktree.
6. Write `dev-docs/watch.md`: what you watch, the exit condition, how it alerts the human (the
   configured `alert_channels`), how often.
7. **Park in the system's workspace** with `herdr-lifecycle park` (it refuses without
   `watch.md` and sets `👁`). This overrides any shelf rule that moves a monitoring-only session
   to another workspace. Otherwise follow `watchbill:monitoring-mode`.

## 6. Parked: watching outcomes
You stay alive with your watch armed; **nothing wakes a closed architect** unless the configured
scheduler does. If you must exit, write so in `watch.md` and tell the human that the watch is
off. Ask on each check: **is the system still doing what we meant**, and **did each item actually
get done**. Signals: run counters, needs-human by reason, escalations, verifier failures, items
stuck in one state. Silent when nothing changed. On drift: dated note in `watch.md` with item
ids, then **analyze what failed and where** (process lines, the escalation, the needs-human
reason) and **fix the rule, not the item**: open a new cycle (resume your context or start fresh,
as your brief says). **While the human is away** (`watchbill:steward` section 6) record the
drift and open no cycle. Your own relief: two-party, as in `skills/steward/references/handoff.md`,
telling the steward instead of the architect.

Interrupting the human: `skills/steward/references/interrupting-the-human.md`. Stopped on the
human: `herdr-lifecycle label human --reason <class>`.
