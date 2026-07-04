# Sales Call Coaching Insights — Reference System Design

## Overview

A tool that turns transcribed sales calls into objective coaching signal:
a per-call scorecard, a rep leaderboard, and a per-rep trend view. Built as
two services so scoring logic and presentation can evolve independently.

## MVP Architecture

See `design/diagrams/mvp-architecture.mmd`.

- **`apps/web`** — Next.js + TypeScript frontend. Server components fetch
  from the API and render the dashboard, call detail, and rep profile pages.
- **`apps/api`** — FastAPI backend. Owns ingestion, scoring, storage, and the
  REST API.
- **SQLite** — zero-setup storage for the exercise; swappable for Postgres
  in production (see Production Architecture below).

## Components

- **Ingestion** — on startup, reads `data/transcripts/*.json` and seeds the
  database if empty (`app/seed.py`).
- **Scoring Engine** — `Scorer` interface (Strategy pattern) with
  `RuleBasedScorer` as the default, dependency-free implementation, and a
  structurally-identical `LLMScorer` stub selectable via the
  `SCORER_BACKEND` env var (Factory pattern, `get_scorer()`).
- **Repository layer** — SQLAlchemy models (`RepDB`, `CallDB`, `ScoreDB`)
  isolate the rest of the app from storage details.
- **REST API** — see API Reference below.
- **Dashboard UI** — leaderboard, call detail, rep profile pages.

## API Reference

| Method | Path | Returns |
|---|---|---|
| GET | `/api/health` | `{"status": "ok"}` |
| GET | `/api/reps` | List of reps with `call_count` and `average_score` |
| GET | `/api/reps/{rep_id}` | Rep detail + list of their calls (summary) |
| GET | `/api/calls` | List of all calls (summary) |
| GET | `/api/calls/{call_id}` | Call detail: transcript turns + full scorecard |

`/api/reps` and `/api/calls` are unbounded list endpoints in the MVP - fine
at the ~20-30 call demo scale, but they need pagination (`?page=`/`?limit=`
or cursor-based) before this could handle a real customer's call volume;
see Production / Scale Architecture and Roadmap.

## Data Model

See `design/diagrams/data-model.mmd`. Three tables: `reps` (id, name,
vertical), `calls` (id, rep_id FK, customer_name, vertical, date,
duration_seconds, turns JSON), `scores` (call_id FK/PK, talk_listen_ratio,
objection_raised, objection_handled_well, pricing_discussed,
next_step_committed, sentiment_score, overall_score, `scored_by`, flags
JSON).

A `call` has **zero or one** `score`, not exactly one — nothing in the
schema forces a call to be scored (an earlier version of this diagram
showed the relationship as mandatory 1:1, which didn't match the
implementation; see Known Limitations). `scored_by` records which scorer
implementation (`"rule"` or `"llm"`) actually produced a given score, so a
silent fallback (e.g. `LLMScorer` falling back to `RuleBasedScorer` when no
API key is configured) is visible in the data rather than indistinguishable
from a real LLM score.

## Design Patterns Used

- **Strategy** — `Scorer` interface with interchangeable implementations.
- **Repository** — SQLAlchemy models as the sole data-access layer.
- **Factory** — `get_scorer()` selects an implementation from configuration.
- **Adapter** (production) — an ASR provider adapter would sit ahead of
  ingestion so the scoring pipeline is provider-agnostic.

## Production / Scale Architecture

See `design/diagrams/production-architecture.mmd`.

- **Ingestion**: audio lands in object storage, an ASR service transcribes
  it, and a message queue decouples transcription from scoring so ingestion
  spikes don't block the API. Message delivery is at-least-once, so worker
  processing must be **idempotent**: dedupe/upsert on `call_id` rather than
  a blind insert. This is the same class of bug this repo's own `seed.py`
  had in the MVP (idempotency gated on "does any rep exist" rather than
  per-call, so a re-run silently skipped newly-added transcripts) - the
  production pipeline needs the per-message version of that fix from day
  one, not as an afterthought.
- **Scoring**: autoscaled worker pool consumes the queue, calls the
  configured `Scorer` (including a real `LLMScorer` in production), writes
  results to Postgres via an upsert keyed on `call_id`, and records
  `scored_by` (and ideally a `scorer_version`, see Known Limitations) so a
  later change to scoring logic doesn't leave old rows silently stale.
