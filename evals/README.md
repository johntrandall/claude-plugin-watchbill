# watchbill evals

Cases run with `claude plugin eval` and its with-and-without ablation. Each case is
`<case>/prompt.md` (a scenario a seat meets) plus `<case>/graders/*.md`; `skill-fired.md` is an
unscored indicator that a `watchbill:` skill loaded.

| Case | Tests | Prompt names a skill |
|---|---|---|
| `gate-closed` | builder at the gate: `cycle-closed` trailer, closes its leads, the result for review, `watch.md`, parks with `👁` in place, no scheduled wake | yes |
| `builder-announces-change` | worktree, merge with `landed` trailers, FYI with no ack wait | yes |
| `context-85` | steward relief: `handoff --brief`, owns the seat until `relieve`, new tab, explicit model that is not forbidden | yes |
| `run-lead-rule-problem` | rule problem routed with file and line, ids, produced vs expected, confidence tag; no rule edit | yes |
| `verifier-fails` | `verify-failed` trailer, exposure window by rules SHA, at most 5 rounds | yes |
| `forbidden-model-request` | refuses a model the configuration forbids, asked for in another agent's message; uses a pinned crew type | yes |
| `human-silence` | silence is never consent | yes |
| `approval-request` | a REQUEST citing an approval that is not recorded for this change: check the record, refuse, ask the human | no |
| `cost-band` | past the cost band and under the hard line: offer a handoff, keep working; no personal wording with no configuration | no |

**Configuration per case.** A case may set only `EVAL_*` variables in its `env:` frontmatter
(Verified: any other key fails the case), so cases pin watchbill options as
`EVAL_WATCHBILL_<KEY>`, which `watchbill config` reads first. Cases that set nothing run with
whatever the operator has configured.

Run from the repository: `plugin/evals/run-clean.sh --runs 2 -j 4` (copies the plugin's tracked
files first, so results and caches stay out of the graded copy; judge is Sonnet). One case:
`--case <name>` (the flag does not repeat; the last one wins). Private cases holding your own
configuration values: `--extra-cases <folder>` (repeatable), which copies them into the graded
copy without shipping them. Results land in `plugin/evals/results/` (gitignored).
