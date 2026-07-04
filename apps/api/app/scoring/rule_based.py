from __future__ import annotations

import re

from app.scoring.models import CallTranscript, ScoreResult

OBJECTION_PHRASES = ["too expensive", "talk to my spouse", "shop around", "think about it"]
# "understand" and "value" were dropped: they're generic enough to match a
# dismissive non-answer ("I understand, but the price is firm.") as if the
# objection had actually been addressed.
HANDLING_PHRASES = ["financing", "break down what's included"]
PRICING_PHRASES = ["price", "cost", "total", "$", "/month"]

# Cap rather than use float('inf') for zero-customer-talk-time calls: `inf`
# serializes as the non-standard JSON token `Infinity`, which breaks JSON
# parsers on the receiving end (e.g. the frontend's fetch().json()).
MAX_TALK_LISTEN_RATIO = 999.0
NEXT_STEP_PHRASES = ["schedule", "follow up", "send over", "paperwork", "next week", "move forward"]
# Bare "yes" was dropped: a reply like "Yes, but I need to shop around" would
# otherwise count as a commitment even though it's a deferral.
NEXT_STEP_COMMIT_PHRASES = [
    "sounds good", "let's do it", "let's move forward", "sure, send it", "we can look at it",
]
POSITIVE_WORDS = ["great", "good", "excited", "sounds good", "yes", "sure"]
NEGATIVE_WORDS = ["expensive", "not sure", "think about it", "shop around", "we'll see"]

_SINGLE_WORD_RE = re.compile(r"^[a-z']+$")


def _contains_any(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    for phrase in phrases:
        # Single bare words get word-boundary matching so they don't fire
        # inside an unrelated longer word; multi-word phrases and phrases
        # with symbols (e.g. "$", "/month") keep plain substring matching,
        # since \b doesn't work sensibly around non-word characters.
        if _SINGLE_WORD_RE.match(phrase):
            if re.search(rf"\b{re.escape(phrase)}\b", lowered):
                return True
        elif phrase in lowered:
            return True
    return False


class RuleBasedScorer:
    """Deterministic, keyword-and-timing based scorer. No external dependencies."""

    def score(self, call: CallTranscript) -> ScoreResult:
        rep_time = sum(t.duration for t in call.turns if t.speaker == "rep")
        customer_time = sum(t.duration for t in call.turns if t.speaker == "customer")
        talk_listen_ratio = round(rep_time / customer_time, 2) if customer_time else MAX_TALK_LISTEN_RATIO

        customer_turns = [t.text for t in call.turns if t.speaker == "customer"]
        rep_turns = [t.text for t in call.turns if t.speaker == "rep"]

        pricing_discussed = any(_contains_any(t, PRICING_PHRASES) for t in rep_turns)
        # Requirements call for tracking specifically whether a *pricing*
        # objection came up (docs/02-requirements.md #2). OBJECTION_PHRASES
        # includes objections that aren't about price (e.g. "talk to my
        # spouse"), so gate on pricing having actually been discussed.
        objection_raised = pricing_discussed and any(
            _contains_any(t, OBJECTION_PHRASES) for t in customer_turns
        )
        objection_handled_well = objection_raised and any(
            _contains_any(t, HANDLING_PHRASES) for t in rep_turns
        )
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
            scored_by="rule",
            flags=flags,
        )
