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
    scorer = get_scorer()
    count = 0
    # Track rep ids we've already added in a local set rather than
    # re-querying via db.get() on every iteration: with autoflush disabled
    # (as app.db.SessionLocal is configured), db.get() doesn't see a rep
    # added earlier in this same loop until the session is flushed, so two
    # transcripts for the same not-yet-committed rep would each add a
    # duplicate RepDB row and blow up on commit with a UNIQUE violation.
    known_rep_ids = {rep.id for rep in db.query(RepDB).all()}
    for raw in load_transcripts(directory):
        if db.get(CallDB, raw["call_id"]) is not None:
            continue  # this call was already seeded in a previous run

        if raw["rep_id"] not in known_rep_ids:
            db.add(RepDB(id=raw["rep_id"], name=raw["rep_name"], vertical=raw["vertical"]))
            known_rep_ids.add(raw["rep_id"])

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
                scored_by=result.scored_by,
                flags=result.flags,
            )
        )
        count += 1

    db.commit()
    return count
