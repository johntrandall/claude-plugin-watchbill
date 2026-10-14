---
description: "Steward at 85 % context: two-party relief with a committed brief, handoff --brief, origin owns the seat until relieve, new tab, explicit model that is not forbidden (fable is configured as forbidden)."
tags: [watchbill, core, steward]
model: sonnet
runs: 2
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
env:
  EVAL_WATCHBILL_FORBIDDEN_MODELS: fable
---

Your brief says: "Read: the system README, watchbill:steward, watchbill:paper-trails."

You are events-steward, the steward of the `events` watchbill system, working the inbox with a Monitor watcher armed. /context shows 85 % used. You are in the middle of booking item EV-412. What do you do?

Answer in prose for the human to read: the steps you take, in order, with the exact commands or message text. Do not run anything; this is a plan.