- **Storage**: Postgres primary + read replicas for the API's read-heavy
  dashboard queries; Redis in front of the leaderboard/trend queries using a
  **cache-aside** pattern (API checks Redis first, falls through to Postgres
  on a miss, and populates the cache with a short TTL, e.g. ~30s). On
  writing a new score, the worker also invalidates that rep's cache entry
  rather than relying purely on TTL expiry, to bound how long a stale
  leaderboard can be served.
- **Consistency**: scoring workers write to the primary while the dashboard
  reads from replicas, so there's a small (typically sub-second)
  replication-lag window where a newly-scored call may not yet be visible
  on a read replica. Acceptable for a coaching dashboard (not a real-time
  system), but a real eventual-consistency tradeoff worth stating
  explicitly rather than assuming read-your-writes.
- **API tier**: stateless, behind a load balancer, autoscaled, deployed
  across multiple availability zones for HA. List endpoints (`/api/reps`,
  `/api/calls`) must be paginated at this scale - the MVP's unbounded lists
  only work at demo data volumes (see API Reference).
- **Security**: multi-tenant auth/RBAC so one customer's reps and transcripts
  are never visible to another; encryption in transit (TLS) and at rest for
  transcript data, which is sensitive customer-conversation content. Also
  needs a defined **data retention/deletion policy** - transcripts contain
  real customer names and conversation content, so this is a compliance
  requirement (GDPR/CCPA-style deletion requests), not just an encryption
  checkbox.
- **Resilience**: if the LLM-backed scorer's provider is unavailable, the
  worker falls back to `RuleBasedScorer` rather than blocking ingestion.

## Known Limitations

- Transcripts are pre-provided text — no ASR/audio pipeline in the MVP.
- No authentication or multi-tenancy — single implicit manager view.
- Keyword/heuristic scoring will miss nuance a trained model or LLM would
  catch (sarcasm, indirect objections, tone).
- SQLite has no concurrent-write story suitable for multiple ingestion
  workers — fine for a single-process demo, not for production.
- **No scoring-logic versioning.** There's no `scorer_version` field, so a
  change to scoring rules doesn't retroactively apply to already-scored
  calls, and there's no way to tell which calls were scored by an older
  ruleset without one. This is a real gap this repo hit directly: an
  independent review found and fixed several bugs in `RuleBasedScorer`
  (false-positive keyword matches, a mis-scoped objection check), but those
  fixes only affect *newly seeded* calls — a running deployment would need
  a `scorer_version` column plus a re-scoring/backfill job to pick up such a
  fix for existing data.
- **No pagination.** `/api/reps` and `/api/calls` return unbounded lists,
  which only works at the MVP's demo data volume (~20-30 calls).
- The ER diagram previously modeled `CALL`–`SCORE` as a mandatory 1:1
  relationship (`||--||`); the implementation doesn't enforce that (a call
  can exist without a score), so the diagram now shows it as zero-or-one
  (`||--o|`) to match reality. Worth remembering as a general lesson: keep
  diagrams honest about what the schema actually enforces, not what's
  merely intended.

## Risks

- Deterministic scoring could produce false-confidence coaching signals if
  presented without the underlying transcript for managers to verify.
- Keyword lists are English-only and vertical-agnostic; a new vertical or
  language would need new phrase banks or a model-based approach.
- A cache-aside Redis layer (production) could serve a stale leaderboard if
  invalidation on write is missed or delayed — bounded by TTL, but worth
  monitoring cache-hit staleness in practice, not just assuming TTL is safe.
- Read-replica lag means a manager could briefly not see a call that was
  just scored; low risk for a coaching tool (not real-time), but would be a
  real bug class if this data model were reused for something time-sensitive.

## Roadmap

1. Real ASR integration (audio in, transcript out).
2. Multi-tenant auth and per-customer data isolation.
3. Production `LLMScorer` with human-in-the-loop review of low-confidence
   scores.
4. Real-time ingestion and manager alerting on flagged calls.
5. CRM integrations (attach scorecards to deal records).
6. Add a `scorer_version` field and a backfill/re-scoring job so scoring-logic
   fixes and improvements can be retroactively applied to existing calls.
7. Paginate `/api/reps` and `/api/calls` before onboarding a customer with
   call volume beyond the demo dataset's scale.
8. Define and implement a transcript retention/deletion policy (including
   per-customer deletion requests) before storing real customer data.
