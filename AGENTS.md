# Agent Handoff — Rilla On-Site Prep Repo

You are implementing a **pre-written, fully-specified plan**. Do not redesign,
re-scope, or improvise architecture — the design and task breakdown are
already decided. Your job is execution, not planning.

## Read first, in this order

1. `docs/superpowers/specs/2026-07-03-rilla-onsite-prep-design.md` — why this
   repo exists and what's being built (design spec).
2. `docs/superpowers/plans/2026-07-03-rilla-onsite-prep-plan.md` — the actual
   task list and **source of truth** for what to build, in what order, and
   with what exact file paths / interfaces. It is written as TDD steps
   (write failing test → run, confirm it fails → implement → run, confirm it
   passes → commit) for every task. Follow that cycle for every task — don't
   skip the "verify it fails" / "verify it passes" steps, and don't batch
   multiple tasks' commits together.
3. `interview.md` and `prd.md` at repo root — background source docs that
   Phase 0 / Task 2 of the plan folds into `docs/` and then deletes. Read
   them for context; don't treat them as current requirements.

## Non-negotiable constraints

Do not deviate from these without stopping and asking first:

- **Branch split:** `main` = kickoff materials only (`README.md`,
  `CHANGELOG.md`, `docs/`, `data/transcripts/`). **Zero application code on
  `main`, ever.** `solution` branch (created in Task 3) = everything else:
  `design/`, `apps/web`, `apps/api`, `presentation/`.
- **Stack is fixed:** Next.js + TypeScript (frontend) and Python + FastAPI
  (backend) only. No other language/framework for core product code.
- **Explicitly out of scope everywhere:** real ASR/audio processing,
  auth/multi-tenancy, cloud deployment, a live-keyed LLM scorer wired into
  the default path. The plan's `LLMScorer` is a structurally-complete stub
  behind an env flag — do not wire it to a real API key or make it the
  default.
- **Never run `git push`** to the `MikeQin/sd-prep` remote without asking me
  first and getting explicit confirmation. Local commits after each task are
  expected and fine.
- **`CHANGELOG.md`** is updated only at the two points the plan specifies
  (Phase 0 Task 2, Phase 5 Task 15) — not after every intermediate task.
- Use the commit messages/conventions given in each task's step (conventional
  commits: `feat:`, `docs:`, `fix:`, etc.).
- Treat the interface names/shapes documented in each task's **Interfaces**
  section as load-bearing contracts for later tasks (e.g. `generate_all()`'s
  return schema, `Scorer.score()`'s signature, the REST response shapes) —
  don't rename or reshape them without checking what downstream task consumes
  them.

## Execution mode

Work through the plan's tasks in order, Task 1 → Task 16, respecting phase
and branch boundaries (Phase 0 on `main`; Phases 1-5 on `solution`, which
Task 3 creates). Finish and verify one task fully (tests passing, committed)
before starting the next. If the plan is ambiguous about something, stop and
ask rather than guessing a scope expansion — this repo is meant to model a
specific, already-agreed-upon reference solution, not your own take on the
problem.

## Status as of handoff

Nothing has been implemented yet. The local git repo exists at this path
with the `origin` remote (`https://github.com/MikeQin/sd-prep`) already
configured but nothing pushed. Start at Phase 0, Task 1 (mock transcript
data generator).

## Definition of done

All 16 tasks across 6 phases complete: `solution` branch has a working
`apps/web` (Next.js/TS) + `apps/api` (FastAPI) + `presentation/slides.md`
(Marp deck); `main` remains code-free; nothing has been pushed to GitHub
until explicitly approved.
