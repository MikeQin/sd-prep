# Rilla On-Site Interview Prep

This repo is a rehearsal environment for the Rilla on-site interview: a
Rilla-domain-flavored version of the "build a product from scratch in ~4
hours, then present it" exercise described in `docs/00-interview-overview.md`.

## Purpose

- Practice the full on-site loop: kickoff, build, present, under realistic
  time pressure.
- Study a complete reference solution (system design + working implementation
  + presentation deck) after your own attempt, to see gaps and alternatives.

## How to Use This Repo

1. Read `docs/00-interview-overview.md` for the process this rehearses.
2. Read `docs/01-problem-statement.md` cold, as if it were just handed to you
   at kickoff. Skim `data/transcripts/` - that's your dataset.
3. Read `docs/02-requirements.md` for the product and technical requirements.
4. Set a timer for ~4 hours. Build a working product from scratch, on your
   own local branch (don't commit to `main`). Use AI coding assistants
   freely - that's expected, per the real process.
5. Spend the last hour drafting a short presentation of what you built.
6. Compare your design and implementation against the `solution` branch:
   `git fetch origin && git diff main origin/solution -- design/ apps/`.

## Reference Links

- Rilla customer stories: https://www.rilla.com/customer-stories
- Rilla Labs: https://www.rilla.com/learn/rilla-labs
- This repo's interview-process notes: `docs/00-interview-overview.md`

## Repo Structure

See `docs/superpowers/specs/2026-07-03-rilla-onsite-prep-design.md` for the
full design rationale, and
`docs/superpowers/plans/2026-07-03-rilla-onsite-prep-plan.md` for the
implementation plan this repo was built from.
