import pytest

from app.scoring.factory import get_scorer
from app.scoring.llm_scorer import LLMScorer
from app.scoring.models import CallTranscript, Turn
from app.scoring.rule_based import RuleBasedScorer


def test_get_scorer_defaults_to_rule_based(monkeypatch):
    monkeypatch.delenv("SCORER_BACKEND", raising=False)
    scorer = get_scorer()
    assert isinstance(scorer, RuleBasedScorer)


def test_get_scorer_returns_llm_scorer_when_configured(monkeypatch):
    monkeypatch.setenv("SCORER_BACKEND", "llm")
    scorer = get_scorer()
    assert isinstance(scorer, LLMScorer)


def test_get_scorer_raises_on_unrecognized_backend(monkeypatch):
    monkeypatch.setenv("SCORER_BACKEND", "lmm")  # typo of "llm"
    with pytest.raises(ValueError, match="lmm"):
        get_scorer()


def test_llm_scorer_falls_back_to_rule_based_without_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    call = CallTranscript(
        call_id="hs-0001",
        rep_id="rep-01",
        vertical="home_services",
        turns=[Turn(speaker="rep", start=0, end=2, text="hello there")],
    )
    result = LLMScorer().score(call)
    assert result is not None
    assert 0 <= result.overall_score <= 100
    # The fallback must be visible in the result, not silent.
    assert result.scored_by == "rule"


def test_rule_based_scorer_reports_itself_as_the_backend():
    call = CallTranscript(
        call_id="hs-0001",
        rep_id="rep-01",
        vertical="home_services",
        turns=[Turn(speaker="rep", start=0, end=2, text="hello there")],
    )
    result = RuleBasedScorer().score(call)
    assert result.scored_by == "rule"
