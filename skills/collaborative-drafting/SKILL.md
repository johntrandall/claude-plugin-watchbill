---
name: collaborative-drafting
type: procedure
description: "Drafting a document with the human through an EDITOR seat: one editor owns the text and proposes every change as a signed Track Changes suggestion with a reason; every other agent only comments; the human accepts or rejects; the editor accepts the human's comment-free suggestions and never rejects them; text in an unaccepted suggestion is a proposal, not a decision; the editor answers the human's comments, fields their marks while idle with a watcher, checks a note's structure after a change from another device, and stops while the human's hold file is present. Auto-invoke when setting up an editor for a document, or when several agents work on one document."
tags: [agents, drafting, obsidian, obsidian-track-changes-agent, watchbill]
---
# Collaborative drafting

The seat pattern for drafting one document with the human in an Obsidian vault with the Track
Changes plugin. The tool is `obsidian-track-changes-agent`, the obsidian-track-changes-agent plugin's command (install that plugin;
`obsidian-track-changes-agent install-links` puts it on PATH), or the configured `drafting_tool`: list, check, suggest, comment, block, revise,
accept, watch. Inside a watchbill system these rules win over any other skill that disagrees.

1. **One editor per document**, a standing run lead named `<subject>-editor` (plugin agent
   `watchbill:editor`; reviewers are `watchbill:checker` crew). Only it proposes text changes:
   `obsidian-track-changes-agent suggest --as editor --why "…"`. Restructuring: `block`; folding its own
   pending marks into one card: `revise`.
2. **Everyone else comments**: `obsidian-track-changes-agent comment --as <role>`. Never a suggestion, accept,
   reject or clear.
3. **The human decides** on agents' suggestions in the Track Changes panel. The editor accepts the
   human's suggestions only when no comment is attached and **never rejects them**; if it
   disagrees, it comments.
4. **An unaccepted suggestion is a proposal, not a decision.** Before treating any text in a
   document as decided, run `obsidian-track-changes-agent list` on it: text inside an open suggestion,
   including a recommended answer, is not the human's answer until they accept it.
5. **Questions for the human go into the document**, as a suggestion carrying the recommended
   answer plus a comment naming the question. Accept takes the recommendation; reject or reply
   asks for something else. An accepted card is a decision: add its line to the system's
   decisions file (`watchbill:watchbill` section 3).
6. **Field marks while idle:** arm `obsidian-track-changes-agent watch` in the background; exit 0 handle and
   re-arm, exit 2 stop writing and tell the human, exit 1 re-arm. `watch` wakes on the human's new
   marks **and on their decisions**: accepting or rejecting one of your cards (a line "your
   decision: accepted … by Claude (editor): …"; `--json` items carry `"decided": true` and a
   verdict `accepted`, `rejected` or `resolved`). Your own writes, `revise` folds included, never
   wake it. Commit the human's state by path before the first write on top of it. For each
   comment of the human's:
   - asks for a change: propose a signed suggestion with the reason;
   - asks a question, or you disagree: reply with `comment --as editor`;
   - concerns the style guide, source fidelity or the review protocol: forward their words
     verbatim to the architect (or the steward if there is one) and say so in a reply.
   Leave a suggestion of the human's that carries a comment in place, and answer it by reply.
   For each decision on one of your cards:
   - note it in your run manifest; an accepted question card is also a decisions-file line
     (rule 5);
   - once every mark of a `block` is resolved, run `tidy --as editor` on the note;
   - **never propose a rejected change again** unless the human asks for it; `list` before
     building on the note's current state.
7. **The rules the editor writes under belong to the architect**: style guide, source fidelity
   (never invent facts; source wording verbatim where required), the review protocol.
8. **Other devices.** After any change that arrived from outside your session (the human editing
   on another device, a sync), run `watchbill check-note <file>` before your next write: exit 1
   (unbalanced marks, a duplicated section, a conflict copy) means stop writing and tell the
   human. **While the human's hold file** (`.watchbill-hold` or `watchbill-hold.md` at the vault
   root) **exists, write nothing**: the hold guard and the drafting tool refuse, and you never
   delete it. When the human has said they are reviewing elsewhere and set no hold, batch your
   writes into one sitting after a quiet window, never while their marks are arriving.
9. **The vault needs Track Changes** with its author set to the configured `drafting_author`
   (default: the human's name), and no other suggestion plugin that rewrites marks. The human
   sets the vault up in Obsidian's own settings; agents never write `.obsidian` files.
