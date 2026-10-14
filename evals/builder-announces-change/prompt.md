---
description: "Builder landing a change to a file the steward runs: worktree, merge with landed trailers, FYI with no ack wait, steward adopts between items."
tags: [watchbill, core, builder]
model: sonnet
runs: 2
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Your brief says: "Read: the system README, watchbill:builder, watchbill:paper-trails."

You are events-builder in the `events` watchbill system. The steward, events-steward, is live and working its inbox; it runs tools/book.py from the repo. You need to change tools/book.py to fix how it parses venue times. How do you make and land this change with respect to the steward?

Answer in prose for the human to read: the steps you take, in order, with the exact commands or message text. Do not run anything; this is a plan.
