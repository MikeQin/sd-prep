from app.scoring.models import CallTranscript, Turn
from app.scoring.rule_based import RuleBasedScorer


def _turn(speaker: str, text: str, start: float, end: float) -> Turn:
    return Turn(speaker=speaker, start=start, end=end, text=text)


def test_strong_call_scores_high_and_has_no_flags():
    call = CallTranscript(
        call_id="hs-0001",
        rep_id="rep-01",
        vertical="home_services",
        turns=[
            _turn("rep", "Thanks for having me out today, let's talk about your system.", 0, 3),
            _turn("customer", "Sure, happy to walk through it.", 3, 6),
            _turn("rep", "The total price for this would be $4,200.", 6, 9),
            _turn("customer", "That feels too expensive honestly.", 9, 12),
            _turn("rep", "Totally fair, let's break down what's included and financing options.", 12, 15),
            _turn("rep", "Let's schedule this for next week.", 15, 17),
            _turn("customer", "Sounds good, let's do it.", 17, 19),
        ],
    )

    result = RuleBasedScorer().score(call)

    assert result.pricing_discussed is True
    assert result.objection_raised is True
    assert result.objection_handled_well is True
    assert result.next_step_committed is True
    assert result.flags == []
    assert result.overall_score > 70


def test_weak_call_flags_unhandled_objection_and_no_commitment():
    call = CallTranscript(
        call_id="hs-0002",
        rep_id="rep-03",
        vertical="home_services",
        turns=[
            _turn("rep", "Here's the system and here's the total cost, $6,800.", 0, 5),
            _turn("customer", "That's too expensive, we'll need to think about it.", 5, 8),
            _turn("rep", "Okay well the price is the price.", 8, 10),
            _turn("customer", "We'll see.", 10, 11),
        ],
    )

    result = RuleBasedScorer().score(call)

    assert result.objection_raised is True
    assert result.objection_handled_well is False
    assert result.next_step_committed is False
    assert "objection_not_handled" in result.flags
    assert "no_next_step_commitment" in result.flags


def test_talk_listen_ratio_flags_rep_dominating_conversation():
    call = CallTranscript(
        call_id="hs-0003",
        rep_id="rep-02",
        vertical="home_services",
        turns=[
            _turn("rep", "word " * 40, 0, 16),
            _turn("customer", "okay", 16, 17.5),
        ],
    )

    result = RuleBasedScorer().score(call)

    assert result.talk_listen_ratio > 2.5
    assert "rep_talked_too_much" in result.flags
