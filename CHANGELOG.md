# Changelog

Rules in the skills are stated as rules; this file keeps when each was decided and what it
replaced.

## 0.4.5 (2026-10-16)

**`watchbill land` runs the system's gate on the merged result and undoes a red merge** (exit 4
with the log path; `--no-gate` skips it, say why in `--message`). Two landings in two days went red
with the gate left to the lander's discipline (1033c33, 7e6592a). The architect skill adds: only a
seat of the system lands on it; another system's architect sends a REQUEST or asks the human to
launch this one. Was: land merged and trusted the lander to have run the suites.

## 0.4.4 (2026-10-16)

**A crew sub-agent is stopped when its report is filed** (the human, 2026-10-16: "verification is
done and an agent has no questions. Can it close down those sub agents automatically?"): the
spawner runs `TaskStop <name>` in the same turn; idle crew held the session's exit open and told
the human nothing. Delegation §6, `crew.md`, architect §5.4. Landed by the ptouch system's
architect at the human's request (7e6592a); the landing carried the human's name into a public
skill and no CHANGELOG line, fixed forward in 3337897 (the installed 0.4.4 label covers the red
tree; 0.4.5 is the first install with the fix).

## 0.4.3 (2026-10-15)

**`watchbill status` finds the cycle-closed event past its 60-commit window, manifests written as
`.md` up to three folders deep (`dev-docs/runs/steward/manifest.md`), and decisions written as
`- **OPEN · title**` bullets, and reports open cycles from the cycle-closed events rather than
folder-name order** (reported by a sibling architect's cold verifier, 2026-10-15; was: a
busy day made status report a closed cycle as open, "no run manifest found" beside an existing
manifest, and "0 open" beside four open bullets). The watchbill skill now names the two decision
line shapes that count.

## 0.4.2 (2026-10-15)

**Shelves have a return trip, and monitoring has its own glyph** (the human, 2026-10-15: "when agents
actually have real work to do and they spawn other agents, they should hop out of whatever monitoring
… or waiting workspace they're in and go into their own workspaces and then as they wind down they can
go tuck themselves back away"; "glyphs are good … make sure that they are distinct and that they mean
something"). `herdr-lifecycle shelve monitoring|waiting` moves a session's pane to the shelf (found by
label or created), labels it glyph-first and records its home workspace; `unshelve` brings it back,
recreating the home workspace when it closed; `spawn` unshelves first; `shelve` refuses while child
`claude` processes run. New glyph `📡` = alive on a shelf, acts itself when its condition fires;
`👁` stays the parked architect in its own workspace; `⏳` stays "someone else moves next". Was: a
hand-run `herdr pane move` recipe that wrote a bare label, no monitoring glyph, no way back.

**The configuration survives a plugin reinstall** (the human, 2026-10-15: "how to do that better so it
doesn't get blown out again"; the path is the architect's choice). `watchbill_config` reads
`~/.claude/watchbill.json` (`$CLAUDE_CONFIG_DIR/watchbill.json`; `$WATCHBILL_CONFIG_FILE` overrides)
after the settings entry and before the default; `watchbill config --write-file` fills it from the
resolved values; `--explain` names it; the session context says when nothing at all is configured.
Was: `pluginConfigs` in `settings.json` only, which a marketplace re-registration emptied that day.

**The editor fields the human's decisions, not only their marks** (`collaborative-drafting` rule
6; was: `watch` woke on new marks only, so an accept or reject of the editor's card went
unnoticed until the next mark). From obsidian-track-changes-agent 0.1.6 `watch` also exits 0 when
the human accepts or rejects an agent's card ("your decision: …"; JSON `"decided": true`). The
editor notes each decision, runs `tidy` once a `block` is fully resolved, and never proposes a
rejected change again unless asked. The watchers table's editor row says so.

## 0.4.1 (2026-10-15)

**The architect is pinned to Fable high** (was Opus high). The seat that changes a system's rules
gets the most capable model; a plan that cannot afford it launches the seat with `--model opus`,
recorded in the system's README roster, as the steward is launched with `--model opus` where
judgement is needed. Every other seat and crew type keeps its pin. The guard is unchanged: a
`forbidden_models` entry still refuses that model everywhere.

