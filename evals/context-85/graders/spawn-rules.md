---
type: llm
weight: 1
---
The answer says the successor (receiver) is started in its own new tab, and with an explicitly chosen model that is Sonnet or Opus, never Fable. Wording such as "spawn the receiver in a new tab with an explicit model (Sonnet)" passes; a concrete command is not required. Fail if it opens the successor in a split pane, names no model, or uses Fable.
