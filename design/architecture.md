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

## Data Model

See `design/diagrams/data-model.mmd`. Three tables: `reps` (id, name,
vertical), `calls` (id, rep_id FK, customer_name, vertical, date,
duration_seconds, turns JSON), `scores` (call_id FK/PK, talk_listen_ratio,
objection_raised, objection_handled_well, pricing_discussed,
next_step_committed, sentiment_score, overall_score, flags JSON).

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
  spikes don't block the API.
- **Scoring**: autoscaled worker pool consumes the queue, calls the
  configured `Scorer` (including a real `LLMScorer` in production), writes
  results to Postgres.
- **Storage**: Postgres primary + read replicas for the API's read-heavy
  dashboard queries; Redis in front of the leaderboard/trend queries.
- **API tier**: stateless, behind a load balancer, autoscaled, deployed
  across multiple availability zones for HA.
- **Security**: multi-tenant auth/RBAC so one customer's reps and transcripts
  are never visible to another; encryption in transit (TLS) and at rest for
  transcript data, which is sensitive customer-conversation content.
- **Resilience**: if the LLM-backed scorer's provider is unavailable, the
  worker falls back to `RuleBasedScorer` rather than blocking ingestion.

## Known Limitations

- Transcripts are pre-provided text — no ASR/audio pipeline in the MVP.
- No authentication or multi-tenancy — single implicit manager view.
- Keyword/heuristic scoring will miss nuance a trained model or LLM would
  catch (sarcasm, indirect objections, tone).
- SQLite has no concurrent-write story suitable for multiple ingestion
  workers — fine for a single-process demo, not for production.

## Risks

- Deterministic scoring could produce false-confidence coaching signals if
  presented without the underlying transcript for managers to verify.
- Keyword lists are English-only and vertical-agnostic; a new vertical or
  language would need new phrase banks or a model-based approach.

## Roadmap

1. Real ASR integration (audio in, transcript out).
2. Multi-tenant auth and per-customer data isolation.
3. Production `LLMScorer` with human-in-the-loop review of low-confidence
   scores.
4. Real-time ingestion and manager alerting on flagged calls.
5. CRM integrations (attach scorecards to deal records).
