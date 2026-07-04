# Problem Statement: Sales Call Coaching Insights

*This is the prompt, as if handed to you at kickoff. Read it once, then start
brainstorming your approach - don't over-plan before you understand the
data.*

## Background

Sales managers at Rilla's customers (home services companies, apartment
communities, and similar in-person sales teams) can't sit in on every rep's
conversation. Today, they rely on spot-checks or "mystery shopping," which is
slow and subjective. You've been given a dataset of transcribed sales calls
and asked to build a tool that helps a sales manager quickly see how their
team is doing - which reps and which calls need coaching attention, without
listening to every call.

## What You're Given

- `data/transcripts/*.json` - ~20-30 transcribed sales calls across two
  verticals (home services, apartment leasing), each call tagged with which
  rep took it, speaker-labeled turns with timing, and a date.

## What You're Building

A working product - not a slide deck - that a sales manager could open and
immediately get value from. You have about 4 hours. You're expected to use
AI coding assistants (Claude Code, Codex, Cursor, or your own tools) the same
way you would on the job here - this is normal, not a shortcut being
penalized.

At the end, you'll present: the product, the architecture behind it, the
decisions you made and why, and how you'd evolve this design for production
scale (more customers, more calls, real-time ingestion, etc.).

See `docs/02-requirements.md` for the specific product and technical
requirements defining the scope of "done" for this exercise.
