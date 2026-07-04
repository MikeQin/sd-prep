# Changelog

All notable changes to this rehearsal repo are documented here.

## [0.1.2] - 2026-07-04

### Fixed
- **`seed_database` could crash on startup against the real dataset** with
  `UNIQUE constraint failed: reps.id`. It checked `db.get(RepDB, rep_id) is
  None` to decide whether to add a rep, but `app.db.SessionLocal` has
  `autoflush=False`, so a rep added earlier in the same seeding pass wasn't
  visible to that check until the session flushed - every transcript after
  a rep's first one added a colliding duplicate row. Since every real rep
  has multiple calls, this broke seeding entirely outside of tests. Fixed
  by tracking already-added rep ids in a local set instead of re-querying
  mid-loop. The test suite had been silently missing this because its own
  session factories didn't match production's `autoflush=False` config -
  fixed those too so they actually exercise the real code path.
- `@app.on_event("startup")` migrated to FastAPI's `lifespan` context
  manager (`on_event` is deprecated).
- `ScoreOut`'s class-based `Config` migrated to `ConfigDict` (Pydantic
  v1-style config is deprecated in Pydantic v2).
- `httpx` swapped for `httpx2` in `apps/api/requirements.txt` -
  `starlette.testclient` now prefers `httpx2` and warns when falling back
  to `httpx`.

### Added
- A "Running the App" section in `README.md` (solution branch): backend/
  frontend setup and dev server commands, environment variables
  (`SCORER_BACKEND`, `LLM_API_KEY`, `NEXT_PUBLIC_API_BASE_URL`), resetting
  the SQLite db, and running tests. Verified by actually booting both
  servers end-to-end against the documented commands.

## [0.1.1] - 2026-07-04

### Fixed
- 20 issues found via an independent code review of the reference
  implementation - a scoring value that serialized as invalid JSON, zero
  navigation links anywhere in the frontend, keyword false-positives in the
  core scoring signal, an objection check not scoped to pricing per the
  actual requirements, N+1 queries in 3 routes, a silent scorer-backend
  fallback, all-or-nothing seed idempotency, and more - each fixed with a
  full TDD cycle (failing test, fix, passing test, commit).

### Changed
- Reference system design (`design/architecture.md` + diagrams) updated to
  address 7 design-level gaps found in the same review: ER cardinality
  corrected to match the schema, a `scorer_version` gap, API pagination,
  cache-aside + invalidation strategy, a replica-lag consistency tradeoff,
  queue processing idempotency, and a transcript retention/deletion policy.
- Reference presentation deck (`presentation/slides.md` / `.pdf`) synced
  with the fixes and design updates above.

### Added
- Calls-listing page and cross-page navigation in the reference frontend
  (dashboard, rep profile, and call detail now link to each other).
- `scored_by` field recording which scorer backend actually produced a
  given score, so a silent fallback is visible rather than indistinguishable
  from a real result.

## [0.1.0] - 2026-07-03

### Added
- Design spec for the Rilla on-site interview prep repo
  (`docs/superpowers/specs/2026-07-03-rilla-onsite-prep-design.md`).
- Reference system design (`design/architecture.md` + diagrams).
- Reference FastAPI backend with pluggable Scorer strategy.
- Reference Next.js/TypeScript frontend (dashboard, call detail, rep profile).
- Reference Marp presentation deck.
- Rehearsal dry-run checklist.
- Mock sales-call transcript generator and dataset (`data/`).
- Kickoff docs: interview overview, problem statement, requirements.
