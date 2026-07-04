import json
import shutil
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


def test_seed_database_picks_up_new_transcripts_added_after_first_seed(tmp_path):
    seed_dir = tmp_path / "transcripts"
    seed_dir.mkdir()
    for fixture in FIXTURE_DIR.glob("*.json"):
        shutil.copy(fixture, seed_dir / fixture.name)

    db = _make_session()
    first_count = seed_database(db, directory=seed_dir)
    assert first_count == 2

    new_call = json.loads((FIXTURE_DIR / "hs-0001.json").read_text())
    new_call["call_id"] = "hs-0003"
    (seed_dir / "hs-0003.json").write_text(json.dumps(new_call))

    second_count = seed_database(db, directory=seed_dir)

    assert second_count == 1
    assert db.query(CallDB).count() == 3
