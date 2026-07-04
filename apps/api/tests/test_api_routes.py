from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.main import app
from app.models_db import CallDB
from app.routes import get_call, get_db
from app.seed import seed_database

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "transcripts"


def _build_test_session_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    seed_database(session, directory=FIXTURE_DIR)
    session.close()
    return Session


TestSession = _build_test_session_factory()


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_list_reps_returns_seeded_rep_with_average_score():
    response = client.get("/api/reps")
    assert response.status_code == 200
    reps = response.json()
    assert len(reps) == 1
    assert reps[0]["id"] == "rep-01"
    assert reps[0]["call_count"] == 2


def test_get_call_detail_returns_transcript_and_score():
    response = client.get("/api/calls/hs-0001")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "hs-0001"
    assert body["score"]["objection_handled_well"] is True


def test_get_call_detail_404_for_unknown_call():
    response = client.get("/api/calls/does-not-exist")
    assert response.status_code == 404


def test_get_call_raises_clean_error_for_call_without_a_score():
    db = TestSession()
    db.add(
        CallDB(
            id="hs-no-score",
            rep_id="rep-01",
            customer_name="Unscored Customer",
            vertical="home_services",
            date="2026-01-01",
            duration_seconds=1.0,
            turns=[],
        )
    )
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        get_call("hs-no-score", db=db)

    assert exc_info.value.status_code == 500
    db.close()
