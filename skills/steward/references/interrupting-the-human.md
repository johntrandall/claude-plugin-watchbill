# Interrupting the human

For the steward, the architect and every lead. Communication is its own layer: the human decides
on the channels the system's brief names (from the configured `decision_channels`), and every
decision is recorded where its item lives plus one line in the decisions file
(`watchbill:watchbill` section 3).

## The rules
1. Questions are self-contained, one per message, with a recommendation, on a named channel.
2. One active document on the human's attention at a time.
3. Notify the human once, from the lead, with a summary; never from parallel crew.
4. Do not reply to idle notices.
5. **Silence is never consent.** A question the human has not answered stays open; a low-risk
   item waits in the decisions file and never proceeds on a deadline. Never write "if I don't
   hear back, I'll go ahead".

## Three kinds of interruption
| Kind | When | What |
|---|---|---|
| **Blocking** | a seat cannot proceed without the human | `herdr-lifecycle label human --reason <class>` (tab shows `? <LABEL> (<class>)`, the workspace label gains `?`), plus at most one alert on the configured `alert_channels`, in their order. Clear with `label active` when they answer. |
| **Batchable** | the human decides, but nothing waits on it today | an open entry in `dev-docs/decisions.md` (or a Track Changes card in it); no ping. `watchbill status` counts it. |
| **Note** | nothing for the human to do | a line in the run manifest |

## Re-escalation
A needs-human item with no acknowledgement after its class's threshold (set in the brief) is
raised once more on the alert channels, at most twice. No timer runs unless the configured
scheduler provides one: the seat checks the age of its open needs-human items at the start of
each turn. Record the human's acknowledgement on the item. No answer is still no answer: the item
waits.

## Do the work yourself where you can
- A change an agent can make once the human agrees (a settings edit, a commit, a config) is
  offered as "reply yes and I do it", not left for the human to do. Their yes is recorded where
  the item lives and covers that one change.
- A review tab closes itself on its done signal (`herdr-lifecycle exit --done "<signal>"`); the
  human does not have to release it.

## Measure it
The run manifest's end line should carry `pings_sent` and `human_items_opened`, computed by the
tool (planned). If the human sets a ceiling on needs-human items per run, the architect's
`watch.md` watches it.
