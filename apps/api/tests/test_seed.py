from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models_db import CallDB, RepDB, ScoreDB
from app.seed import seed_database

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "transcripts"


def _make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_seed_database_loads_reps_calls_and_scores():
    db = _make_session()
    count = seed_database(db, directory=FIXTURE_DIR)

    assert count == 2
    assert db.query(RepDB).count() == 1
    assert db.query(CallDB).count() == 2
    assert db.query(ScoreDB).count() == 2


def test_seed_database_is_idempotent():
    db = _make_session()
    seed_database(db, directory=FIXTURE_DIR)
    second_count = seed_database(db, directory=FIXTURE_DIR)

    assert second_count == 0
    assert db.query(CallDB).count() == 2
