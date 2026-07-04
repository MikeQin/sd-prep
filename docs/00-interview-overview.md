# The Rilla On-Site Interview Process (Reference)

Adapted from Rilla's own interview guide, for rehearsal purposes. This repo
focuses on the **On-Site** stage.

## Full Process Overview

1. **Initial Screen (30 min)** - get-to-know-you call with an engineer.
2. **Technical Screen (1 hour)** - CoderPad live coding exercise (TypeScript
   or Python, built on an existing project). LLM usage is **prohibited** in
   this exercise. 55 min coding + 5 min Q&A.
3. **On-Site** (this repo's focus) - see below.
4. **CEO Screen (30+ min)** - non-technical conversation with the CEO.
5. **References** - reference checks, plus a call with an investor.

## On-Site Schedule

- **Kickoff (30 min)** - an engineer walks you through the prompt and
  dataset, answers questions, and you start brainstorming your approach.
  Think whiteboard conversation, not a written test.
- **Building (4 hours)** - you build, using any tool you want. This repo
  assumes AI coding assistants like Claude Code, Codex, or Cursor are in
  play - Rilla provides accounts for these on the on-site laptop. Halfway
  through, an engineer pairs with you for 30 minutes: you walk through what
  you've built, your decisions, and where you're headed, and they pair with
  you live.
- **Presentation (1 hour)** - you present the product, architecture, and
  decisions. Interviewers dig into details and also ask how you'd solve the
  same problem in production at larger scale - close to a systems-design
  interview.
- **Culture Interview (30 min)** - conversation with the CTO about approach,
  values, and cultural fit.

## What This Repo Rehearses

`docs/01-problem-statement.md` and `docs/02-requirements.md` play the role of
the kickoff conversation. `data/transcripts/` is your dataset. The `solution`
branch plays the role of "what a strong answer looks like," covering all
three on-site parts: system design, the build, and the presentation.
