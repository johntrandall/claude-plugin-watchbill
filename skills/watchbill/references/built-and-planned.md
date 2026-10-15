# Built today and planned

Read this before relying on any tool a skill names. Anything not in the first table is not built.

## Exists today

| Piece | Where | Notes |
|---|---|---|
| Seven plugin skills | `skills/` | watchbill, architect, steward, delegation, paper-trails, watchers, collaborative-drafting; plus the session skills (handoff-session, historian, multi-agent-routing, monitoring-mode, herdr-workspace-placement, role-relaunch, infra-handoff, lead-and-crew) |
| Twelve plugin agents | `agents/` | seats architect, steward, rules-lead, run-lead, editor, advisor; crew worker, reader, verifier, backfill, checker, escalation; model, effort and tools pinned |
| Configuration | `plugin.json` options, `watchbill config [--explain] [--json] [KEY]` | order: `WATCHBILL_<KEY>` env, the plugin's options in user settings, the code default. The overlay file is printed into context at start |
| Session context hook | `hooks/session_context.py` (SessionStart: startup, resume, clear, compact) | prints the resolved values, the overlay and, for a seat, its primer (seat, brief, owned paths). Silent outside a watchbill system unless the session is a seat |
| Ownership hook | `hooks/ownership_warn.py` | PreToolUse on Edit, Write, MultiEdit, NotebookEdit, Bash; compares the target with `dev-docs/owners.yaml`, keyed by seat kind or agent name (or its `-hoN` origin); **warns only**; silent without an owners file |
| Model guard | `hooks/model_guard.py` | inside a watchbill system: denies an Agent call or a `claude` launch with a model forbidden for the launched role (`forbidden_models`, empty by default; `<role>: <models>` entries are per role), `ANTHROPIC_MODEL` set to one, and, with `require_explicit_model`, a `claude` launch or plain `spawn` with no model; reminds when a generic Agent call names no model. Quoted text never matches |
| Hold guard | `hooks/hold_guard.py` | while `.watchbill-hold` (or `watchbill-hold.md`) exists at a vault or repo root, denies writes under it, and its deletion. Only the human creates or deletes it; `watchbill hold <path>` reports which file holds and since when |
| Context band | `hooks/context_band.py`, `watchbill context` | tells a seat once when it crosses `handoff_offer_tokens` (offer a handoff) and on every prompt past `handoff_hard_percent` (hand off) |
| Trailer check | `hooks/git/commit-msg`, installed per repo by `hooks/git/install-commit-msg.sh` (copied: re-run after an update) | rejects malformed `Watchbill-*` trailers; joins trailing trailer paragraphs into one block; a merge of `build/*` must carry `landed` |
| `herdr-lifecycle` | plugin `bin/`, linked from `~/.local/bin` to the installed copy by `watchbill install-links` | spawn (`--seat`, sets `WATCHBILL_SEAT`, `--brief`), label (`active`, `waiting`, `human`, `watching`, `handed-off`, `review`, `parked`), siblings, next-name, handoff (`--brief`, required for seats), relieve (`--watch FILE`), relief-check, park, promote, closed, historian-check, exit (`--done <signal>` for a `✓` tab or an advisor). `label`, `exit` and `closed` keep the workspace's `?` in sync |
| `watchbill` | plugin `bin/` (on PATH while the plugin is enabled; elsewhere `~/.local/bin/watchbill`) | `status <system-dir>`: the ball from roster, siblings, the decisions file (an answer inside an unaccepted suggestion is still open), the run manifest's `needs_human`; rules SHA, recent landings with their approvals; "unknown: <source>" where a source is missing. `land <branch>` (below). `rules-sha`. `restore <system-dir> [--dry-run] [--stalled]`. `check-note <file>`. `hold`. `context`. `config`. `install-links [--dev DIR] [--check]` |
| `watchbill land` | | `land <branch> --backfill owed\|none --steward affected\|unaffected\|none [--approved WHERE] [--fixes SHA] [--cycle ID] [--wait MIN] [--dry-run]`: merges `--no-ff` in the primary checkout with the trailers; refuses while the live steward is working (`--wait` polls); refuses an approval already spent |
| Handoff ledger | `~/.local/state/herdr-lifecycle/handoffs.jsonl` (override `HERDR_LIFECYCLE_LEDGER`) | rows carry `launched_by`, `accountable`, `schema_version` 2; handoff and relieve rows carry the relief deadline |
| Drafting tool | `obsidian-track-changes-agent` from the obsidian-track-changes-agent plugin (or the configured `drafting_tool`); no longer bundled | list, check, suggest, comment, block, revise, accept, watch; refuses every write while a hold is on |
| Eval cases | `evals/` | `evals/run-clean.sh` |

## Planned, and what to do until then

| Planned | Until it exists |
|---|---|
| Ownership hook in BLOCK mode | treat a warning as a stop: ask your launcher or the human |
| `watchbill-watch` (shared watcher with adapters) | `obsidian-track-changes-agent watch` for review marks; otherwise a one-shot script in the repo that follows the watcher contract |
| Liveness registry | `herdr-lifecycle siblings` |
| Away mode's daily dead-man check | none runs unless the configured scheduler provides one; tell the human before they leave (`watchbill:steward` section 6) |
| Scheduled fallback or wake for a steward or parked architect | **none** with `scheduler` at `none`; say so in the README roster |
| Run-manifest and escalation-log tools with computed counters | the subject's own tools; never type a count |
| `watch.md` template | the fields in `watchbill:architect` section 5 |
| A successor keeping its origin's address | the successor is `<name>-hoN`; a live session's address can be moved with `/rename`, but no tool does it yet |
| Claiming an item before working it (`claimed_by` on the record) | one steward per inbox |
| The unattended contract (durable record, independent gate, deferred review queue, time-to-live) | `skills/delegation/references/delegation-model.md` section 7; unattended work is not built |
