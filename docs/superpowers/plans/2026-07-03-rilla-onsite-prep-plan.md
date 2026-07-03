# Rilla On-Site Interview Prep Repo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a rehearsal repo for Rilla's on-site interview: a "Sales Call
Coaching Insights" exercise (problem statement + requirements + mock data on
`main`) with a full reference solution (system design, Next.js/TS + Python
FastAPI implementation, Marp presentation deck) on a `solution` branch.

**Architecture:** Two services on the `solution` branch — a Python FastAPI
backend with a pluggable `Scorer` strategy (deterministic `RuleBasedScorer`
default, stubbed `LLMScorer`) backed by SQLite, and a Next.js/TypeScript
frontend consuming it over REST. `main` carries only the kickoff materials
(docs + mock dataset), no application code, so it stays "0 lines of code"
for rehearsal purposes.

**Tech Stack:** Python 3.11+ / FastAPI / SQLAlchemy / pytest (backend);
Next.js 14 (App Router) / TypeScript / Recharts / Vitest + Testing Library
(frontend); Marp (presentation); Mermaid (diagrams).

## Global Constraints

- Core product code must be Next.js/React+TypeScript and/or Python only —
  no other language/framework (per `docs/02-requirements.md`).
- `main` branch: docs + `data/transcripts/` only, no `apps/` code — it must
  stay "0 lines of code" for rehearsal fidelity.
- `solution` branch: everything else (design docs, diagrams, `apps/web`,
  `apps/api`, `presentation/`).
- No real ASR/audio processing, no auth/multi-tenancy, no cloud deployment —
  explicitly out of scope everywhere in this plan.
- Any `git push` to the `MikeQin/sd-prep` remote requires explicit user
  confirmation before running — never push automatically.
- `CHANGELOG.md` is updated twice: once in Phase 0 (Task 2, kickoff
  materials) and once in Phase 5 (Task 15, summarizing everything added on
  the `solution` branch) — not after every intermediate task.
- Backend commands assume Python 3.11+ with `pip` available; a virtualenv is
  recommended but not required by these steps.
- Frontend commands assume Node.js 20+ with `npm` available.

---

## Phase 0 — Repo & Rehearsal Scaffolding (`main` branch)

### Task 1: Mock transcript data generator

**Files:**
- Create: `data/__init__.py`
- Create: `data/generate_transcripts.py`
- Create: `data/requirements.txt`
- Create: `data/tests/__init__.py`
- Create: `data/tests/test_generate_transcripts.py`

**Interfaces:**
- Produces: `generate_all() -> list[dict]` — writes one JSON file per call to
  `data/transcripts/`, returns the list of call dicts. Each call dict has keys
  `call_id, vertical, rep_id, rep_name, customer_name, date,
  duration_seconds, turns` where `turns` is a list of
  `{speaker, start, end, text}` dicts. Later tasks (backend seeding) read
  these JSON files directly — this exact schema is load-bearing.

- [ ] **Step 1: Write the failing tests**

```python
# data/tests/test_generate_transcripts.py
import json
from pathlib import Path

from data.generate_transcripts import generate_all, OUTPUT_DIR, REPS


def test_generate_all_produces_expected_call_count_range():
    calls = generate_all()
    assert 20 <= len(calls) <= 30


def test_each_call_has_required_schema_fields():
    calls = generate_all()
    required = {
        "call_id", "vertical", "rep_id", "rep_name", "customer_name",
        "date", "duration_seconds", "turns",
    }
    for call in calls:
        assert required.issubset(call.keys())
        assert len(call["turns"]) > 0
        for turn in call["turns"]:
            assert turn["speaker"] in ("rep", "customer")
            assert turn["end"] > turn["start"]


def test_all_verticals_and_reps_represented():
    calls = generate_all()
    verticals = {c["vertical"] for c in calls}
    rep_ids = {c["rep_id"] for c in calls}
    assert verticals == {"home_services", "apartment_leasing"}
    assert rep_ids == {r["id"] for r in REPS}


def test_output_files_written_to_disk():
    generate_all()
    written = list(OUTPUT_DIR.glob("*.json"))
    assert len(written) >= 20
    sample = json.loads(written[0].read_text())
    assert "call_id" in sample
```

Also create empty `data/__init__.py` and `data/tests/__init__.py` (zero
bytes) so `data.generate_transcripts` is importable as a package.

- [ ] **Step 2: Run tests to verify they fail**

Run (from repo root): `pip install -r data/requirements.txt && python -m pytest data/tests -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'data.generate_transcripts'`

- [ ] **Step 3: Write the generator implementation**

```python
# data/requirements.txt
pytest>=7.4
```

```python
# data/generate_transcripts.py
"""Generate synthetic sales-call transcripts for the Rilla on-site prep exercise."""
import json
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).parent / "transcripts"

VERTICALS = ["home_services", "apartment_leasing"]

REPS = [
    {"id": "rep-01", "name": "Jordan Blake", "vertical": "home_services", "tier": "strong"},
    {"id": "rep-02", "name": "Casey Nguyen", "vertical": "home_services", "tier": "average"},
    {"id": "rep-03", "name": "Riley Thompson", "vertical": "home_services", "tier": "weak"},
    {"id": "rep-04", "name": "Morgan Ellis", "vertical": "apartment_leasing", "tier": "strong"},
    {"id": "rep-05", "name": "Avery Kim", "vertical": "apartment_leasing", "tier": "average"},
    {"id": "rep-06", "name": "Drew Patel", "vertical": "apartment_leasing", "tier": "weak"},
]

CUSTOMER_NAMES = [
    "Pat Romero", "Sam Osei", "Jamie Cruz", "Taylor Novak", "Alex Farrow",
    "Chris Bellamy", "Robin Hart", "Skyler Voss", "Quinn Alvarado", "Reese Dunlap",
]

OPENERS = {
    "home_services": [
        "Hi {customer}, thanks for having me out today to look at your {system}.",
        "Good afternoon, I'm with the team that called about your {system} estimate.",
    ],
    "apartment_leasing": [
        "Hi {customer}, welcome in! Thanks for scheduling a tour with us today.",
        "Hey {customer}, great to meet you, ready to see the community?",
    ],
}

DISCOVERY_REP = [
    "So tell me, what's prompting you to look into this now?",
    "What's most important to you as you're making this decision?",
    "Have you looked at other options before reaching out to us?",
]

DISCOVERY_CUSTOMER = [
    "Honestly our old unit finally gave out last week.",
    "We're just comparing a few places before we decide.",
    "We want something reliable that won't cost us more down the road.",
]

PRICING_REP = [
    "Based on what we've walked through, the total price for this would be {price}.",
    "For the package we discussed, the total cost is {price}.",
]

OBJECTION_CUSTOMER = [
    "That's a bit more than I expected, it feels too expensive.",
    "I'll need to talk to my spouse before we commit to anything.",
    "We were planning to shop around a little more first.",
]

OBJECTION_HANDLING = {
    "strong": [
        "Totally fair, a lot of folks feel that way at first. Let's break down what's included so you can see the value, and I can walk you through financing.",
    ],
    "average": [
        "I understand, it is an investment. We do have financing options if that helps.",
    ],
    "weak": [
        "Okay, well, the price is the price, but let me know if you change your mind.",
    ],
}

NEXT_STEP_REP = {
    "strong": [
        "Let's go ahead and schedule this for next week, and I'll follow up tomorrow to confirm everything.",
    ],
    "average": [
        "Why don't I send over the paperwork and we can follow up in a few days?",
    ],
    "weak": [
        "Alright, well, feel free to reach out whenever you're ready.",
    ],
}

NEXT_STEP_CUSTOMER = {
    "strong": ["Sounds good, let's do it.", "Yes, let's move forward with that."],
    "average": ["Okay sure, send it over.", "Alright, we can look at it."],
    "weak": ["Yeah, maybe.", "We'll see."],
}

CLOSING_CUSTOMER_NO_COMMIT = [
    "We'll think about it and let you know.",
    "Not sure yet, we'll be in touch.",
]


def _duration_for(text: str) -> float:
    return max(1.5, len(text.split()) * 0.4)


def _build_turns(rep: dict, customer_name: str, vertical: str) -> tuple[list[dict], float]:
    turns: list[dict] = []
    t = 0.0

    def add(speaker: str, text: str) -> None:
        nonlocal t
        dur = _duration_for(text)
        turns.append({"speaker": speaker, "start": round(t, 1), "end": round(t + dur, 1), "text": text})
        t += dur

    system = random.choice(["HVAC system", "water heater", "electrical panel"]) if vertical == "home_services" else ""
    opener = random.choice(OPENERS[vertical]).format(customer=customer_name, system=system)
    add("rep", opener)
    add("customer", "Thanks for coming, come on in." if vertical == "home_services" else "Thanks, excited to see it!")

    add("rep", random.choice(DISCOVERY_REP))
    add("customer", random.choice(DISCOVERY_CUSTOMER))

    price = random.choice(["$4,200", "$6,800", "$1,150/month", "$980/month"])
    add("rep", random.choice(PRICING_REP).format(price=price))

    tier = rep["tier"]
    raises_objection = tier != "strong" or random.random() < 0.5
    if raises_objection:
        add("customer", random.choice(OBJECTION_CUSTOMER))
        add("rep", random.choice(OBJECTION_HANDLING[tier]))

    add("rep", random.choice(NEXT_STEP_REP[tier]))
    if tier == "weak" and random.random() < 0.6:
        add("customer", random.choice(CLOSING_CUSTOMER_NO_COMMIT))
    else:
        add("customer", random.choice(NEXT_STEP_CUSTOMER[tier]))

    return turns, round(t, 1)


def generate_all() -> list[dict]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    calls = []
    call_index = 1
    start_date = date(2026, 5, 1)
    for rep in REPS:
        num_calls = random.randint(4, 5)
        for _ in range(num_calls):
            customer_name = random.choice(CUSTOMER_NAMES)
            turns, duration = _build_turns(rep, customer_name, rep["vertical"])
            call = {
                "call_id": f"{rep['vertical'][:2]}-{call_index:04d}",
                "vertical": rep["vertical"],
                "rep_id": rep["id"],
                "rep_name": rep["name"],
                "customer_name": customer_name,
                "date": str(start_date + timedelta(days=call_index)),
                "duration_seconds": duration,
                "turns": turns,
            }
            calls.append(call)
            call_index += 1
    for call in calls:
        path = OUTPUT_DIR / f"{call['call_id']}.json"
        path.write_text(json.dumps(call, indent=2))
    return calls


if __name__ == "__main__":
    generated = generate_all()
    print(f"Generated {len(generated)} transcripts in {OUTPUT_DIR}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest data/tests -v`
