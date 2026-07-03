# Rilla On-Site Interview Prep Repo — Design Spec

Date: 2026-07-03
Repo: https://github.com/MikeQin/sd-prep (exists, currently empty)

## Purpose

Rilla's on-site interview (per `interview.md`) requires building a working software
product from scratch in ~4 hours, then presenting it (product + architecture +
"how would you scale this" discussion) to interviewers. This repo is a rehearsal
environment: a realistic, Rilla-domain-flavored version of that exercise, plus a
full reference solution to study against, so the candidate can practice the whole
kickoff → build → present loop before the real thing.

Candidates are explicitly allowed to use AI coding assistants (Claude Code, Codex,
Cursor) during the real on-site — this repo's scope and the reference
implementation are sized accordingly (a notch beyond bare-minimum toy CRUD, since
AI pairing accelerates boilerplate/scaffolding).

## Domain & Exercise Concept

**"Sales Call Coaching Insights"** — mirrors Rilla's real product (AI-analyzed
sales conversations enabling coaching at scale, per rilla.com/customer-stories
and rilla.com/learn/rilla-labs). The candidate ingests mock sales-call
transcripts and builds a coaching/manager dashboard:
- Per-call scorecard (talk/listen ratio, objection handling, next-step
  commitment, keyword/phrase detection, simple sentiment)
- Rep leaderboard across calls
- Rep trend view over time

Chosen over a generic FAANG-style clone (mini Twitter/Uber) because it
demonstrates domain understanding, which the Rilla process appears to value,
while staying scoped for a single build session.

## Repo Structure & Branch Strategy

Single git repo, `main` + `solution` branches (single-branch answer key,
not split further per part).

**`main`** — what a candidate sees at kickoff ("0 lines of code"):
```
sd-prep/
├── README.md                          # purpose, how to use, reference links
├── CHANGELOG.md
├── docs/
│   ├── 00-interview-overview.md       # the on-site process, adapted from interview.md
│   ├── 01-problem-statement.md        # the "prompt" — read cold, like the real kickoff
│   ├── 02-requirements.md             # product + technical requirements, in/out of scope
│   └── superpowers/specs/             # brainstorming/plan artifacts (this file, the plan)
└── data/
    └── transcripts/                   # ~20-30 mock transcripts, 2-3 verticals
```
No `apps/` code on `main` — the candidate builds that during their own practice
run on a local, uncommitted branch, then can diff against `solution`.

**`solution`** (branched from `main`) — the reference answer key:
```
├── design/
│   ├── architecture.md                # reference system design
│   └── diagrams/                      # Mermaid sources (+ exported PNG for slides)
├── apps/
│   ├── web/                           # Next.js + TypeScript frontend
│   └── api/                           # Python FastAPI backend
└── presentation/
    └── slides.md                      # Marp deck
```

Repo is connected to `origin` = `https://github.com/MikeQin/sd-prep`. Local
commits happen freely; any `git push` is confirmed with the user first.

## Part 1 — Problem Statement, Requirements, Reference Design

**Problem statement & requirements** (`docs/01-problem-statement.md`,
`docs/02-requirements.md`): written as the kickoff prompt would be, explicitly
noting AI assistant usage is expected/allowed. Requirements split into product
features (ingest transcripts, per-call scorecard, leaderboard, rep trend,
in/out of scope list) and technical requirements (stack constraint: Next.js/TS
or Python; must run locally with minimal setup; tests for scoring logic).

**Reference system design** (`design/architecture.md`, on `solution` branch)
has two layers:

1. **As-built MVP** — Next.js/TS frontend ⇄ Python FastAPI backend (REST/JSON),
   SQLite via SQLAlchemy. Components: Ingestion, Scoring Engine (`Scorer`
   interface, Strategy pattern, `RuleBasedScorer` default), Repository layer,
   REST API, Dashboard UI. API: `GET /calls`, `GET /calls/{id}`,
   `GET /reps/{id}/summary`, `GET /leaderboard`. Data model: reps,
   calls/transcripts, scores, coaching-flags.
2. **Production/scale discussion** — queue-based ingestion pipeline (audio →
   ASR → transcript → scoring), horizontal scaling of scoring workers,
   Postgres + read replicas, object storage for audio, Redis caching,
   multi-tenant auth/RBAC, encryption in transit/at rest, PII handling, HA
   (multi-AZ, stateless API tier behind LB, graceful degradation if the
   LLM-scorer path is down), known limitations, risks, roadmap.

**Diagrams** (Mermaid): MVP component diagram, ingestion→scoring→dashboard
sequence diagram, ER diagram, production-scale architecture diagram.

## Part 2 — Reference Implementation

**Backend** (`apps/api`, FastAPI): `Scorer` interface with `RuleBasedScorer`
(talk/listen ratio, keyword/phrase detection for objections/pricing/next-step
commitments, lightweight sentiment heuristic) as the working, dependency-free
default; a stubbed `LLMScorer` behind an env flag implementing the same
interface via an external LLM API call (Adapter/Factory pattern, showing how
the deterministic default would be swapped for Rilla's real AI-driven
approach). SQLite + SQLAlchemy, seeded from `data/transcripts/` at startup.
Pytest unit tests on scoring logic.

**Frontend** (`apps/web`, Next.js + TypeScript): dashboard/leaderboard page,
call detail page (transcript + scorecard breakdown), rep profile page with a
trend chart (Recharts). Typed API client matching the backend schema.

## Part 3 — Presentation

`presentation/slides.md`, Marp-authored Markdown slide deck (renders to
HTML/PDF), outline: title/problem framing → product demo walkthrough →
architecture overview → key design decisions & trade-offs → design patterns
used → known limitations & risks → production/scale story → roadmap → Q&A
appendix (API reference, data model).

## Phased Implementation Plan (high-level; detailed plan via writing-plans)

- **Phase 0** — Repo & rehearsal scaffolding: git init, remote to
  `MikeQin/sd-prep`, README/CHANGELOG, `docs/`, mock transcript dataset,
  initial commit to `main`.
- **Phase 1** — Reference system design: create `solution` branch,
  `design/architecture.md` + diagrams.
- **Phase 2** — Backend reference implementation (FastAPI, scorer, API,
  tests).
- **Phase 3** — Frontend reference implementation (Next.js/TS, pages, charts,
  wired to API).
- **Phase 4** — Presentation deck (Marp slides, embedded diagrams).
- **Phase 5** — Polish & rehearsal pass: full end-to-end dry run, gap fixes,
  finalize README, push branches (with explicit confirmation).

Each phase is sized to fit one session, since the user may not finish this in
a single sitting.

## Existing Files

The working directory currently has two loose files predating this design:
`interview.md` (the real Rilla process doc) and `prd.md` (a verbatim paste of
the original task instructions, not an actual PRD). Phase 0 will fold
`interview.md`'s content into `docs/00-interview-overview.md` and remove
`prd.md`, since this spec and the forthcoming plan supersede it.

## Out of Scope

- Real ASR/audio processing (transcripts are provided as pre-transcribed text)
- Real authentication/multi-tenancy in the MVP build (discussed only in the
  production/scale section of the design doc)
- A working, API-keyed LLM scorer wired into CI (the `LLMScorer` is a
  structurally-complete stub demonstrating the pattern, not a live dependency)
- Deployment to any cloud provider (local-run only)
