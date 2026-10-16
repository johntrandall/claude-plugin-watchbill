# Crew sub-types

Crew are sub-agents: fresh context, one step, gone after the report, never a tab. Each sub-type
is a plugin agent that pins its model, effort and tools: pass it as `subagent_type` and the pin
holds.

| Sub-type | Agent | Class | Does | May write | Model, effort | Tools withheld |
|---|---|---|---|---|---|---|
| Worker | `watchbill:worker` | work | one step of real work | its records, through the tools | Sonnet medium | Agent |
| Reader / researcher | `watchbill:reader` | nothing | reads, searches, reports | nothing (by construction: no Bash) | Sonnet medium (no CLAUDE.md) | Agent, Bash, Edit, Write, MultiEdit, NotebookEdit |
| Verifier | `watchbill:verifier` | nothing | checks cold; pass or fail per check | nothing, by brief (keeps Bash for its scripts) | Sonnet high (no CLAUDE.md) | Agent, Edit, Write, MultiEdit, NotebookEdit |
| Backfill | `watchbill:backfill` | work | applies a landed rule change to existing records | records, one commit with `Watchbill-Event: backfilled` | Sonnet medium | Agent |
| Checker / commenter | `watchbill:checker` | nothing (comments) | reviews a draft | comments only, through the drafting tool (by brief; keeps Bash for it) | Sonnet high (no CLAUDE.md) | Agent, Edit, Write, MultiEdit, NotebookEdit |
| Escalation specialist | `watchbill:escalation` | work | one item a Sonnet worker failed | that item | Opus high | Agent |

**Models.** The Agent tool's `model` parameter overrides an agent's pinned model, so do not pass
one to a watchbill crew type unless the brief says why, and never a forbidden model. A generic
`subagent_type` needs `model:` on every call; the model guard denies a forbidden model inside a
watchbill system and reminds you when a generic call names no model.

**No CLAUDE.md** (`omitClaudeMd`) for reader, verifier and checker: they write nothing, a cold
check is colder without the human's global instructions, and it saves tokens on every spawn.
Worker, backfill and escalation keep it: they write records and need the human's safety rules. A
reading job that needs git history or a script goes to a verifier, not a reader.

**Name the sub-type in the brief** anyway, with what it may write: the pin covers model and
tools, not the files.

**Reports.** Crew report to whoever spawned them. The spawner files the report verbatim in the
run or cycle folder; a report is not a trail until filed. **Then the spawner stops the crew
member** (`TaskStop <name>`) in the same turn: a sub-agent that has reported is gone, not idle.
An idle crew member holds the session's exit open and answers no question.

**An empty or missing report** is checked against the files the crew member was told to produce
before it is called a failure.

**Verifier rounds:** at most 5 on one item or change, then ask the human.

**Crew never spawn crew** (the Agent tool is withheld).
