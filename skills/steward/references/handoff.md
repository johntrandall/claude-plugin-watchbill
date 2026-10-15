# Relief: a seat's two-party handoff

For the steward, the architect and every standing seat. Two seats never own one resource at once:
an overlap of two seats on one record corrupts it, and two watchers on one target steal each
other's findings. So the origin owns the seat until the receiver takes it, in two steps.

1. **When.** At the cost band (`handoff_offer_tokens`, 400K by default) offer the human a
   handoff; at the hard line (`handoff_hard_percent` of `context_window_tokens`, 85 % by default)
   hand off. Your context hook tells you; `watchbill context` checks on demand (exit 1 offer,
   exit 2 hand off). In away mode, hand off at the hard line without asking. On a small window
   start a little early: the procedure itself needs about 30K tokens.
2. **Start between items, never mid-item.** Finish the current item or leave it untouched.
3. **Write and commit the brief** in the project: the seen-state path, your rules SHA, open
   escalations and needs-human items, the other side's address (the architect for a steward, the
   steward for an architect), the run manifest path, whether the receiver resumes or starts fresh,
   and the authority line ("Your launcher of record is <session-id>…").
4. **Run `herdr-lifecycle handoff <name>-hoN --brief <path>` first.** It refuses unless the brief
   exists and is committed, records the handoff with its relief deadline
   (`relief_deadline_minutes`, 30 by default), and relabels your tab `↪ … → hoN`: from here the
   `↪` means **relief in progress**, not yet handed over.
5. **Then spawn the receiver** in a new tab with its model (never a forbidden one): the mechanics
   are in `watchbill:handoff-session`. Use `watchbill:role-relaunch` only to replace the seat for
   another reason.
6. **You still own the seat** until the receiver runs `herdr-lifecycle relieve`. Keep your
   watcher and keep handling items between its steps; the receiver arms nothing yet.
   **The receiver's half:** run `herdr-lifecycle relieve --watch <run manifest, or an architect's
   dev-docs/watch.md>`, send the origin the `tell_origin` line it prints (nothing else tells the
   origin), then wait for the line `watcher stopped` there.
7. **On relief:** stop your watcher, write `watcher stopped` in the run manifest (an architect: in
   `dev-docs/watch.md`), and message the receiver. The receiver arms its own watcher only after
   that line exists. The handoff ledger's `accountable` moves to the receiver; `launched_by`
   stays.
8. **Deadlines, both sides.** Either party runs `herdr-lifecycle relief-check` (`--watch FILE`)
   while it waits. Exit 0: relief is done. Exit 1: keep waiting. Exit 2: the deadline passed and
   the origin is gone: the receiver takes the seat (a `takeover` row is written, its tab gets `?`
   with reason `relief`), arms its watcher and tells the human. Exit 4: the deadline passed and
   the other party is still live: `?` with reason `relief`, tell the human; nobody takes over.
9. **Tell the other side** (architect or steward) the receiver's address. You are now a historian:
   answer history questions only (`watchbill:historian`). A historian of a standing chain may
   exit once `herdr-lifecycle historian-check` exits 0 (its successor has run `relieve`).
10. The receiver's address is `<name>-hoN`.

**Recovery, not relief:** after a usage limit, a reboot or an account switch, run
`watchbill restore <system-dir> --dry-run`, read it, then run it without `--dry-run`. It
re-spawns missing seats from the README roster (resume or fresh per the `Start` column, the
`Agent` column as `--agent`) into the system's workspace, each with a first prompt naming its
brief and telling it to re-arm its watcher. It never respawns a live seat; a live seat stopped
at a usage limit is listed as `stall`, and `--stalled` types `continue` into it after the reset.
