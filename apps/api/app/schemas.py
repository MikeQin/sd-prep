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