Expected: 4 passed

- [ ] **Step 5: Generate the actual dataset and commit**

```bash
python data/generate_transcripts.py
git add data/__init__.py data/generate_transcripts.py data/requirements.txt data/tests data/transcripts
git commit -m "feat: add mock sales-call transcript generator and dataset"
```

---

### Task 2: README, CHANGELOG, kickoff docs, and repo cleanup

**Files:**
- Create: `README.md`
- Create: `CHANGELOG.md`
- Create: `docs/00-interview-overview.md`
- Create: `docs/01-problem-statement.md`
- Create: `docs/02-requirements.md`
- Delete: `prd.md` (superseded by `docs/superpowers/specs/2026-07-03-rilla-onsite-prep-design.md`)
- Delete: `interview.md` (content folded into `docs/00-interview-overview.md`)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: no code interfaces — these are the human-facing docs every later
  phase's README/checklist steps will reference by path.

- [ ] **Step 1: Write `docs/00-interview-overview.md`**

```markdown
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
```

- [ ] **Step 2: Write `docs/01-problem-statement.md`**

```markdown
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
```

- [ ] **Step 3: Write `docs/02-requirements.md`**

```markdown
# Requirements: Sales Call Coaching Insights

## Product Requirements

**In scope:**
1. Ingest the provided transcript dataset (`data/transcripts/*.json`) into
   whatever storage you choose.
2. For each call, compute a **scorecard**: at minimum, a talk/listen ratio,
   whether a pricing objection came up and how it was handled, whether the
   rep secured a next-step commitment, and an overall call score.
3. A **call detail view**: the transcript alongside its scorecard.
4. A **leaderboard**: reps ranked by performance across their calls, so a
   manager can see who's excelling and who needs coaching.
5. A **rep trend view**: how a single rep's scores change over time/calls.

**Out of scope (explicitly - don't spend time here):**
- Real audio processing or speech-to-text (transcripts are provided as text).
- Authentication, multi-tenancy, or user accounts.
- Deployment anywhere - running locally is sufficient.
- A live-keyed LLM integration wired into the default path (a structurally
  complete stub/pattern showing how one *would* plug in is enough - see
  Technical Requirements).

**Stretch, if time allows:** a pluggable "LLM-backed" scoring mode alongside
your default scoring approach, and/or filtering the leaderboard/calls list by
vertical or date range.

## Technical Requirements

1. Implementation must use **Next.js/React with TypeScript, and/or Python**
   - no other language/framework for the core product.
2. The project must run locally with a minimal, documented setup (a README
   section is enough - no infra required).
3. Your scoring logic must have automated tests. It's the part of this
   system most worth testing: it's pure logic, deterministic, and it's the
   "product" - if it's wrong, the whole tool gives bad coaching advice.
4. Be ready to explain, live, how you'd change this design to handle: many
   more customers and calls, real-time ingestion instead of a batch dataset,
   and the security/privacy concerns of storing sales call transcripts.
```

- [ ] **Step 4: Write `README.md`**

```markdown
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
```

- [ ] **Step 5: Write `CHANGELOG.md`**

```markdown
# Changelog

All notable changes to this rehearsal repo are documented here.

## [Unreleased]

### Added
- Design spec for the Rilla on-site interview prep repo.
- Mock sales-call transcript generator and dataset (`data/`).
- Kickoff docs: interview overview, problem statement, requirements.
```

- [ ] **Step 6: Remove superseded files and commit**

```bash
rm interview.md prd.md
git add -A README.md CHANGELOG.md docs interview.md prd.md
git commit -m "docs: add rehearsal README, changelog, and kickoff docs"
```

- [ ] **Step 7: Add the GitHub remote (no push yet)**

```bash
git remote add origin https://github.com/MikeQin/sd-prep.git
git remote -v
```

Do **not** run `git push` here — confirm with the user first (per Global
Constraints). Pushing happens in Task 16.

---

## Phase 1 — Reference System Design (`solution` branch)

### Task 3: Create `solution` branch and write the architecture doc

**Files:**
- Create: `design/architecture.md`

**Interfaces:**
- Consumes: nothing (this is a design document, not code).
- Produces: the API contract (`GET /api/reps`, `GET /api/reps/{id}`,
  `GET /api/calls`, `GET /api/calls/{id}`) and data model (reps, calls,
  scores) that Tasks 5-13 implement exactly as described here.

- [ ] **Step 1: Create the `solution` branch**

```bash
git checkout -b solution
```

- [ ] **Step 2: Write `design/architecture.md`**

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
git add design/architecture.md
git commit -m "docs: add reference system design for coaching insights"
```

---

### Task 4: Reference architecture diagrams

**Files:**
- Create: `design/diagrams/mvp-architecture.mmd`
- Create: `design/diagrams/ingestion-sequence.mmd`
- Create: `design/diagrams/data-model.mmd`
- Create: `design/diagrams/production-architecture.mmd`

**Interfaces:**
- Consumes: the component/API/data-model description written in Task 3.
- Produces: diagram source files referenced from `design/architecture.md`
  and later embedded (as exported PNGs) in `presentation/slides.md` (Task 14).

- [ ] **Step 1: Write `design/diagrams/mvp-architecture.mmd`**

```
flowchart LR
    subgraph Frontend [apps/web - Next.js + TS]
        UI[Dashboard / Call Detail / Rep Profile]
    end
    subgraph Backend [apps/api - FastAPI]
        API[REST API]
        Scorer[Scorer Strategy: RuleBasedScorer / LLMScorer]
        Repo[Repository Layer]
    end
    DB[(SQLite)]
    Seed[data/transcripts/*.json]

    UI -->|HTTP/JSON| API
    API --> Scorer
    API --> Repo
    Repo --> DB
    Seed -->|seed on startup| Repo
```

- [ ] **Step 2: Write `design/diagrams/ingestion-sequence.mmd`**

```
sequenceDiagram
    participant Seed as data/transcripts/*.json
    participant API as FastAPI app startup
    participant Scorer as Scorer (RuleBasedScorer)
    participant DB as SQLite

    API->>Seed: read transcript files
    loop each transcript
        API->>Scorer: score(call_transcript)
        Scorer-->>API: ScoreResult
        API->>DB: insert rep, call, score rows
    end
    Note over API,DB: Subsequent requests read directly from DB, no re-scoring
```

- [ ] **Step 3: Write `design/diagrams/data-model.mmd`**

```
erDiagram
    REP ||--o{ CALL : takes
    CALL ||--|| SCORE : has

    REP {
        string id PK
        string name
        string vertical
    }
    CALL {
        string id PK
        string rep_id FK
        string customer_name
        string vertical
        date date
        float duration_seconds
        json turns
    }
    SCORE {
        string call_id PK "FK"
        float talk_listen_ratio
        bool objection_raised
        bool objection_handled_well
        bool pricing_discussed
        bool next_step_committed
        float sentiment_score
        float overall_score
        json flags
    }
```

- [ ] **Step 4: Write `design/diagrams/production-architecture.mmd`**

```
flowchart TB
    subgraph Clients
        Mgr[Manager Dashboard - Next.js]
    end
    LB[Load Balancer]
    subgraph API_Tier [Stateless API Tier, autoscaled]
        API1[API instance]
        API2[API instance]
    end
    Queue[[Message Queue]]
    subgraph Workers [Scoring Workers, autoscaled]
        W1[Worker]
        W2[Worker]
    end
    ASR[ASR / Transcription Service]
    ObjStore[(Object Storage - raw audio)]
    PG[(Postgres - primary + read replicas)]
    Cache[(Redis Cache)]
    LLM[LLM Scoring Provider]

    Mgr -->|HTTPS| LB --> API1
    LB --> API2
    API1 --> Cache
    API2 --> Cache
    Cache --> PG
    API1 --> PG
    API2 --> PG

    ObjStore --> ASR --> Queue
    Queue --> W1
    Queue --> W2
    W1 --> LLM
    W2 --> LLM
    W1 --> PG
    W2 --> PG
```

- [ ] **Step 5: Verify diagrams render and commit**

Open each `.mmd` file's content in the GitHub web preview (Mermaid renders
natively in `.md`) or paste into https://mermaid.live to sanity-check syntax
before committing.

```bash
git add design/diagrams
git commit -m "docs: add mermaid diagrams for reference architecture"
```

---

## Phase 2 — Backend Reference Implementation (`apps/api`, `solution` branch)

### Task 5: FastAPI project scaffold and health check

**Files:**
- Create: `apps/api/requirements.txt`
- Create: `apps/api/.gitignore`
- Create: `apps/api/app/__init__.py`
- Create: `apps/api/app/main.py`
- Create: `apps/api/tests/__init__.py`
- Create: `apps/api/tests/test_health.py`

**Interfaces:**
- Produces: `app.main:app` (the FastAPI instance), `GET /api/health`.

- [ ] **Step 1: Write the failing test**

```python
# apps/api/tests/test_health.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
mkdir -p apps/api/app apps/api/tests
```

Run (from `apps/api`): `python -m pytest tests -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 3: Write the scaffold**

```
# apps/api/requirements.txt
fastapi>=0.110
uvicorn[standard]>=0.29
sqlalchemy>=2.0
pydantic>=2.6
pytest>=7.4
httpx>=0.27
```

```
# apps/api/.gitignore
__pycache__/
*.pyc
.venv/
*.db
```

```python
# apps/api/app/main.py
from fastapi import FastAPI

app = FastAPI(title="Rilla Coaching Insights API")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

Create empty `apps/api/app/__init__.py` and `apps/api/tests/__init__.py`.

- [ ] **Step 4: Run test to verify it passes**

Run (from `apps/api`): `pip install -r requirements.txt && python -m pytest tests -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add apps/api/requirements.txt apps/api/.gitignore apps/api/app apps/api/tests
git commit -m "feat(api): scaffold FastAPI app with health check"
```

---

### Task 6: Scorer domain models and `RuleBasedScorer`

**Files:**
- Create: `apps/api/app/scoring/__init__.py`
- Create: `apps/api/app/scoring/models.py`
- Create: `apps/api/app/scoring/rule_based.py`
- Create: `apps/api/tests/test_rule_based_scorer.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `Turn(speaker, start, end, text)`, `CallTranscript(call_id,
  rep_id, vertical, turns)`, `ScoreResult(talk_listen_ratio, objection_raised,
  objection_handled_well, pricing_discussed, next_step_committed,
  sentiment_score, overall_score, flags)`, and `RuleBasedScorer.score(call:
  CallTranscript) -> ScoreResult`. Tasks 7-9 import these exact names.

- [ ] **Step 1: Write the failing tests**

```python
# apps/api/tests/test_rule_based_scorer.py
from app.scoring.models import CallTranscript, Turn
from app.scoring.rule_based import RuleBasedScorer


def _turn(speaker: str, text: str, start: float, end: float) -> Turn:
    return Turn(speaker=speaker, start=start, end=end, text=text)


def test_strong_call_scores_high_and_has_no_flags():
    call = CallTranscript(
        call_id="hs-0001",
        rep_id="rep-01",
        vertical="home_services",
        turns=[
            _turn("rep", "Thanks for having me out today, let's talk about your system.", 0, 3),
            _turn("customer", "Sure, happy to walk through it.", 3, 6),
            _turn("rep", "The total price for this would be $4,200.", 6, 9),
            _turn("customer", "That feels too expensive honestly.", 9, 12),
            _turn("rep", "Totally fair, let's break down what's included and financing options.", 12, 15),
            _turn("rep", "Let's schedule this for next week.", 15, 17),
            _turn("customer", "Sounds good, let's do it.", 17, 19),
        ],
    )

    result = RuleBasedScorer().score(call)

    assert result.pricing_discussed is True
    assert result.objection_raised is True
    assert result.objection_handled_well is True
    assert result.next_step_committed is True
    assert result.flags == []
    assert result.overall_score > 70


def test_weak_call_flags_unhandled_objection_and_no_commitment():
    call = CallTranscript(
        call_id="hs-0002",
        rep_id="rep-03",
        vertical="home_services",
        turns=[
            _turn("rep", "Here's the system and here's the total cost, $6,800.", 0, 5),
            _turn("customer", "That's too expensive, we'll need to think about it.", 5, 8),
            _turn("rep", "Okay well the price is the price.", 8, 10),
            _turn("customer", "We'll see.", 10, 11),
        ],
    )

    result = RuleBasedScorer().score(call)

    assert result.objection_raised is True
    assert result.objection_handled_well is False
    assert result.next_step_committed is False
    assert "objection_not_handled" in result.flags
    assert "no_next_step_commitment" in result.flags


def test_talk_listen_ratio_flags_rep_dominating_conversation():
    call = CallTranscript(
        call_id="hs-0003",
        rep_id="rep-02",
        vertical="home_services",
        turns=[
            _turn("rep", "word " * 40, 0, 16),
            _turn("customer", "okay", 16, 17.5),
        ],
    )

    result = RuleBasedScorer().score(call)

    assert result.talk_listen_ratio > 2.5
    assert "rep_talked_too_much" in result.flags
```

- [ ] **Step 2: Run tests to verify they fail**

Run (from `apps/api`): `python -m pytest tests/test_rule_based_scorer.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.scoring'`

- [ ] **Step 3: Write the implementation**

```python
# apps/api/app/scoring/models.py
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Turn:
    speaker: str  # "rep" or "customer"
    start: float
    end: float
    text: str

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass
class CallTranscript:
    call_id: str
    rep_id: str
    vertical: str
    turns: list[Turn]


@dataclass
class ScoreResult:
    talk_listen_ratio: float
    objection_raised: bool
    objection_handled_well: bool
    pricing_discussed: bool
    next_step_committed: bool
    sentiment_score: float
    overall_score: float
    flags: list[str] = field(default_factory=list)
```

```python
# apps/api/app/scoring/rule_based.py
from __future__ import annotations

from app.scoring.models import CallTranscript, ScoreResult

OBJECTION_PHRASES = ["too expensive", "talk to my spouse", "shop around", "think about it"]
HANDLING_PHRASES = ["financing", "break down what's included", "value", "understand"]
PRICING_PHRASES = ["price", "cost", "total", "$", "/month"]
NEXT_STEP_PHRASES = ["schedule", "follow up", "send over", "paperwork", "next week", "move forward"]
NEXT_STEP_COMMIT_PHRASES = ["sounds good", "let's do it", "let's move forward", "sure, send it", "yes"]
POSITIVE_WORDS = ["great", "good", "excited", "sounds good", "yes", "sure"]
NEGATIVE_WORDS = ["expensive", "not sure", "think about it", "shop around", "we'll see"]


def _contains_any(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


class RuleBasedScorer:
    """Deterministic, keyword-and-timing based scorer. No external dependencies."""

    def score(self, call: CallTranscript) -> ScoreResult:
        rep_time = sum(t.duration for t in call.turns if t.speaker == "rep")
        customer_time = sum(t.duration for t in call.turns if t.speaker == "customer")
        talk_listen_ratio = round(rep_time / customer_time, 2) if customer_time else float("inf")

        customer_turns = [t.text for t in call.turns if t.speaker == "customer"]
        rep_turns = [t.text for t in call.turns if t.speaker == "rep"]

        objection_raised = any(_contains_any(t, OBJECTION_PHRASES) for t in customer_turns)
        objection_handled_well = objection_raised and any(
            _contains_any(t, HANDLING_PHRASES) for t in rep_turns
        )
        pricing_discussed = any(_contains_any(t, PRICING_PHRASES) for t in rep_turns)
        next_step_offered = any(_contains_any(t, NEXT_STEP_PHRASES) for t in rep_turns)
        next_step_committed = next_step_offered and any(
            _contains_any(t, NEXT_STEP_COMMIT_PHRASES) for t in customer_turns
        )

        positive_hits = sum(_contains_any(t, POSITIVE_WORDS) for t in customer_turns)
        negative_hits = sum(_contains_any(t, NEGATIVE_WORDS) for t in customer_turns)
        total_hits = positive_hits + negative_hits
        sentiment_score = round((positive_hits - negative_hits) / total_hits, 2) if total_hits else 0.0

        flags: list[str] = []
        if talk_listen_ratio > 2.5:
            flags.append("rep_talked_too_much")
        if objection_raised and not objection_handled_well:
            flags.append("objection_not_handled")
        if not next_step_committed:
            flags.append("no_next_step_commitment")

        score_components = [
            1.0 if 0.5 <= talk_listen_ratio <= 2.5 else 0.4,
            1.0 if not objection_raised or objection_handled_well else 0.2,
            1.0 if pricing_discussed else 0.5,
            1.0 if next_step_committed else 0.3,
            (sentiment_score + 1) / 2,
        ]
        overall_score = round(sum(score_components) / len(score_components) * 100, 1)

        return ScoreResult(
            talk_listen_ratio=talk_listen_ratio,
            objection_raised=objection_raised,
            objection_handled_well=objection_handled_well,
            pricing_discussed=pricing_discussed,
            next_step_committed=next_step_committed,
            sentiment_score=sentiment_score,
            overall_score=overall_score,
            flags=flags,
        )
```

Create empty `apps/api/app/scoring/__init__.py`.

- [ ] **Step 4: Run tests to verify they pass**

Run (from `apps/api`): `python -m pytest tests/test_rule_based_scorer.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/scoring apps/api/tests/test_rule_based_scorer.py
git commit -m "feat(api): add Scorer domain models and RuleBasedScorer"
```

---

### Task 7: `LLMScorer` stub and scorer factory

**Files:**
- Create: `apps/api/app/scoring/llm_scorer.py`
- Create: `apps/api/app/scoring/factory.py`
- Create: `apps/api/tests/test_scorer_factory.py`

**Interfaces:**
- Consumes: `RuleBasedScorer`, `CallTranscript`, `ScoreResult` from Task 6.
- Produces: `LLMScorer.score(call) -> ScoreResult`, `get_scorer() -> Scorer`
  (reads `SCORER_BACKEND` env var, `"llm"` or default `"rule"`). Task 8's
  `seed.py` calls `get_scorer()`.

- [ ] **Step 1: Write the failing tests**

```python
# apps/api/tests/test_scorer_factory.py
from app.scoring.factory import get_scorer
from app.scoring.llm_scorer import LLMScorer
from app.scoring.models import CallTranscript, Turn
from app.scoring.rule_based import RuleBasedScorer


def test_get_scorer_defaults_to_rule_based(monkeypatch):
    monkeypatch.delenv("SCORER_BACKEND", raising=False)
    scorer = get_scorer()
    assert isinstance(scorer, RuleBasedScorer)


def test_get_scorer_returns_llm_scorer_when_configured(monkeypatch):
    monkeypatch.setenv("SCORER_BACKEND", "llm")
    scorer = get_scorer()
    assert isinstance(scorer, LLMScorer)


def test_llm_scorer_falls_back_to_rule_based_without_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    call = CallTranscript(
        call_id="hs-0001",
        rep_id="rep-01",
        vertical="home_services",
        turns=[Turn(speaker="rep", start=0, end=2, text="hello there")],
    )
    result = LLMScorer().score(call)
    assert result is not None
    assert 0 <= result.overall_score <= 100
```

- [ ] **Step 2: Run tests to verify they fail**

Run (from `apps/api`): `python -m pytest tests/test_scorer_factory.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.scoring.llm_scorer'`

- [ ] **Step 3: Write the implementation**

```python
# apps/api/app/scoring/llm_scorer.py
from __future__ import annotations

import os

from app.scoring.models import CallTranscript, ScoreResult
from app.scoring.rule_based import RuleBasedScorer


class LLMScorer:
    """Structurally-complete stub showing how an LLM-backed scorer plugs into
    the same interface as RuleBasedScorer. Not wired to a live API key by
    default - see docs/02-requirements.md for why a live LLM dependency is
    out of scope for the core exercise. Falls back to RuleBasedScorer if no
    API key is configured, so selecting this backend never breaks the app.
    """

    def __init__(self) -> None:
        self._fallback = RuleBasedScorer()

    def score(self, call: CallTranscript) -> ScoreResult:
        api_key = os.environ.get("LLM_API_KEY")
        if not api_key:
            return self._fallback.score(call)
        # A real implementation would serialize call.turns into a prompt,
        # call the LLM provider, and parse a structured ScoreResult back out.
        # Left as a stub: the exercise scope excludes a live LLM dependency.
        return self._fallback.score(call)
```

```python
# apps/api/app/scoring/factory.py
from __future__ import annotations

import os

from app.scoring.llm_scorer import LLMScorer
from app.scoring.rule_based import RuleBasedScorer


def get_scorer():
    backend = os.environ.get("SCORER_BACKEND", "rule").lower()
    if backend == "llm":
        return LLMScorer()
    return RuleBasedScorer()
```

- [ ] **Step 4: Run tests to verify they pass**

Run (from `apps/api`): `python -m pytest tests/test_scorer_factory.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/scoring/llm_scorer.py apps/api/app/scoring/factory.py apps/api/tests/test_scorer_factory.py
git commit -m "feat(api): add pluggable LLMScorer stub and scorer factory"
```

---

### Task 8: SQLAlchemy models and transcript seeding

**Files:**
- Create: `apps/api/app/db.py`
- Create: `apps/api/app/models_db.py`
- Create: `apps/api/app/seed.py`
- Create: `apps/api/tests/fixtures/transcripts/hs-0001.json`
- Create: `apps/api/tests/fixtures/transcripts/hs-0002.json`
- Create: `apps/api/tests/test_seed.py`

**Interfaces:**
- Consumes: `get_scorer()` from Task 7; the JSON schema produced by Task 1's
  generator.
- Produces: `RepDB`, `CallDB`, `ScoreDB` (SQLAlchemy models), `Base`, `engine`,
  `SessionLocal` from `app.db`, and `seed_database(db: Session, directory:
  Path = TRANSCRIPTS_DIR) -> int`. Task 9's routes and Task 5's `main.py`
  startup hook use all of these exact names.

- [ ] **Step 1: Write the test fixtures**

```json
// apps/api/tests/fixtures/transcripts/hs-0001.json
{
  "call_id": "hs-0001",
  "vertical": "home_services",
  "rep_id": "rep-01",
  "rep_name": "Jordan Blake",
  "customer_name": "Pat Romero",
  "date": "2026-05-02",
  "duration_seconds": 19,
  "turns": [
    {"speaker": "rep", "start": 0, "end": 3, "text": "Thanks for having me out today."},
    {"speaker": "customer", "start": 3, "end": 6, "text": "Sure, happy to walk through it."},
    {"speaker": "rep", "start": 6, "end": 9, "text": "The total price for this would be $4,200."},
    {"speaker": "customer", "start": 9, "end": 12, "text": "That feels too expensive honestly."},
    {"speaker": "rep", "start": 12, "end": 15, "text": "Totally fair, let's break down what's included and financing options."},
    {"speaker": "rep", "start": 15, "end": 17, "text": "Let's schedule this for next week."},
    {"speaker": "customer", "start": 17, "end": 19, "text": "Sounds good, let's do it."}
  ]
}
```

```json
// apps/api/tests/fixtures/transcripts/hs-0002.json
{
  "call_id": "hs-0002",
  "vertical": "home_services",
  "rep_id": "rep-01",
  "rep_name": "Jordan Blake",
  "customer_name": "Sam Osei",
  "date": "2026-05-03",
  "duration_seconds": 11,
  "turns": [
    {"speaker": "rep", "start": 0, "end": 5, "text": "Here's the system and here's the total cost, $6,800."},
    {"speaker": "customer", "start": 5, "end": 8, "text": "That's too expensive, we'll need to think about it."},
    {"speaker": "rep", "start": 8, "end": 10, "text": "Okay well the price is the price."},
    {"speaker": "customer", "start": 10, "end": 11, "text": "We'll see."}
  ]
}
```

- [ ] **Step 2: Write the failing tests**

```python
# apps/api/tests/test_seed.py
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models_db import CallDB, RepDB, ScoreDB
from app.seed import seed_database

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "transcripts"


def _make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_seed_database_loads_reps_calls_and_scores():
    db = _make_session()
    count = seed_database(db, directory=FIXTURE_DIR)

    assert count == 2
    assert db.query(RepDB).count() == 1
    assert db.query(CallDB).count() == 2
    assert db.query(ScoreDB).count() == 2


def test_seed_database_is_idempotent():
    db = _make_session()
    seed_database(db, directory=FIXTURE_DIR)
    second_count = seed_database(db, directory=FIXTURE_DIR)

    assert second_count == 0
    assert db.query(CallDB).count() == 2
```

- [ ] **Step 3: Run tests to verify they fail**

Run (from `apps/api`): `python -m pytest tests/test_seed.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.db'`

- [ ] **Step 4: Write the implementation**

```python
# apps/api/app/db.py
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./coaching_insights.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

```python
# apps/api/app/models_db.py
from __future__ import annotations

from sqlalchemy import Boolean, Column, Float, ForeignKey, JSON, String
from sqlalchemy.orm import relationship

from app.db import Base


class RepDB(Base):
    __tablename__ = "reps"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    vertical = Column(String, nullable=False)

    calls = relationship("CallDB", back_populates="rep")


class CallDB(Base):
    __tablename__ = "calls"

    id = Column(String, primary_key=True)
    rep_id = Column(String, ForeignKey("reps.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    vertical = Column(String, nullable=False)
    date = Column(String, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    turns = Column(JSON, nullable=False)

    rep = relationship("RepDB", back_populates="calls")
    score = relationship("ScoreDB", back_populates="call", uselist=False)


class ScoreDB(Base):
    __tablename__ = "scores"

    call_id = Column(String, ForeignKey("calls.id"), primary_key=True)
    talk_listen_ratio = Column(Float, nullable=False)
    objection_raised = Column(Boolean, nullable=False)
    objection_handled_well = Column(Boolean, nullable=False)
    pricing_discussed = Column(Boolean, nullable=False)
    next_step_committed = Column(Boolean, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    flags = Column(JSON, nullable=False)

    call = relationship("CallDB", back_populates="score")
```

```python
# apps/api/app/seed.py
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models_db import CallDB, RepDB, ScoreDB
from app.scoring.factory import get_scorer
from app.scoring.models import CallTranscript, Turn

TRANSCRIPTS_DIR = Path(__file__).resolve().parents[3] / "data" / "transcripts"


def load_transcripts(directory: Path = TRANSCRIPTS_DIR) -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(directory.glob("*.json"))]


def seed_database(db: Session, directory: Path = TRANSCRIPTS_DIR) -> int:
    if db.query(RepDB).first() is not None:
        return 0  # already seeded

    scorer = get_scorer()
    count = 0
    for raw in load_transcripts(directory):
        if db.get(RepDB, raw["rep_id"]) is None:
            db.add(RepDB(id=raw["rep_id"], name=raw["rep_name"], vertical=raw["vertical"]))

        transcript = CallTranscript(
            call_id=raw["call_id"],
            rep_id=raw["rep_id"],
            vertical=raw["vertical"],
            turns=[Turn(**t) for t in raw["turns"]],
        )
        result = scorer.score(transcript)

        db.add(
            CallDB(
                id=raw["call_id"],
                rep_id=raw["rep_id"],
                customer_name=raw["customer_name"],
                vertical=raw["vertical"],
                date=raw["date"],
                duration_seconds=raw["duration_seconds"],
                turns=raw["turns"],
            )
        )
        db.add(
            ScoreDB(
                call_id=raw["call_id"],
                talk_listen_ratio=result.talk_listen_ratio,
                objection_raised=result.objection_raised,
                objection_handled_well=result.objection_handled_well,
                pricing_discussed=result.pricing_discussed,
                next_step_committed=result.next_step_committed,
                sentiment_score=result.sentiment_score,
                overall_score=result.overall_score,
                flags=result.flags,
            )
        )
        count += 1

    db.commit()
    return count
```

Note: `TRANSCRIPTS_DIR` resolves `apps/api/app/seed.py` -> `parents[3]` ->
repo root, then `data/transcripts`. Verify this resolves correctly for your
checkout (adjust the index if the directory nesting differs).

- [ ] **Step 5: Run tests to verify they pass**

Run (from `apps/api`): `python -m pytest tests/test_seed.py -v`
Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/db.py apps/api/app/models_db.py apps/api/app/seed.py apps/api/tests/fixtures apps/api/tests/test_seed.py
git commit -m "feat(api): add SQLAlchemy models and transcript seeding"
```

---

### Task 9: REST API endpoints

**Files:**
- Create: `apps/api/app/schemas.py`
- Create: `apps/api/app/routes.py`
- Modify: `apps/api/app/main.py` (wire router + startup seeding)
- Create: `apps/api/tests/test_api_routes.py`

**Interfaces:**
- Consumes: `RepDB`, `CallDB`, `SessionLocal`, `Base`, `engine` (Task 8);
  `seed_database` (Task 8).
- Produces: the live API described in `design/architecture.md`'s API
  Reference table. Task 10's `lib/api.ts` types must match these response
  shapes exactly.

- [ ] **Step 1: Write the failing tests**

```python
# apps/api/tests/test_api_routes.py
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.main import app
from app.routes import get_db
from app.seed import seed_database

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "transcripts"


def _build_test_session_factory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    seed_database(session, directory=FIXTURE_DIR)
    session.close()
    return Session


TestSession = _build_test_session_factory()


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_list_reps_returns_seeded_rep_with_average_score():
    response = client.get("/api/reps")
    assert response.status_code == 200
    reps = response.json()
    assert len(reps) == 1
    assert reps[0]["id"] == "rep-01"
    assert reps[0]["call_count"] == 2


def test_get_call_detail_returns_transcript_and_score():
    response = client.get("/api/calls/hs-0001")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "hs-0001"
    assert body["score"]["objection_handled_well"] is True


def test_get_call_detail_404_for_unknown_call():
    response = client.get("/api/calls/does-not-exist")
    assert response.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

Run (from `apps/api`): `python -m pytest tests/test_api_routes.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.routes'`

- [ ] **Step 3: Write the implementation**

```python
# apps/api/app/schemas.py
from __future__ import annotations

from pydantic import BaseModel


class ScoreOut(BaseModel):
    talk_listen_ratio: float
    objection_raised: bool
    objection_handled_well: bool
    pricing_discussed: bool
    next_step_committed: bool
    sentiment_score: float
    overall_score: float
    flags: list[str]

    class Config:
        from_attributes = True


class CallSummaryOut(BaseModel):
    id: str
    rep_id: str
    customer_name: str
    vertical: str
    date: str
    overall_score: float


class CallDetailOut(BaseModel):
    id: str
    rep_id: str
    customer_name: str
    vertical: str
    date: str
    duration_seconds: float
    turns: list[dict]
    score: ScoreOut


class RepSummaryOut(BaseModel):
    id: str
    name: str
    vertical: str
    call_count: int
    average_score: float


class RepDetailOut(BaseModel):
    id: str
    name: str
    vertical: str
    calls: list[CallSummaryOut]
```

```python
# apps/api/app/routes.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models_db import CallDB, RepDB
from app.schemas import CallDetailOut, CallSummaryOut, RepDetailOut, RepSummaryOut, ScoreOut

router = APIRouter(prefix="/api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/reps", response_model=list[RepSummaryOut])
def list_reps(db: Session = Depends(get_db)):
    reps = db.query(RepDB).all()
    out = []
    for rep in reps:
        scores = [c.score.overall_score for c in rep.calls if c.score]
        avg = round(sum(scores) / len(scores), 1) if scores else 0.0
        out.append(
            RepSummaryOut(id=rep.id, name=rep.name, vertical=rep.vertical, call_count=len(rep.calls), average_score=avg)
        )
    return out


@router.get("/reps/{rep_id}", response_model=RepDetailOut)
def get_rep(rep_id: str, db: Session = Depends(get_db)):
    rep = db.get(RepDB, rep_id)
    if rep is None:
        raise HTTPException(status_code=404, detail="Rep not found")
    calls = [
        CallSummaryOut(
            id=c.id, rep_id=c.rep_id, customer_name=c.customer_name,
            vertical=c.vertical, date=c.date, overall_score=c.score.overall_score if c.score else 0.0,
        )
        for c in sorted(rep.calls, key=lambda c: c.date)
    ]
    return RepDetailOut(id=rep.id, name=rep.name, vertical=rep.vertical, calls=calls)


@router.get("/calls", response_model=list[CallSummaryOut])
def list_calls(db: Session = Depends(get_db)):
    calls = db.query(CallDB).all()
    return [
        CallSummaryOut(
            id=c.id, rep_id=c.rep_id, customer_name=c.customer_name,
            vertical=c.vertical, date=c.date, overall_score=c.score.overall_score if c.score else 0.0,
        )
        for c in calls
    ]


@router.get("/calls/{call_id}", response_model=CallDetailOut)
def get_call(call_id: str, db: Session = Depends(get_db)):
    call = db.get(CallDB, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    return CallDetailOut(
        id=call.id, rep_id=call.rep_id, customer_name=call.customer_name,
        vertical=call.vertical, date=call.date, duration_seconds=call.duration_seconds,
        turns=call.turns, score=ScoreOut.model_validate(call.score),
    )
```

```python
# apps/api/app/main.py
from fastapi import FastAPI

from app.db import Base, SessionLocal, engine
from app.routes import router
from app.seed import seed_database

app = FastAPI(title="Rilla Coaching Insights API")
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 4: Run tests to verify they pass**

Run (from `apps/api`): `python -m pytest tests -v`
Expected: all tests pass (health, rule-based scorer, factory, seed, routes)

- [ ] **Step 5: Manually verify the running server**

```bash
uvicorn app.main:app --reload --port 8000
```

In another terminal: `curl http://localhost:8000/api/reps` should return
JSON for the 6 seeded reps once `data/transcripts/` (Task 1) is present.
Stop the server with Ctrl+C.

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/schemas.py apps/api/app/routes.py apps/api/app/main.py apps/api/tests/test_api_routes.py
git commit -m "feat(api): add REST endpoints for reps and calls"
```

---

## Phase 3 — Frontend Reference Implementation (`apps/web`, `solution` branch)

### Task 10: Next.js scaffold and typed API client

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/next.config.mjs`
- Create: `apps/web/.gitignore`
- Create: `apps/web/vitest.config.ts`
- Create: `apps/web/lib/types.ts`
- Create: `apps/web/lib/api.ts`
- Create: `apps/web/lib/api.test.ts`
- Create: `apps/web/app/layout.tsx`

**Interfaces:**
- Consumes: the API response shapes from Task 9.
- Produces: `RepSummary`, `RepDetail`, `CallSummary`, `CallDetail`,
  `ScoreOut` TypeScript types; `fetchReps()`, `fetchRep(repId)`,
  `fetchCalls()`, `fetchCall(callId)`. Tasks 11-13's pages and components
  import these exact names.

- [ ] **Step 1: Scaffold config files**

```json
// apps/web/package.json
{
  "name": "coaching-insights-web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "test": "vitest run"
  },
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "recharts": "^2.12.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "@types/node": "^20.11.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "vitest": "^1.5.0",
    "@testing-library/react": "^15.0.0",
    "@testing-library/jest-dom": "^6.4.0",
    "jsdom": "^24.0.0"
  }
}
```

```json
// apps/web/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

```javascript
// apps/web/next.config.mjs
/** @type {import('next').NextConfig} */
const nextConfig = {};
export default nextConfig;
```

```
# apps/web/.gitignore
node_modules/
.next/
next-env.d.ts
```

```typescript
// apps/web/vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
  },
});
```

```tsx
// apps/web/app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 2: Write the failing test**

