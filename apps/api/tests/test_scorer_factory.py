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
