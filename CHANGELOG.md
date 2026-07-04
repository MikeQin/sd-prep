# Changelog

All notable changes to this rehearsal repo are documented here.

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
