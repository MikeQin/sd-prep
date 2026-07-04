---
marp: true
theme: default
paginate: true
---

# Sales Call Coaching Insights
### Rilla On-Site Build - Reference Presentation

---

## The Problem

Sales managers can't sit in on every rep's conversation. Coaching today
relies on slow, subjective spot-checks. This tool turns every transcribed
call into an objective scorecard, at scale.

---

## Product Walkthrough

1. **Leaderboard** - reps ranked by average call score
2. **Call Detail** - transcript and scorecard side by side
3. **Rep Profile** - score trend over time

*(live demo here)*

---

## Architecture (MVP)

![bg right:40% fit](../design/diagrams/mvp-architecture.png)

- Next.js/TypeScript frontend
- FastAPI backend, SQLite storage
- `Scorer` interface (Strategy pattern): `RuleBasedScorer` default, pluggable
  `LLMScorer`

---

## Key Decisions & Trade-offs

- **SQLite over Postgres** - zero setup for a 4-hour build; swappable later
- **Deterministic scoring first** - testable, reproducible, no API-key
  dependency; LLM scoring is an additive path, not a requirement
- **Two services, not one monolith** - mirrors how this would actually
  scale: frontend and scoring logic evolve independently

---

## Design Patterns Used

- **Strategy** - `Scorer` interface, `RuleBasedScorer` / `LLMScorer`
- **Repository** - DB access isolated behind SQLAlchemy models
- **Factory** - `get_scorer()` picks implementation from `SCORER_BACKEND` env

---

## Known Limitations

- Transcripts are pre-provided text - no ASR/audio pipeline
- No auth/multi-tenancy - single manager view
- Keyword-based scoring misses nuance an LLM or trained model would catch

---

## Production / Scale Architecture

![bg right:40% fit](../design/diagrams/production-architecture.png)

- Audio -> ASR -> queue -> autoscaled scoring workers
- Postgres with read replicas, Redis cache for dashboard reads
- Multi-tenant auth/RBAC, encryption in transit/at rest
- Stateless API tier behind a load balancer, multi-AZ for HA
- Graceful degradation: LLM scorer path failure falls back to rule-based

---

## Roadmap

1. Real ASR integration
2. Multi-tenant auth
3. Production LLM scorer with human-in-the-loop review
4. Real-time ingestion and alerting
5. CRM integrations

---

## Q&A

Appendix: API reference and data model in `design/architecture.md`.
