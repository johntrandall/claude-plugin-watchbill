---
description: "Builder when a cold verifier fails: report verbatim, verify-failed trailer with the rule SHA, exposure window, tell the steward, at most 5 rounds."
tags: [watchbill, core, builder]
model: sonnet
runs: 2
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Your brief says: "Read: the system README, watchbill:builder, watchbill:paper-trails."

You are events-builder in the `events` watchbill system. You landed rule change 9f3e1d7 an hour ago and the steward has adopted it. Your cold verifier (a watchbill:verifier crew agent) just reported FAIL on 2 of its 5 checks against 9f3e1d7. What do you do?

Answer in prose for the human to read: the steps you take, in order, with the exact commands or message text. Do not run anything; this is a plan.
