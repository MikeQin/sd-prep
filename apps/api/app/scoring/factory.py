from __future__ import annotations

import os

from app.scoring.llm_scorer import LLMScorer
from app.scoring.rule_based import RuleBasedScorer


def get_scorer():
    backend = os.environ.get("SCORER_BACKEND", "rule").lower()
    if backend == "llm":
        return LLMScorer()
    return RuleBasedScorer()
