from __future__ import annotations

from app.scoring.models import CallTranscript, ScoreResult

OBJECTION_PHRASES = ["too expensive", "talk to my spouse", "shop around", "think about it"]
HANDLING_PHRASES = ["financing", "break down what's included", "value", "understand"]
PRICING_PHRASES = ["price", "cost", "total", "$", "/month"]
NEXT_STEP_PHRASES = ["schedule", "follow up", "send over", "paperwork", "next week", "move forward"]
NEXT_STEP_COMMIT_PHRASES = ["sounds good", "let's do it", "let's move forward", "sure, send it", "yes"]
POSITIVE_WORDS = ["great", "good", "excited", "sounds good", "yes", "sure"]
NEGATIVE_WORDS = ["expensive", "not sure", "think about it", "shop around", "we'll see"]


def _contains_any(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


class RuleBasedScorer:
    """Deterministic, keyword-and-timing based scorer. No external dependencies."""

    def score(self, call: CallTranscript) -> ScoreResult:
        rep_time = sum(t.duration for t in call.turns if t.speaker == "rep")
        customer_time = sum(t.duration for t in call.turns if t.speaker == "customer")
        talk_listen_ratio = round(rep_time / customer_time, 2) if customer_time else float("inf")

        customer_turns = [t.text for t in call.turns if t.speaker == "customer"]
        rep_turns = [t.text for t in call.turns if t.speaker == "rep"]

        objection_raised = any(_contains_any(t, OBJECTION_PHRASES) for t in customer_turns)
        objection_handled_well = objection_raised and any(
            _contains_any(t, HANDLING_PHRASES) for t in rep_turns
        )
        pricing_discussed = any(_contains_any(t, PRICING_PHRASES) for t in rep_turns)
        next_step_offered = any(_contains_any(t, NEXT_STEP_PHRASES) for t in rep_turns)
        next_step_committed = next_step_offered and any(
            _contains_any(t, NEXT_STEP_COMMIT_PHRASES) for t in customer_turns
        )

        positive_hits = sum(_contains_any(t, POSITIVE_WORDS) for t in customer_turns)
        negative_hits = sum(_contains_any(t, NEGATIVE_WORDS) for t in customer_turns)
        total_hits = positive_hits + negative_hits
        sentiment_score = round((positive_hits - negative_hits) / total_hits, 2) if total_hits else 0.0

        flags: list[str] = []
        if talk_listen_ratio > 2.5:
            flags.append("rep_talked_too_much")
        if objection_raised and not objection_handled_well:
            flags.append("objection_not_handled")
        if not next_step_committed:
            flags.append("no_next_step_commitment")

        score_components = [
            1.0 if 0.5 <= talk_listen_ratio <= 2.5 else 0.4,
            1.0 if not objection_raised or objection_handled_well else 0.2,
            1.0 if pricing_discussed else 0.5,
            1.0 if next_step_committed else 0.3,
            (sentiment_score + 1) / 2,
        ]
        overall_score = round(sum(score_components) / len(score_components) * 100, 1)

        return ScoreResult(
            talk_listen_ratio=talk_listen_ratio,
            objection_raised=objection_raised,
            objection_handled_well=objection_handled_well,
            pricing_discussed=pricing_discussed,
            next_step_committed=next_step_committed,
            sentiment_score=sentiment_score,
            overall_score=overall_score,
            flags=flags,
        )
