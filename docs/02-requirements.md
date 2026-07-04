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
