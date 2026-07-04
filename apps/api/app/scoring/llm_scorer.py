from __future__ import annotations

from app.scoring.models import CallTranscript, ScoreResult
from app.scoring.rule_based import RuleBasedScorer


class LLMScorer:
    """Structurally-complete stub showing how an LLM-backed scorer plugs into
    the same interface as RuleBasedScorer. Not wired to a live API key by
    default - see docs/02-requirements.md for why a live LLM dependency is
    out of scope for the core exercise. Falls back to RuleBasedScorer if no
    API key is configured, so selecting this backend never breaks the app.
    """

    def __init__(self) -> None:
        self._fallback = RuleBasedScorer()

    def score(self, call: CallTranscript) -> ScoreResult:
        # A real implementation would check for LLM_API_KEY, serialize
        # call.turns into a prompt, call the LLM provider, and parse a
        # structured ScoreResult back out (with scored_by="llm"). Left as a
        # stub: the exercise scope excludes a live LLM dependency. The
        # fallback's own scored_by="rule" makes this substitution visible
        # to callers rather than silent.
        return self._fallback.score(call)
