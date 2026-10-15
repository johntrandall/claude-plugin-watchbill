---
name: lead-and-crew
type: procedure
description: "How a lead runs a multi-step change with a crew: a task list with dependencies, phases of parallel crew in worktrees (watchbill crew sub-agents, or herdr worktree workers of any agent kind), merging and verifying between phases, cleaning up worktrees, a final independent verifier, and the recovery cases. Auto-invoke when a lead or architect takes a change with five or more tasks and internal dependencies, or is asked to orchestrate a sweep, migration or refactor."
tags: [agents, orchestration, worktrees, crew, watchbill]
---
> Where a global skill disagrees with the watchbill plugin on a decided point, the plugin's rules win (list: `watchbill:watchbill`, top).


# Lead and crew

A lead (rules or run, `watchbill:watchbill`) that owns a change of five or more tasks with
dependencies runs it in phases: **task list → parallel crew per phase → merge and verify → next
phase → independent verifier.** Fewer than three tasks: do them inline. All independent with no
dependencies: one wave of crew in a single message. Whether to delegate at all, and the launch
rules (model, authority line, lineage), are `watchbill:delegation`.

## 1. Task list and phases
Create one task per unit (`TaskCreate`). Each description is self-contained, because the crew
member works from it cold: required reading (full paths), what to build, verification commands,
the commit command, what to report. Encode dependencies with `addBlockedBy`; phases fall at the
dependency edges. If the work touches a schema-validated artifact, confirm which schema live code
actually validates before dispatching anyone against it.

## 2. Dispatch a phase
Every crew brief carries: the task id; required reading; verification to run before committing;
`git commit -m '<subject>' -m 'REPORT: <done, verified>' -- <paths>` with your setup's commit
trailers; and "commit on your branch and do nothing else; the lead merges".

**Default: watchbill crew sub-agents.** Agent tool, `subagent_type: watchbill:worker` (model
pinned) or a generic agent with `model:` passed, never a forbidden model, `isolation: "worktree"`
for anything that writes. Send a phase's crew in one message so they run at once. Each result
names its worktree (`.claude/worktrees/agent-<id>`) and branch (`worktree-agent-<id>`).

**herdr worktree workers**, when the worker should be another agent kind (`codex`, `gemini`, …)
or the human wants to watch each one:
```bash
REPO=$(git rev-parse --show-toplevel)
EXCLUDE="$(git rev-parse --git-common-dir)/info/exclude"
grep -qx '.worktrees/' "$EXCLUDE" || echo '.worktrees/' >> "$EXCLUDE"
BASE=$(git rev-parse HEAD)            # once per phase, after the previous merge
herdr worktree create --cwd "$REPO" --branch task-<id> --base "$BASE" \
  --path "$REPO/.worktrees/task-<id>" --label task-<id> --no-focus
# keep result.workspace.workspace_id and result.root_pane.pane_id from this reply
herdr agent start task-<id> --kind <kind> --pane <pane_id> --timeout 60000 -- <args, with the model> '<brief>'
```
- Address a worker by **pane id** from the create reply: a start that times out does not keep the
  name. Never find the pane by listing afterwards.
- Start workers in their default permission mode; never pass bypass flags. A worker that needs
  approval shows `blocked`: read its pane and take it to the human. Folder trust and sign-in
  screens are the human's call.
- A worker whose sandbox cannot write the main repo's `.git` stops at an approval for its
  commit. Never answer an approval prompt by typing into the worker's pane: take it to the human
  with the exact command shown, or commit the worker's checked work yourself after inspecting it.
- **Done is a commit, then idle.** Poll the branch (`git rev-list --count "$BASE"..task-<id>`),
  check for `blocked` while waiting, and re-read the branch tip once the worker is idle: a worker
  may amend after its first commit appears. Name each worker (kind, pane, session id if any) in the
  merge commit; that is the attribution record.

## 3. Merge, then verify, before the next phase
```bash
git merge --no-ff task-X task-Y -m "merge: phase N — <summary>"
```
One octopus merge when the branches touch different files; otherwise merge one at a time. If
upstream moved, merge it in; never rebase across a phase merge (it rewrites the crew's commits and
strands their branches). Then verify independently of the self-reports: files exist, `grep` for
the new names, run the suites and the phase's success criteria. A broken phase poisons the next:
stop and fix.

**Clean up** only what this orchestration created, after the merge is verified:
- herdr worker: `git -C .worktrees/task-<id> status --short` empty, then
  `herdr worktree remove --workspace <id>` (it also closes that workspace and ends its worker) and
  `git branch -d task-<id>`.
- Sub-agent: `git worktree remove .claude/worktrees/agent-<id>`, then
  `git branch -d worktree-agent-<id>`.
- **Never `--force` or `-D`.** A refusal is the safety check: dirty means uncommitted work
  (inspect it, commit or consciously discard, `trash` generated junk); "not fully merged" means
  those commits are missing from your merge.

## 4. Final verifier
The last task is a fresh verifier (`watchbill:verifier`) on the merged branch, not in a worktree,
with no context from the orchestration: it re-runs every suite, smoke-tests, re-reads the documents
that drove the work, and reports discrepancies. Close what it finds before reporting done.

## 5. Recovery and traps
- **Crew finished but did not commit:** `git -C <worktree> log --oneline -5` and `status --short`;
  for a herdr worker read its pane first (it may be waiting on a question). Commit on its behalf
  only after inspecting.
- **Worktrees see a stale tree:** a failure that reproduces only in the worktree may be its
  snapshot. Check on the merged branch before fixing.
- **Sequencing is the human's:** a denied out-of-order action means a missing prerequisite; find
  it, do not argue with the denial.
- **Stage by explicit path only**, never `git add -A` or `.`: other sessions may have uncommitted
  work in the tree.
- **Teammates as crew:** some versions do not exit on a shutdown request alone. At your exit choose
  "Exit and stop tasks", never "Move to background", unless the team must outlive you.
- **More work than fits:** hand off with a long, thorough briefing (`watchbill:handoff-session`):
  reading list, caveats, prioritised open loops.
