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
    scored_by: str
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


class TurnOut(BaseModel):
    speaker: str
    start: float
    end: float
    text: str


class CallDetailOut(BaseModel):
    id: str
    rep_id: str
    customer_name: str
    vertical: str
    date: str
    duration_seconds: float
    turns: list[TurnOut]
    score: ScoreOut


class RepSummaryOut(BaseModel):
    id: str
    name: str
    vertical: str
    call_count: int
    # Separate from call_count so a caller can tell when average_score is
    # computed over fewer calls than call_count reports (e.g. a call whose
    # scoring hasn't completed yet), instead of the two numbers silently
    # resting on different denominators.
    scored_call_count: int
    average_score: float


class RepDetailOut(BaseModel):
    id: str
    name: str
    vertical: str
    calls: list[CallSummaryOut]
