# Laying out and starting a system

Read when you start a system, spawn a seat, or name or relabel a tab.

## Layout
- **One herdr workspace per system**, labelled by the configured `workspace_label` (default
  `<SUBJECT> system`). Every seat lives there.
- **Agent name = Claude `-n` address = tab slug:** `<subject>-builder`, `<subject>-steward`,
  `<subject>-build-<task>`, `<subject>-run-<task>`, `<subject>-<function>` for a standing lead or
  the editor (`report-editor`, `report-layout`), `<subject>-advisor[-<topic>]`. Keep the subject
  token to 8 characters and the task token to 10: the sidebar cuts labels at about 25 characters
  (`spawn --seat` warns when longer). Successor of any seat: `<name>-ho2`
  (`herdr-lifecycle next-name`).
- **Labels, glyph first:** `_ EVENTS BUILDER`, `_ EVENTS STEWARD`, `EVENTS BUILD · routing`,
  `EVENTS RUN · bookings`, `REPORT EDITOR`, `REPORT LAYOUT`, `↪ EVENTS BUILDER → ho2`.
- **Order:** builder, steward, build leads, run leads, standing leads (build or run) in the order
  they were started, advisors, historians last. A successor takes its origin's slot.
  `spawn --seat` places the tab.
- **Glyphs** (the lifecycle mark at the front of the tab label; set them with `herdr-lifecycle label <state>`, never by hand; a pane's state badge, `herdr pane report-metadata --state-label`, is separate and may be stamped directly):

| Glyph | State | `label` state |
|---|---|---|
| none or `_` | active (`_` = the live lead of its workspace) | `active` |
| `⏳` | waiting on someone or something other than the human | `waiting` |
| `?` | stopped on the human. Reason class in parentheses at the end: `? EVENTS STEWARD (sign-in)`. The workspace label carries `?` while any of its tabs does; every `label` call re-syncs it. Clear it when the human answers. | `human --reason <class>` |
| `👁` | parked builder, alive, watch armed | `watching`, or `herdr-lifecycle park` |
| `↪` | relief in progress from `handoff` until the receiver runs `relieve`; after that, historian | set by `handoff` |
| `✓` | done, for the human's review | `review` |
| `💤` | process exited, resume line typed | `parked` |

- **Tab or pane:** a tab for anything working on a different thing, which includes every seat
  and every fork. A pane (`--pane`) only for something short-lived and closely paired with the
  tab's resident: a teammate, a sub-agent you want to watch, a process.
- **Spawn a seat:** `herdr-lifecycle spawn --seat builder|steward|build|run|standing|advisor
  --subject <s> [--task <t>] --model <m> [--effort <e>] [--cwd <subject home>]
  [--agent watchbill:<agent>] [--resume <session-id>]`. It builds the name and label, sets
  `WATCHBILL_SEAT` for the new session, opens a new tab in its slot, **requires `--model` and
  refuses a forbidden model**, runs the configured headroom check if there is one, and records
  `launched_by` and `accountable` in the handoff ledger. For a standing lead, `--task` is the
  function (`editor`).
- **A `✓` tab closes itself** when the done signal its brief names appears (a file it can read,
  every mark resolved, an artifact published; not a board card, which nothing polls cheaply):
  `herdr-lifecycle exit --done "<the signal it saw>"`. An advisor leaves the same way when its
  question is answered. The human does not have to release either in words. A parked builder is
  never `✓`: it parks with `👁`.
- **A cross-subject fault** (infrastructure) goes to that subject's home, the configured
  `infra_home`, and its own workspace (`watchbill:infra-handoff`); it is not a seat of this
  system. With no `infra_home`, it goes to the human.
- Model and effort go in the brief and the roster, never in the name.

## Starting a system
0. **Check first.** Run `herdr-lifecycle siblings --all` and look in the subject's home for an
   existing system. If the human's request does not say, ask them once: what is the inbox, which
   tool reads and writes it, what do they decide, what can never be undone.
1. **Write the system README** with a section headed `Roster`: a table
   `Seat | Agent name | Model | Effort | Start | Brief | Cwd` (optional `Agent`), where Start is
   `resume` or `fresh` (the brief's choice). No session ids in the roster; `watchbill restore`
   finds them in the handoff ledger. Also the current rules, and a pointer to the decisions file.
2. **Write `dev-docs/owners.yaml`** (seat or agent name to path globs, plus `shared` paths),
   create `dev-docs/decisions.md`, and install the trailer check:
   `${CLAUDE_PLUGIN_ROOT}/hooks/git/install-commit-msg.sh <repo>`.
3. **Approval gate.** Show the human the roster and the gate. Spawn nothing and ask no seat to
   change anything until they say yes. No answer is not a yes. Record the yes (`SKILL.md`
   section 3).
4. **Create the workspace**: `herdr workspace create --label "<workspace label>" --cwd <subject
   home>` (`watchbill restore` finds it by that label, a leading `?` ignored), and pass
   `--workspace` on every spawn. Spawn the builder (tab 0) from
   `skills/builder/references/brief-templates.md`. When the steward's rules exist, spawn the
   steward (tab 1) in the primary checkout from `skills/steward/references/brief-template.md`. A
   system with no inbox has no steward; its builder closes out after the gate instead of parking.
5. **Scheduled fallback.** With the configured `scheduler` at `none`, write "none" in the roster
   and tell the human that nothing restarts a seat that dies until they or `watchbill restore`
   do. With a scheduler, the roster names what it restarts.
6. Follow any registration duties the overlay file names (anchors, registries).
