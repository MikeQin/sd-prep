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

## Reference Solution (on the `solution` branch)

`git fetch origin && git checkout solution` to see:
- `design/architecture.md` + `design/diagrams/` - full system design
- `apps/api` - FastAPI backend, `apps/web` - Next.js/TS frontend
- `presentation/slides.md` - a reference Marp deck

Try `docs/03-rehearsal-checklist.md` for a full timed dry run.

## Running the App

Requires **Python 3.11+** and **Node.js 20+**. Start the backend first -
the frontend expects it on port 8000.

### Backend (`apps/api`)

```bash
cd apps/api
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Seeds automatically from `data/transcripts/*.json` on first startup into a
local `coaching_insights.db` SQLite file (gitignored). Verify with
`curl http://localhost:8000/api/reps` - should return 6 reps.

### Frontend (`apps/web`)

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:3000`.

### Environment Variables (optional)

| Variable | Where | Default | Purpose |
|---|---|---|---|
| `SCORER_BACKEND` | backend | `rule` | `rule` or `llm` - selects the scoring implementation via `get_scorer()`. `llm` currently falls back to rule-based scoring unless `LLM_API_KEY` is set, since `LLMScorer` is a structurally-complete stub, not wired to a live provider (see `docs/02-requirements.md`). |
| `LLM_API_KEY` | backend | unset | Only read by the `LLMScorer` stub; has no effect on scoring since it's never wired to a real API call. |
| `NEXT_PUBLIC_API_BASE_URL` | frontend | `http://localhost:8000` | Where the frontend fetches the API from. |

### Resetting the Database

Seeding is idempotent per-call (new transcripts added to `data/transcripts/`
get picked up on restart, already-seeded ones don't get re-inserted). To
start over from scratch instead, stop the backend and delete
`apps/api/coaching_insights.db`, then restart it.

### Running Tests

```bash
cd apps/api && python -m pytest tests -v   # backend: 31 tests
cd apps/web && npm test                    # frontend: 9 tests
cd apps/web && npx tsc --noEmit            # frontend: type-check
```
