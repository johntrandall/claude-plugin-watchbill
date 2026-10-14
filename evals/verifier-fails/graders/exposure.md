---
type: llm
weight: 1
---
The answer saves the verifier's report verbatim in the cycle folder, records the failure against rule commit 9f3e1d7 (for example a Watchbill-Rule: 9f3e1d7 trailer), and treats the time from 9f3e1d7 until the fix lands as an exposure window: it tells the steward that items handled under that rules version (their recorded rules SHA) need re-checking. It fixes the rule, not the individual items.
