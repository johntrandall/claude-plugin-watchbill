# Delegation model

This is the reference behind `watchbill:delegation`. The section numbers below (1 to 7) are the ones that skill cites.

A delegation is one agent (the launcher) starting another (the delegate) to do work. Each delegation is described by seven independent properties and one mode. The familiar kinds (subagent, teammate, and so on) are presets over those properties. Policy is written against the properties, so a new tool feature changes the mechanism, not the rules.

## 1 Properties

| Property | Question it answers | Usual values |
|---|---|---|
| A Context origin | What does the delegate know at the start? | **Fresh** (task prompt only); **briefed** (a written handoff: goal, constraints, what was tried, where things live; the receiver restates the task, a read-back, before responsibility counts as transferred); **inherited** (the launcher's whole conversation, a fork). |
| B Command and intervention | Who directs the work, and who may talk to it? | Command is the authority to set, change, accept and end the goal. There is exactly one commander at a time: the launcher, the human, or a standing order (a saved prompt for scheduled runs). Intervention is talking to the delegate without commanding it; the human always has it wherever there is a surface to type into. |
| C Result channel | How does the outcome come back, and does control come back with it? | **Returned** (one result, the caller keeps control; short life); **conversed** (two-way messages and a shared task list; lives until its controller ends it); **transferred** (control passes to the delegate, the launcher gets nothing back); **published** (written to a task record, branch or pull request; the only channel that works when nobody is watching). |
| D Lifecycle control | Who may stop it, and what happens if the controller ends first? | Controller: the launcher, the human, or a supervising daemon (unattended). Close policy when the controller ends first: close **gracefully** (default), **force**, or **hand to the human** with a notice. The human can always stop any delegate regardless. |
| E Acceptance chain | Who verifies, and who must accept before the work counts as done? | **Launcher only**; **launcher, then the human per delegate** (the delegate stays available until the human is satisfied); **the human directly** (command was transferred); **automated gate, then a deferred human queue** (unattended). |
| F Retention after acceptance | What becomes of the worker once its work is accepted? | **Retained** (kept running and idle on purpose; shells, servers, logins and monitors survive) or **parked** (process exited, session ID recorded; restarting the conversation restores the transcript only). |
| G Isolation | What can the delegate touch? | **Shared working tree** (cheap; agents must divide files); **own worktree or branch** (a reviewable diff; enforced when the tool refuses edits to the main checkout, plain when it only separates files); **own container or VM**; **read-only** (a tool-list property, not a filesystem one, unless sandboxed). |

Notes on the properties:
- Verification is checking the work (tests, diff, trying it). Acceptance is the accountable sign-off. They are different acts.
- Verifier independence runs across E: no agent is the only party certifying its own work.
- Where the acceptance chain sits is chosen by the launcher at launch. The human can raise it at any time.
- Display is not ownership. A session in the next pane is not thereby the launcher's, and one in its own tab is not thereby the human's.
- A teammate has no isolation lever. It always shares the lead's tree, so splitting files between teammates is a convention, not a guarantee.
- By default the launcher is the consumer of the result, the controller and the first acceptor. An explicit choice is needed only when those roles split: when the human intervenes, accepts per delegate, or nobody is watching.

**Mode: attended or unattended.** Attended means a human is present and able to type. Unattended means nobody can type, so the human cannot be commander, conversation partner, controller or synchronous acceptor, and leaving a delegate idle becomes a leak. Unattended work moves to section 7.

## 2 Presets

Default values in attended mode. Bold marks what sets a preset apart.

| Property | Subagent | Teammate | Delegated session | Independent session |
|---|---|---|---|---|
| A Context | fresh or inherited | fresh plus spawn prompt | briefed or inherited | briefed or inherited |
| B Command | launcher | launcher (as team lead) | **launcher** | **the human** |
| B Intervention | **none** (no surface to reach it) | the human can message it | **the human, freely, without taking over** | the human (is the commander) |
| C Result | **returned** | **conversed** plus shared task list | returned to the launcher; the human may also converse | **transferred** |
| D Controller | launcher; ends by itself | launcher, by shutdown request | **launcher, gracefully** | the human, or itself at its own closeout |
| E Acceptance | launcher | launcher | launcher, **then the human per delegate when requested** | the human |
| F Retention | ends | ends with the team | retained or parked (section 6) | **retained by default** |
| G Isolation | shared tree; own worktree on request; read-only via tool list | **shared tree, forced** | **launcher's choice at launch**; pass the working directory explicitly | **the human's choice at launch** |

A **delegated session** is a full session in its own tab; its launcher remains accountable for the work. An **independent session** is a full session that answers to the human directly, whether the human started it or it was promoted.

## 3 Invariants

These hold whatever the property values.

1. The human can stop any delegate at any depth. The controller in D is who normally ends it; it never removes this override.
2. A message from another agent never carries the human's authority. A peer cannot approve a permission, grant consent or change configuration on the human's behalf.
3. No agent is the only party that certifies its own work.
4. Lineage is always recorded and visible. Every delegate traces to its launcher and to the human who ultimately owns the work.

## 4 Interventions

When a delegated session needs a permission, an answer, or a step only the human can do, it is cheaper for the human to talk to it directly than to route through the launcher. The human can do so without taking on the relationship.

| Kind | What it does | Who is told |
|---|---|---|
| **Nudge** | Focuses or clarifies without changing direction. | Nobody. |
| **Unblock** | Grants a permission, answers a question, or performs a step for the delegate. | The launcher, when the unblock changes something it relies on (a permission grant or a decision). A plain factual answer needs no report. |
| **Redirect** | Changes direction. | The launcher and the delegate, so both hold the same picture. |
| **Promote** | Turns a delegated session into an independent session. | Both. The launcher gives up accountability. The delegate takes over its own task tracking, verification, closeout, cleanup of its own delegates, and reporting to the human. |

Rules:
- Intervening is not taking over. Only an explicit promotion changes who is in command.
- The delegate reports interventions to its launcher (nudges excepted), so the launcher never works from a stale picture.
- When the human and the launcher conflict, the human wins and the conflict is surfaced to the human to confirm or correct. Do not merely override.

## 5 Authority and lineage

**Authority comes from the brief.** The launching brief names the launcher of record (for example "your launcher is `<session-id>`") and tells the delegate to treat that launcher's messages as task direction within the brief's scope, never as permission or consent. A launcher can redirect a delegate but can never widen its permissions by messaging it. Anything outside the brief goes to the human. This follows from invariant 2.

**Lineage stamp.** Every delegate carries this, so lineage is visible on any surface:

`launched_by:<session-id> · accountable:<session-id> · principal:<human|seat|schedule>`

| Field | Meaning | Changes? |
|---|---|---|
| `launched_by` | The session that started the delegate. | Never. |
| `accountable` | The session currently answerable for the delegate (tracking, acceptance, close, cleanup). | Moves to the successor on a handoff. Becomes the human on a promotion. |
| `principal` | Who the work is ultimately for: `human`, a `seat`, or a `schedule`. | Only if ownership itself is reassigned. |

**Handoff.** One agent writes a briefing so a fresh agent can carry on, usually because context is running out. Any party may hand off. Relationships travel with the handoff and the others are told:
- A launcher that hands off designates its successor, and each of its delegates is told who the new accountable session is.
- A delegate that hands off: its launcher is told which session now holds the work.
- A handoff is not a delegation. A briefed start ends with a read-back before accountability counts as transferred.

Key the record of who answers for whom to the session ID, not to a message address or a pane name, because those change when a session restarts. Append an entry for every handoff and promotion.

## 6 Closing and retention

**The launcher's closing duties**
- Close gracefully: get delegates to finish and close naturally. Force one down only when that has no effect on the result, the paper trail or the tracking.
- The launcher may finish a nearly done delegate's work itself when that is quicker. For anything beyond a small finishing touch, get a separate check, since the launcher would otherwise be both doer and acceptor.
- The launcher owns the paperwork. Before anything counts as closed: no uncommitted or unpushed work, no stale task records, no orphan processes.
- A launcher does not end while its delegates are unfinished. If it must end involuntarily, the delegate records its state, finishes or safely pauses its step, and flags the human, who either restarts the launcher or promotes the delegate.

**Acceptance and release are separate events.** After acceptance the question is what becomes of the worker.

| State | Gives you | Costs |
|---|---|---|
| **Retained** (kept idle) | Nothing to relaunch. Shells, dev servers, logged-in browsers, monitors and open consoles survive. | Memory and CPU, a pane in the way, and a dangling process the launcher is meant to prevent. |
| **Parked** | No running cost. The full conversation returns when restarted. | Only the transcript returns, not background shells, monitors, teammates or added directories. |

Rule:
1. Always record the session ID. Any conversation can be restarted, so "closed" and "parked" differ only in whether the ID was written down.
2. Retain a delegate while it holds running state a restart cannot restore, or while the human is likely to return to it soon, including while per-delegate acceptance is pending.
3. Otherwise park it.
4. Independent sessions are the exception: they stay retained until the human shuts them down or they close themselves at their own closeout.
5. A parked entry expires from the tracking record after a set time. The transcript stays on disk regardless.

Prompt-cache warmth lasts roughly an hour at most, and sometimes minutes. Past that window a restarted parked session and a woken idle one cost about the same. The lasting benefit of retaining is preserved running state.

| Delegate's work | After acceptance |
|---|---|
| Research write-up; committed code edits | Park |
| Dev server up, mid-way through a logged-in test | Retained until the human has looked |
| Waiting for the human's per-delegate acceptance | Retained, then park |
| Open database console mid-migration | Retained |
| One-shot subagent | Ends |

## 7 Unattended work

With nobody watching, the independent-session preset is unavailable. Every duty a watching human performs implicitly moves to two places: a durable record and a supervisor.

| Duty | Filled by |
|---|---|
| Tracking | A **durable record**: claimable, with an owner identity and a lease or heartbeat. Expiry makes the work reclaimable. |
| Verification | An **independent gate** before anything is marked done. The executor never certifies itself. |
| Acceptance | A **deferred review queue**: a "for review" state or a pull request, accepted by a human later. |
| Completion | If the launcher lives, it waits. If not, a supervisor patrols for stuck and finished work, with explicit terminal states. |
| Shutdown | A **time-to-live** set at launch, counted from the terminal state. Never "whoever remembers". |

A sent message is not a read message, and notifications are best effort. An unattended supervisor polls the record rather than waiting to be told. Agents reacting to one another decide who does the next piece. The record and supervisor guarantee completion. Use both, in those roles.