**`forbidden_models` is per role.** A plain entry (`fable`) forbids a model for every role; an entry
`<role>: <models>` (`architect: none`, `steward: fable haiku`) is that role's own list and replaces
the every-role entries for it. The role checked is the one being launched: `spawn --seat <kind>`,
`claude --agent watchbill:<role>`, an Agent call's watchbill `subagent_type`; a launch that names no
role (a generic Agent call, a bare `claude`, `ANTHROPIC_MODEL`) gets the every-role list, so a seat
allowed a model does not pass it to its delegates. Existing plain lists mean what they did.

**The drafting tool is the `obsidian-track-changes-agent` plugin's, no longer bundled.** `bin/criticmarkup.py` is gone;
`drafting_tool` defaults to the command `obsidian-track-changes-agent` on PATH (that plugin provides it; `obsidian-track-changes-agent
install-links` links it), and still accepts a path. `watchbill status` and `check-note` report a missing
tool by name. The hold switch honours that tool's names too (`.track-changes-hold`,
`track-changes-hold.md`), so one hold stops both. The protocol (editor, checker, `collaborative-drafting`)
stays here. `install-links` reads the plugins file under `$CLAUDE_CONFIG_DIR` (it read `~/.claude` only).

**A seat blocked at startup is recorded, not lost.** `spawn --seat` moves the new tab to its slot
before starting the agent, so a folder-trust dialog can no longer leave it last; when `herdr agent
start` answers `agent_not_ready`, the spawn row is written with `startup: blocked` and the output
names the next step (the human answers the dialog; the launcher sends the launch prompt by
SendMessage; nothing retries the spawn). Before, the spawn died there with no row and no slot.
**`relieve` moves the origin's tab to the historian slot** (after every seat tab), since relief is
when the origin becomes a historian; `handoff` only relabels it, the origin owning the seat until
then. The receiver's output says where the tab went (`origin_tab`).

## 0.4.0 (2026-10-15)

**The rules seat is the Playbook Architect.** "Builder" read as the seat that writes code, which
is the workers' job. The set of rules a system runs on is its **playbook** (schema, code, skills,
briefs, README); the seat that changes it is the Playbook Architect, short form the architect.
Its task and standing leads are **rules leads**. Steward, run lead, standing, advisor, editor and
every crew type keep their names; so do the `Watchbill-*` trailers and `build/*` branches.

| Was | Now |
|---|---|
| seat kind `builder`, agent `watchbill:builder`, skill `watchbill:builder` | `architect`, `watchbill:architect`, `watchbill:architect` |
| name `<subject>-builder`, tab `_ SUBJECT BUILDER` | `<subject>-architect`, `_ SUBJECT ARCHITECT` |
| seat kind `build`, agent `watchbill:build-lead`, name `<subject>-build-<task>`, tab `SUBJECT BUILD · task` | `rules`, `watchbill:rules-lead`, `<subject>-rules-<task>`, `SUBJECT RULES · task` |
| `WATCHBILL_SEAT=builder` / `build` | `architect` / `rules` |

**Read old, write new.** Nothing written from 0.4.0 uses the old names; everything that reads
still accepts them, so ledger rows, rosters, owners files and live tabs from 0.3 keep working:
- `herdr-lifecycle spawn --seat builder|build` and `handoff --seat builder|build` mean architect
  and rules; roster seat text "Builder", "Build lead" and agent types `watchbill:builder` /
  `watchbill:build-lead` resolve the same way.
- Names `<subject>-builder(-hoN)` and `<subject>-build-<task>` map to the new kinds (tab order,
  lead mark, ownership). `watchbill restore` respawns a 0.3 roster row under its old name, so a
  live address never changes.
- Ledger rows with `"seat": "builder"` or `"build"` read as architect or rules (tab slot,
  historian-check, relieve, the session primer). Ledger rows are never rewritten.
- owners.yaml keys `builder`, `build` and `build-lead` still name the architect and rules leads
  (ownership hook, session primer, `watchbill rules-sha`), and a session started before 0.4.0
  (`WATCHBILL_SEAT=builder`) still owns an `architect` key.

## 0.3.2 (2026-10-14)

**Configuration and publishing**
- Everything specific to one person moved out of the skills and agents into plugin options and
  one private overlay file. Skills say "the human" and "a forbidden model"; the resolved values
  arrive in each session's context at start (`watchbill config`, SessionStart hook). An unset
  option is never shown as literal template text.
