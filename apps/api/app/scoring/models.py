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
    # Which scorer actually produced this result ("rule" or "llm") - lets a
    # caller detect when LLMScorer silently fell back to RuleBasedScorer
    # instead of the substitution being invisible.
    scored_by: str
    flags: list[str] = field(default_factory=list)
