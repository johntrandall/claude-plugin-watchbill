# watchbill

A role model for multi-agent work in [herdr](https://herdr.dev) with a human in the loop,
packaged as a Claude Code plugin. A watch bill is the roster that says who stands which watch,
who relieves whom, and who keeps the log. Here the watches are the seats agents hold, relief is a
two-party handoff, and the log is commit trailers, item records and a historian.

**One seat changes the rules, another runs the work, and every relief leaves a log.**

It is for anyone who runs a standing agentic system (an inbox of items worked under written
rules) or a build cycle with several agents, and wants each agent to know what it may write,
whom it answers to, and how the human's decisions are recorded.

## The seats

| Seat | Write class | Manages | Lives |
|---|---|---|---|
| **Builder** | rules | the system's rules: schema, code, skills, briefs, README. Edits in a git worktree, lands with `watchbill land` between the steward's items, watches outcomes after the gate | tab 0 of the system's workspace; parks there with `👁` while its watch is armed |
| **Steward** | work | the inbox: new items, the human's decisions, confirmations, under the current rules; stamps the rules SHA on every item | tab 1, in the primary checkout |
| **Build lead** | rules | one bounded rules task, inside the files its brief assigns | its own tab; closed by the builder once its report is filed |
| **Run lead** | work | a chunk of work under the current rules; sends rule problems, never edits rules | its own tab; closed by the steward |
| **Editor** | work | one document's text with the human, as signed Track Changes suggestions | a standing run lead |
| **Advisor** | nothing | answers design questions on call | a tab, no glyph |
| **Crew** | work or nothing | one step each, fresh context: worker, reader, verifier, backfill, checker, escalation | sub-agents, never a tab |
| **Historian** | nothing | history questions after a handoff | `↪` tab, last |

Builder and steward run side by side and message each other only with information (no acks, no
pauses). A message from another agent never carries the human's authority, and silence is never
consent: an approval is a recorded decision, bound to one change and spent once.

## What is in the plugin

| Part | For |
|---|---|
| `skills/` | `watchbill` (the map), `builder`, `steward`, `delegation`, `paper-trails`, `watchers`, `collaborative-drafting`, and the session skills (`handoff-session`, `historian`, `multi-agent-routing`, `monitoring-mode`, `herdr-workspace-placement`, `role-relaunch`, `infra-handoff`, `lead-and-crew`) |
| `agents/` | one agent per seat and per crew sub-type, with model, effort and tools pinned (`--agent watchbill:builder`, `subagent_type: watchbill:reader`) |
| `hooks/` | session context (configuration, overlay, the seat's primer), an ownership warning from `dev-docs/owners.yaml`, a model guard, a hold guard, a context-band notice, and a commit-msg check for `Watchbill-Event` trailers |
| `bin/` | `herdr-lifecycle` (spawn seats, labels and glyphs, two-party handoff and relief, park, exit), `watchbill` (`status`, `land`, `rules-sha`, `restore`, `config`, `context`, `check-note`, `hold`, `install-links`), `criticmarkup.py` (Track Changes from the command line) |
| `evals/` | cases for `claude plugin eval` |

## Install

Requirements: Claude Code, [herdr](https://github.com/herdrdev/herdr) (tested on 0.9.3), Python 3
(PyYAML optional). Optional: Obsidian with the Track Changes plugin, for collaborative drafting.

```
/plugin marketplace add johntrandall/watchbill
/plugin install watchbill@watchbill
```

The plugin's `bin/` is on the Bash tool's PATH inside Claude. For launchers and shells outside
Claude, run `watchbill install-links` once after each update: it points `~/.local/bin` links at
the installed copy. To try a clone without installing: `claude --plugin-dir <clone>`.

## Configuration

Nothing about you is built in. Set values in `/plugin configure watchbill@watchbill`, or from a
shell with `claude plugin configure watchbill@watchbill --values-stdin`. A
`WATCHBILL_<KEY>` environment variable overrides a configured value. `watchbill config --explain`
prints every value and where it came from; a SessionStart hook prints them into each session's
context, so skills and agents can stay in generic wording ("the human", "a forbidden model").

| Option | Default | What it does |
|---|---|---|
| `human_name` | `the human` | how seats name you |
| `forbidden_models` | none | models no seat may spawn or launch; the model guard denies them |
| `require_explicit_model` | true | remind a seat when a generic Agent call names no model |
| `alert_channels` | `tab glyph only` | how a seat stopped on you gets your attention, in order |
| `decision_channels` | `chat` | where you give decisions; each system's brief names its channels from this |
| `drafting_tool` | the bundled `criticmarkup.py` | the Track Changes tool |
| `drafting_author` | your `human_name` | the author your Track Changes marks carry |
| `headroom_command` | none | a check spawn runs first; non-zero refuses the spawn |
| `scheduler` | `none` | what may restart or wake a seat; with `none`, nothing does |
| `infra_home` | none | where a fault outside a system's subject is handed; with none, to you |
| `workspace_label` | `{SUBJECT} system` | the herdr workspace label per system |
| `overlay_file` | none | a private markdown file of your own rules, printed into every session at start |
| `relief_deadline_minutes` | 30 | how long either side of a relief waits before `relief-check` acts |
| `handoff_offer_tokens` | 400000 | context size at which a seat offers you a handoff, for cost |
| `handoff_hard_percent` | 85 | percent of the window at which a seat hands off |
| `context_window_tokens` | 1000000 | the window size the percent is taken of |

**The overlay file** carries rules that are yours alone (which shelf a monitoring session moves
to, which sign-in screens an agent must never complete, what memory a brief should not load).
If it is configured but missing, the session context says so.

## Starting a system

Ask any session to set up a watchbill system for a subject; `watchbill:watchbill` routes it. In
short: one herdr workspace per system; a README with a `Roster` table; `dev-docs/owners.yaml`
(who writes what) and `dev-docs/decisions.md` (your decisions); the trailer check installed with
`hooks/git/install-commit-msg.sh`; your yes to the roster and gate before anything is spawned.
`watchbill status <system-dir>` answers "who has the ball" from records; `watchbill restore
<system-dir>` brings seats back after a usage limit or a reboot.

## Licence

MIT. See `LICENSE`. Changes: `CHANGELOG.md`.
