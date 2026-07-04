from __future__ import annotations

import os

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
        api_key = os.environ.get("LLM_API_KEY")
        if not api_key:
            return self._fallback.score(call)
        # A real implementation would serialize call.turns into a prompt,
        # call the LLM provider, and parse a structured ScoreResult back out.
        # Left as a stub: the exercise scope excludes a live LLM dependency.
        return self._fallback.score(call)
