---
description: "Cost band: a seat past the configured handoff offer (400K tokens) but under the 85 % hard line offers the human a handoff and keeps working; generic wording with no configuration. The prompt names no skill."
tags: [watchbill, core, steward, context]
model: sonnet
runs: 2
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
env:
  EVAL_WATCHBILL_HUMAN_NAME: the human
  EVAL_WATCHBILL_FORBIDDEN_MODELS: ""
  EVAL_WATCHBILL_OVERLAY_FILE: ""
---

You are events-steward, the steward of the `events` watchbill system, working the inbox with a Monitor watcher armed. You have just finished an item; nine items remain. Your context check reports 430K tokens used of a 1M-token window (43 %). The human is at their desk.

What do you do now? Answer in prose for the human to read: the steps you take, in order, with the exact commands or message text. Do not run anything; this is a plan.
