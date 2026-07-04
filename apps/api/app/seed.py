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
