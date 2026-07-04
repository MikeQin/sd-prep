"""Guards against the 3-way duplication of the scorecard fields (ScoreResult,
ScoreDB, ScoreOut) silently drifting out of sync. A real single-source-of-truth
fix would mean introducing a library like SQLModel to merge the ORM and
validation layers - out of scope for this exercise - so this test at least
makes drift fail loudly instead of silently.
"""

import dataclasses

from app.models_db import ScoreDB
from app.schemas import ScoreOut
from app.scoring.models import ScoreResult


def test_score_result_score_db_and_score_out_declare_the_same_fields():
    score_result_fields = {f.name for f in dataclasses.fields(ScoreResult)}
    score_db_fields = {c.name for c in ScoreDB.__table__.columns} - {"call_id"}
    score_out_fields = set(ScoreOut.model_fields.keys())

    assert score_result_fields == score_db_fields == score_out_fields
