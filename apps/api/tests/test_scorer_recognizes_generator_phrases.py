"""Guards against data/generate_transcripts.py's dialogue strings and
rule_based.py's phrase lists drifting apart. The scorer's phrase lists were
copy-pasted from the generator's dialogue with nothing keeping them in sync,
so a future wording change to either file could silently break detection
with no test failure. Loads the generator module directly by path since
data/ and apps/api/ are independent packages (data/ has its own
requirements.txt), rather than merging them into one shared module.
"""

import importlib.util
from pathlib import Path

from app.scoring.rule_based import (
    HANDLING_PHRASES,
    NEXT_STEP_COMMIT_PHRASES,
    OBJECTION_PHRASES,
    PRICING_PHRASES,
    _contains_any,
)

_GENERATOR_PATH = Path(__file__).resolve().parents[3] / "data" / "generate_transcripts.py"


def _load_generator():
    spec = importlib.util.spec_from_file_location("generate_transcripts", _GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = _load_generator()


def test_objection_lines_are_recognized_by_the_scorer():
    for phrase in generator.OBJECTION_CUSTOMER:
        assert _contains_any(phrase, OBJECTION_PHRASES), (
            f"generate_transcripts.py's OBJECTION_CUSTOMER line {phrase!r} is no "
            "longer recognized by rule_based.py's OBJECTION_PHRASES - update one "
            "to match the other."
        )


def test_strong_and_average_objection_handling_lines_are_recognized():
    for tier in ("strong", "average"):
        for phrase in generator.OBJECTION_HANDLING[tier]:
            assert _contains_any(phrase, HANDLING_PHRASES), (
                f"generate_transcripts.py's OBJECTION_HANDLING[{tier!r}] line "
                f"{phrase!r} is no longer recognized by rule_based.py's "
                "HANDLING_PHRASES."
            )


def test_strong_and_average_next_step_commit_lines_are_recognized():
    for tier in ("strong", "average"):
        for phrase in generator.NEXT_STEP_CUSTOMER[tier]:
            assert _contains_any(phrase, NEXT_STEP_COMMIT_PHRASES), (
                f"generate_transcripts.py's NEXT_STEP_CUSTOMER[{tier!r}] line "
                f"{phrase!r} is no longer recognized by rule_based.py's "
                "NEXT_STEP_COMMIT_PHRASES."
            )


def test_pricing_rep_lines_are_recognized_as_pricing_discussion():
    for phrase in generator.PRICING_REP:
        sample = phrase.format(price="$4,200")
        assert _contains_any(sample, PRICING_PHRASES)
