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
    scored_by = Column(String, nullable=False)
    flags = Column(JSON, nullable=False)

    call = relationship("CallDB", back_populates="score")
