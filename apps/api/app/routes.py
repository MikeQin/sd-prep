from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db import session_scope
from app.models_db import CallDB, RepDB
from app.schemas import CallDetailOut, CallSummaryOut, RepDetailOut, RepSummaryOut, ScoreOut

router = APIRouter(prefix="/api")


def get_db():
    with session_scope() as db:
        yield db


def _to_call_summary(call: CallDB) -> CallSummaryOut:
    return CallSummaryOut(
        id=call.id, rep_id=call.rep_id, customer_name=call.customer_name,
        vertical=call.vertical, date=call.date,
        overall_score=call.score.overall_score if call.score else 0.0,
    )


@router.get("/reps", response_model=list[RepSummaryOut])
def list_reps(db: Session = Depends(get_db)):
    reps = db.query(RepDB).options(selectinload(RepDB.calls).selectinload(CallDB.score)).all()
    out = []
    for rep in reps:
        scores = [c.score.overall_score for c in rep.calls if c.score]
        avg = round(sum(scores) / len(scores), 1) if scores else 0.0
        out.append(
            RepSummaryOut(
                id=rep.id, name=rep.name, vertical=rep.vertical,
                call_count=len(rep.calls), scored_call_count=len(scores), average_score=avg,
            )
        )
    return out


@router.get("/reps/{rep_id}", response_model=RepDetailOut)
def get_rep(rep_id: str, db: Session = Depends(get_db)):
    rep = db.get(
        RepDB, rep_id, options=[selectinload(RepDB.calls).selectinload(CallDB.score)]
    )
    if rep is None:
        raise HTTPException(status_code=404, detail="Rep not found")
    calls = [_to_call_summary(c) for c in sorted(rep.calls, key=lambda c: c.date)]
    return RepDetailOut(id=rep.id, name=rep.name, vertical=rep.vertical, calls=calls)


@router.get("/calls", response_model=list[CallSummaryOut])
def list_calls(db: Session = Depends(get_db)):
    calls = db.query(CallDB).options(joinedload(CallDB.score)).all()
    return [_to_call_summary(c) for c in calls]


@router.get("/calls/{call_id}", response_model=CallDetailOut)
def get_call(call_id: str, db: Session = Depends(get_db)):
    call = db.get(CallDB, call_id, options=[joinedload(CallDB.score)])
    if call is None:
        raise HTTPException(status_code=404, detail="Call not found")
    if call.score is None:
        raise HTTPException(status_code=500, detail=f"Call {call_id} has no score")
    return CallDetailOut(
        id=call.id, rep_id=call.rep_id, customer_name=call.customer_name,
        vertical=call.vertical, date=call.date, duration_seconds=call.duration_seconds,
        turns=call.turns, score=ScoreOut.model_validate(call.score),
    )