- No model is forbidden by default (`forbidden_models`); the guard that denied one fixed model
  became a model guard that reads the option.
- The Track Changes tool (`criticmarkup.py`) is bundled in `bin/`; the machine headroom check
  runs only when `headroom_command` is set.
- Decision provenance (dates, question numbers, review-theme tags) left the skills; it lives
  here and in the source repository's decision records.
- MIT licence; author line without an email address.
- The plugin lives in its own folder of the source repository, so installs carry no design
  documents; live tools point at the installed copy (`watchbill install-links`).

**Rules**
- **Communication is its own layer.** A system's brief names the channels the human decides in;
  every decision is recorded where its item lives plus one line in the system's decisions file
  (`dev-docs/decisions.md`), which `watchbill status` reads with Track Changes awareness.
  Approvals are single-use and bound to the exact change: `watchbill land --approved` writes
  `Watchbill-Approved:` and refuses a spent approval; a REQUEST cites where its approval is
  recorded and the receiver checks it there.
- **Seat identity at start.** `spawn --seat` sets `WATCHBILL_SEAT`; the session context names the
  seat, its brief and its owned paths, at start and after compaction. Owners files may key by
  seat kind or agent name. Seats run as their plugin agents.
- **The steward runs in the primary checkout; the builder lands between its items** with
  `watchbill land` (merge `--no-ff`, `landed` trailers), and stamps items with `watchbill
  rules-sha`.
- **Relief cannot deadlock.** Both waits have a deadline (`relief_deadline_minutes`);
  `relief-check` lets the receiver take over when the origin is gone, and marks `?` for the human.
- **Edits from other devices.** `watchbill check-note` checks a note's structure after an outside
  change; the human's hold file stops every writer while it exists, and only the human removes it.
- **Cost band.** A seat offers a handoff at about 400K tokens (`handoff_offer_tokens`); 85 % stays
  the hard line.
- Session skills bundled from the author's global set: handoff-session, historian,
  multi-agent-routing, monitoring-mode, herdr-workspace-placement, role-relaunch, infra-handoff,
  lead-and-crew.
- Evals: two cases whose prompt names no skill; cases pin configuration with
  `EVAL_WATCHBILL_<KEY>`.

## 0.2.2 (2026-10-14)
- Paths under the plugin folder; `install-links` replaces links into the working tree.

## 0.2.1 (2026-10-13)
- `watchbill status` says "unknown: <source>" instead of "nobody" when a source is missing.
- `restore` brings seats back as seats (brief, first prompt, agent, workspace) and handles a live
  seat stopped at a usage limit.
- The commit-msg check joins trailer paragraphs and requires an event on landings; the model
  guard reads a command as the shell does.
- No acks or pauses anywhere: the builder's announcements are FYI, the steward adopts a new rules
  SHA between items after its check.
- `✓` tabs and advisors leave by themselves on their done signal.

## 0.2.0 (2026-10-13)
Decided after the first design review:
- Build events are commit trailers (`Watchbill-Event`), replacing a change ledger; the builder
  works in a worktree and lands by merge.
- Seat lifetime is situational: each brief says resume or fresh.
- Two-party relief (`handoff`, then `relieve`); `watchbill restore` for recovery.
- Away mode: no pings except due needs-human items; no new build cycles.
- Precedence: inside a watchbill system the plugin wins over other skills that disagree.
- Seats are classed by what they may write (rules, work, nothing).
- One plugin agent per seat and crew sub-type, models pinned; an ownership warning hook.
- Launcher of record: `launched_by` fixed, `accountable` moves on handoff and promotion.
- Silence is never consent.
- `?` marks a seat stopped on the human; `👁` a parked builder watching.
- A seat closes the leads it spawned; successors and historians end themselves.
- No scheduled fallback while no scheduler is configured.

## 0.1.1 (2026-10-13)
- The delegation layer: presets over delegation properties, authority in the brief, the human's
  interventions, invariants, closing.
- First design review's minor fixes.

## 0.1.0 (2026-10-13)
- First plugin: builder, steward, paper-trails, watchers, collaborative-drafting and the
  `watchbill` map; `herdr-lifecycle`.
