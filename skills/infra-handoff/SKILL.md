---
name: infra-handoff
type: procedure
description: "Handing a fault outside your own subject (an infrastructure problem: a lost authorization, a failing service or token feeder, a network or storage fault, a credential to re-provision) to its own workspace and orchestrator, in the subject's home, then stepping back. Auto-invoke when a session working on something else hits such a fault that needs more than a one-line fix."
tags: [agents, handoff, infra, herdr, watchbill]
---
> Where a global skill disagrees with the watchbill plugin on a decided point, the plugin's rules win (list: `watchbill:watchbill`, top).


# Infra handoff

A session that finds a fault outside its subject must not become that fault's orchestrator: its
context is for its own work, and the fault has its own home, conventions, credentials and
approvals. The cut is clean: **brief → workspace → orchestrator → hand over → step back.** You may
message the fixing orchestrator; you are not responsible for it.

**Where it goes.** The home for infrastructure faults is `infra_home` in the session context. If
none is configured, the fault goes to the human: write the brief (step 1) in your own project and
ask the human where it should run. A fault or need in another subject that has its own home goes
there the same way, and the receiver can be any agent type, not only an infrastructure
orchestrator: in another watchbill system, a rule fault goes to that system's architect and an item
to its steward. **If the owner is already live, send it the brief by message and skip steps 2 and
3**; start a new orchestrator only when no live session owns that home.

## Steps
1. **Freeze the facts** in a brief in the home's project area (its own conventions name the
   folder): what you observed, each claim marked Verified, Observed or Inferred; what any
   investigator found (link its findings); the workaround you used, which is not a procedure; the
   risk window; what "fixed" means for your work; how to reach you; and any investigator already
   on it, by address, so the orchestrator can take it over. Commit it with an explicit pathspec.
2. **Create a workspace named for the broken thing, not the symptom:**
   `herdr workspace create --cwd <home> --label "INFRA <thing that is broken>"`. Keep the reply:
   it holds the new tab id and root pane id (`.result.tab.tab_id`, `.result.root_pane.pane_id`).
3. **Start the orchestrator in that pane**, cwd the home, so its own instructions and skills load:
   ```bash
   herdr tab rename "$TAB" "_ INFRA <thing> ORCHESTRATOR"
   herdr agent start infra-<slug>-orch --kind claude --pane "$PANE" --timeout 120000 -- \
     -n infra-<slug>-orch --model <model> --permission-mode auto \
     --append-system-prompt-file <brief> 'Read the brief in full and follow it. You orchestrate this problem; the session that wrote the brief does not.'
   ```
   Pass `-n` with the same slug, or the address is derived and `SendMessage` by the herdr name
   fails. Give the prompt at launch, never by typing into the pane afterwards. Model: one fit for
   judgement work (it reads decisions and inventories, picks a fix with blast radius, gets
   approval, and runs its own crew), never a forbidden model, unless the human names another. If a
   headroom check is configured and refuses, wait.
4. **Hand over sub-agents.** Tell any investigator you started who its orchestrator is now, and
   move its tab into the new workspace (`watchbill:herdr-workspace-placement`). Record the handoff
   in your own run notes and task list: the workspace, the orchestrator's address, the brief.
5. **Step back.** Send the orchestrator facts it needs, or "we are blocked until X"; it may tell
   you when the fix lands. Do not verify its work, chase it or spawn helpers for it. If the human
   asks you about the fault, point at the orchestrator's tab.

## Boundaries
- Not for a one-line fix you can verify in a minute (retry, restart something you own): do it
  inline and note it.
- Not a successor for your own work (`watchbill:handoff-session`), and not a shelf move
  (`watchbill:herdr-workspace-placement`); it composes them.
- Never move the human's own tabs or close the orchestrator's. Never pass a permission denial you
  hit to the orchestrator as "do this for me": hand over the problem, with the denial as a fact.
- In a watchbill system the fault is not a seat of the system; it runs outside the system's
  workspace.