```typescript
// apps/web/lib/api.test.ts
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchReps } from "./api";

describe("fetchReps", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("returns parsed rep list on success", async () => {
    const mockReps = [
      { id: "rep-01", name: "Jordan Blake", vertical: "home_services", call_count: 4, average_score: 82.5 },
    ];
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockReps,
    }) as unknown as typeof fetch;

    const result = await fetchReps();

    expect(result).toEqual(mockReps);
    expect(fetch).toHaveBeenCalledWith("http://localhost:8000/api/reps", { cache: "no-store" });
  });

  it("throws when the response is not ok", async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, status: 500 }) as unknown as typeof fetch;

    await expect(fetchReps()).rejects.toThrow("Request to /api/reps failed with status 500");
  });
});
```

- [ ] **Step 3: Install dependencies and run test to verify it fails**

Run (from `apps/web`): `npm install`
Run: `npm test`
Expected: FAIL — `./api` has no exported member `fetchReps` (module doesn't exist yet)

- [ ] **Step 4: Write the implementation**

```typescript
// apps/web/lib/types.ts
export interface ScoreOut {
  talk_listen_ratio: number;
  objection_raised: boolean;
  objection_handled_well: boolean;
  pricing_discussed: boolean;
  next_step_committed: boolean;
  sentiment_score: number;
  overall_score: number;
  flags: string[];
}

export interface CallSummary {
  id: string;
  rep_id: string;
  customer_name: string;
  vertical: string;
  date: string;
  overall_score: number;
}

export interface CallDetail extends Omit<CallSummary, "overall_score"> {
  duration_seconds: number;
  turns: { speaker: string; start: number; end: number; text: string }[];
  score: ScoreOut;
}

export interface RepSummary {
  id: string;
  name: string;
  vertical: string;
  call_count: number;
  average_score: number;
}

export interface RepDetail {
  id: string;
  name: string;
  vertical: string;
  calls: CallSummary[];
}
```

```typescript
// apps/web/lib/api.ts
import type { CallDetail, CallSummary, RepDetail, RepSummary } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchReps(): Promise<RepSummary[]> {
  return getJson<RepSummary[]>("/api/reps");
}

export function fetchRep(repId: string): Promise<RepDetail> {
  return getJson<RepDetail>(`/api/reps/${repId}`);
}

export function fetchCalls(): Promise<CallSummary[]> {
  return getJson<CallSummary[]>("/api/calls");
}

export function fetchCall(callId: string): Promise<CallDetail> {
  return getJson<CallDetail>(`/api/calls/${callId}`);
}
```

- [ ] **Step 5: Run test to verify it passes**

Run (from `apps/web`): `npm test`
Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add apps/web/package.json apps/web/tsconfig.json apps/web/next.config.mjs apps/web/.gitignore apps/web/vitest.config.ts apps/web/lib apps/web/app/layout.tsx
git commit -m "feat(web): scaffold Next.js app with typed API client"
```

---

### Task 11: Dashboard/leaderboard page

**Files:**
- Create: `apps/web/components/RepLeaderboardTable.tsx`
- Create: `apps/web/components/RepLeaderboardTable.test.tsx`
- Create: `apps/web/app/page.tsx`

**Interfaces:**
- Consumes: `RepSummary` (Task 10), `fetchReps()` (Task 10).
- Produces: `RepLeaderboardTable({ reps: RepSummary[] })` component, used
  standalone here and importable by any later page.

- [ ] **Step 1: Write the failing test**

```tsx
// apps/web/components/RepLeaderboardTable.test.tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RepLeaderboardTable } from "./RepLeaderboardTable";

describe("RepLeaderboardTable", () => {
  it("sorts reps by average score descending", () => {
    render(
      <RepLeaderboardTable
        reps={[
          { id: "rep-01", name: "Jordan Blake", vertical: "home_services", call_count: 4, average_score: 70 },
          { id: "rep-02", name: "Casey Nguyen", vertical: "home_services", call_count: 5, average_score: 90 },
        ]}
      />
    );

    const rows = screen.getAllByRole("row");
    expect(rows[1]).toHaveTextContent("Casey Nguyen");
    expect(rows[2]).toHaveTextContent("Jordan Blake");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run (from `apps/web`): `npm test`
Expected: FAIL — cannot find module `./RepLeaderboardTable`

- [ ] **Step 3: Write the implementation**

```tsx
// apps/web/components/RepLeaderboardTable.tsx
import type { RepSummary } from "../lib/types";

export function RepLeaderboardTable({ reps }: { reps: RepSummary[] }) {
  const sorted = [...reps].sort((a, b) => b.average_score - a.average_score);
  return (
    <table>
      <thead>
        <tr>
          <th>Rep</th>
          <th>Vertical</th>
          <th>Calls</th>
          <th>Avg Score</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map((rep) => (
          <tr key={rep.id}>
            <td>{rep.name}</td>
            <td>{rep.vertical}</td>
            <td>{rep.call_count}</td>
            <td>{rep.average_score.toFixed(1)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

```tsx
// apps/web/app/page.tsx
import { fetchReps } from "../lib/api";
import { RepLeaderboardTable } from "../components/RepLeaderboardTable";

export default async function DashboardPage() {
  const reps = await fetchReps();
  return (
    <main>
      <h1>Rep Leaderboard</h1>
      <RepLeaderboardTable reps={reps} />
    </main>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run (from `apps/web`): `npm test`
Expected: 3 passed (2 from Task 10 + 1 new)

- [ ] **Step 5: Commit**

```bash
git add apps/web/components/RepLeaderboardTable.tsx apps/web/components/RepLeaderboardTable.test.tsx apps/web/app/page.tsx
git commit -m "feat(web): add rep leaderboard dashboard page"
```

---

### Task 12: Call detail page

**Files:**
- Create: `apps/web/components/ScoreCard.tsx`
- Create: `apps/web/components/ScoreCard.test.tsx`
- Create: `apps/web/app/calls/[callId]/page.tsx`

**Interfaces:**
- Consumes: `ScoreOut`, `CallDetail` (Task 10), `fetchCall(callId)` (Task 10).
- Produces: `ScoreCard({ score: ScoreOut })` component.

- [ ] **Step 1: Write the failing test**

```tsx
// apps/web/components/ScoreCard.test.tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScoreCard } from "./ScoreCard";

describe("ScoreCard", () => {
  it("renders coaching flags when present", () => {
    render(
      <ScoreCard
        score={{
          talk_listen_ratio: 3.1,
          objection_raised: true,
          objection_handled_well: false,
          pricing_discussed: true,
          next_step_committed: false,
          sentiment_score: -0.2,
          overall_score: 45.2,
          flags: ["objection_not_handled", "no_next_step_commitment"],
        }}
      />
    );

    expect(screen.getByLabelText("coaching-flags")).toHaveTextContent("objection_not_handled");
    expect(screen.getByText("Overall score: 45.2")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run (from `apps/web`): `npm test`
Expected: FAIL — cannot find module `./ScoreCard`

- [ ] **Step 3: Write the implementation**

```tsx
// apps/web/components/ScoreCard.tsx
import type { ScoreOut } from "../lib/types";

export function ScoreCard({ score }: { score: ScoreOut }) {
  return (
    <section aria-label="scorecard">
      <p>Overall score: {score.overall_score.toFixed(1)}</p>
      <p>Talk/listen ratio: {score.talk_listen_ratio.toFixed(2)}</p>
      <p>Pricing discussed: {score.pricing_discussed ? "Yes" : "No"}</p>
      <p>Objection handled well: {score.objection_handled_well ? "Yes" : "No"}</p>
      <p>Next step committed: {score.next_step_committed ? "Yes" : "No"}</p>
      {score.flags.length > 0 && (
        <ul aria-label="coaching-flags">
          {score.flags.map((flag) => (
            <li key={flag}>{flag}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
```

```tsx
// apps/web/app/calls/[callId]/page.tsx
import { fetchCall } from "../../../lib/api";
import { ScoreCard } from "../../../components/ScoreCard";

export default async function CallDetailPage({ params }: { params: { callId: string } }) {
  const call = await fetchCall(params.callId);
  return (
    <main>
      <h1>Call {call.id} - {call.customer_name}</h1>
      <ScoreCard score={call.score} />
      <ol aria-label="transcript">
        {call.turns.map((turn, index) => (
          <li key={index}>
            <strong>{turn.speaker}:</strong> {turn.text}
          </li>
        ))}
      </ol>
    </main>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run (from `apps/web`): `npm test`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add apps/web/components/ScoreCard.tsx apps/web/components/ScoreCard.test.tsx apps/web/app/calls
git commit -m "feat(web): add call detail page with scorecard"
```

---

### Task 13: Rep profile and trend chart page

**Files:**
- Create: `apps/web/components/RepTrendChart.tsx`
- Create: `apps/web/components/RepTrendChart.test.tsx`
- Create: `apps/web/app/reps/[repId]/page.tsx`

**Interfaces:**
- Consumes: `CallSummary` (Task 10), `RepDetail`, `fetchRep(repId)` (Task 10).
- Produces: `RepTrendChart({ calls: CallSummary[] })` component.

- [ ] **Step 1: Write the failing test**

```tsx
// apps/web/components/RepTrendChart.test.tsx
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RepTrendChart } from "./RepTrendChart";

describe("RepTrendChart", () => {
  it("renders an svg chart without crashing", () => {
    const { container } = render(
      <RepTrendChart
        calls={[
          { id: "hs-0001", rep_id: "rep-01", customer_name: "Pat", vertical: "home_services", date: "2026-05-02", overall_score: 60 },
          { id: "hs-0002", rep_id: "rep-01", customer_name: "Sam", vertical: "home_services", date: "2026-05-05", overall_score: 80 },
        ]}
      />
    );

    expect(container.querySelector("svg")).not.toBeNull();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run (from `apps/web`): `npm test`
Expected: FAIL — cannot find module `./RepTrendChart`

- [ ] **Step 3: Write the implementation**

```tsx
// apps/web/components/RepTrendChart.tsx
"use client";

import { CartesianGrid, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";
import type { CallSummary } from "../lib/types";

export function RepTrendChart({ calls }: { calls: CallSummary[] }) {
  const data = [...calls]
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((call) => ({ date: call.date, score: call.overall_score }));

  return (
    <LineChart width={600} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis domain={[0, 100]} />
      <Tooltip />
      <Line type="monotone" dataKey="score" stroke="#2563eb" />
    </LineChart>
  );
}
```

```tsx
// apps/web/app/reps/[repId]/page.tsx
import { fetchRep } from "../../../lib/api";
import { RepTrendChart } from "../../../components/RepTrendChart";

export default async function RepProfilePage({ params }: { params: { repId: string } }) {
  const rep = await fetchRep(params.repId);
  return (
    <main>
      <h1>{rep.name}</h1>
      <p>Vertical: {rep.vertical}</p>
      <RepTrendChart calls={rep.calls} />
    </main>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run (from `apps/web`): `npm test`
Expected: 5 passed

- [ ] **Step 5: Manually verify the full stack**

With the backend running (`uvicorn app.main:app --reload --port 8000` from
`apps/api`), in another terminal from `apps/web`: `npm run dev`, then open
`http://localhost:3000` and click through to a call and a rep profile.

- [ ] **Step 6: Commit**

```bash
git add apps/web/components/RepTrendChart.tsx apps/web/components/RepTrendChart.test.tsx apps/web/app/reps
git commit -m "feat(web): add rep profile page with trend chart"
```

---

## Phase 4 — Presentation Deck (`solution` branch)

### Task 14: Marp presentation deck

**Files:**
- Create: `presentation/slides.md`

**Interfaces:**
- Consumes: `design/architecture.md` and `design/diagrams/*.mmd` (Tasks 3-4).
- Produces: nothing consumed by later tasks — this is the final deliverable
  artifact for Part 3 of the on-site.

- [ ] **Step 1: Export diagram PNGs for embedding**

```bash
npx -y @mermaid-js/mermaid-cli -i design/diagrams/mvp-architecture.mmd -o design/diagrams/mvp-architecture.png
npx -y @mermaid-js/mermaid-cli -i design/diagrams/production-architecture.mmd -o design/diagrams/production-architecture.png
```

- [ ] **Step 2: Write `presentation/slides.md`**

```markdown
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
```

- [ ] **Step 3: Render the deck to verify it builds**

```bash
npx -y @marp-team/marp-cli presentation/slides.md -o presentation/slides.pdf
```

Expected: `presentation/slides.pdf` is created without errors.

- [ ] **Step 4: Commit**

```bash
git add design/diagrams/*.png presentation/slides.md presentation/slides.pdf
git commit -m "docs: add reference presentation deck"
```

---

## Phase 5 — Polish & Rehearsal Pass (`solution` branch, then push)

### Task 15: End-to-end rehearsal checklist and doc finalization

**Files:**
- Create: `docs/03-rehearsal-checklist.md`
- Modify: `README.md` (add a "Reference solution" section)
- Modify: `CHANGELOG.md`

**Interfaces:** none — documentation only.

- [ ] **Step 1: Write `docs/03-rehearsal-checklist.md`**

```markdown
# Rehearsal Dry-Run Checklist

Run through this once, end to end, timing yourself, before the real on-site.

- [ ] Cold-read `docs/01-problem-statement.md` and `docs/02-requirements.md`
      in under 10 minutes, as if at kickoff.
- [ ] Start a 4-hour timer. Build your own version on a local branch.
- [ ] Backend: `cd apps/api && pip install -r requirements.txt && python -m pytest tests -v`
      all pass.
- [ ] Backend runs: `uvicorn app.main:app --reload --port 8000`,
      `curl http://localhost:8000/api/reps` returns data.
- [ ] Frontend: `cd apps/web && npm install && npm test` all pass.
- [ ] Frontend runs: `npm run dev`, dashboard/call/rep pages load and link
      to each other correctly at `http://localhost:3000`.
- [ ] Draft your own 5-8 slide presentation in the last hour.
- [ ] Compare: `git fetch origin && git diff main origin/solution -- design/ apps/`
      - note what you did differently and why.
- [ ] Rehearse answering: "how would this look at 100x the customers and
      calls?" out loud, in under 3 minutes.
```

- [ ] **Step 2: Add a "Reference Solution" section to `README.md`**

```markdown

## Reference Solution (on the `solution` branch)

`git fetch origin && git checkout solution` to see:
- `design/architecture.md` + `design/diagrams/` - full system design
- `apps/api` - FastAPI backend, `apps/web` - Next.js/TS frontend
- `presentation/slides.md` - a reference Marp deck

Try `docs/03-rehearsal-checklist.md` for a full timed dry run.
```

- [ ] **Step 3: Update `CHANGELOG.md`**

```markdown

## [0.1.0] - 2026-07-03

### Added
- Reference system design (`design/architecture.md` + diagrams).
- Reference FastAPI backend with pluggable Scorer strategy.
- Reference Next.js/TypeScript frontend (dashboard, call detail, rep profile).
- Reference Marp presentation deck.
- Rehearsal dry-run checklist.
```

- [ ] **Step 4: Commit**

```bash
git add docs/03-rehearsal-checklist.md README.md CHANGELOG.md
git commit -m "docs: add rehearsal checklist and finalize solution branch docs"
```

---

### Task 16: Push branches to GitHub

**Files:** none — git operations only.

- [ ] **Step 1: Confirm with the user before pushing**

Stop and ask the user to confirm before running any push — this publishes
the repo to `https://github.com/MikeQin/sd-prep`, which is a visible,
shared-state action per this project's operating rules.

- [ ] **Step 2: Push `main`**

```bash
git checkout main
git push -u origin main
```

- [ ] **Step 3: Push `solution`**

```bash
git checkout solution
git push -u origin solution
```

- [ ] **Step 4: Verify on GitHub**

Open `https://github.com/MikeQin/sd-prep` and confirm both branches are
present, `main` shows only docs/data, and `solution` shows the full
reference implementation.
