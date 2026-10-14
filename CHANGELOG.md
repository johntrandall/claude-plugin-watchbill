# Changelog

Rules in the skills are stated as rules; this file keeps when each was decided and what it
replaced.

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
