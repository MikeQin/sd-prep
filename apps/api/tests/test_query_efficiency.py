from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models_db import CallDB, RepDB, ScoreDB
from app.routes import get_rep, list_calls, list_reps


def _make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session()


def _seed(db, rep_count=2, calls_per_rep=2):
    for rep_index in range(rep_count):
        rep_id = f"rep-{rep_index}"
        db.add(RepDB(id=rep_id, name=f"Rep {rep_index}", vertical="home_services"))
        for call_index in range(calls_per_rep):
            call_id = f"{rep_id}-call-{call_index}"
            db.add(
                CallDB(
                    id=call_id,
                    rep_id=rep_id,
                    customer_name="Test Customer",
                    vertical="home_services",
                    date="2026-01-01",
                    duration_seconds=10.0,
                    turns=[],
                )
            )
            db.add(
                ScoreDB(
                    call_id=call_id,
                    talk_listen_ratio=1.0,
                    objection_raised=False,
                    objection_handled_well=False,
                    pricing_discussed=True,
                    next_step_committed=True,
                    sentiment_score=0.0,
                    overall_score=80.0,
                    flags=[],
                )
            )
    db.commit()


def _count_queries(engine, fn):
    count = 0

    def _increment(*args, **kwargs):
        nonlocal count
        count += 1

    event.listen(engine, "before_cursor_execute", _increment)
    try:
        fn()
    finally:
        event.remove(engine, "before_cursor_execute", _increment)
    return count


def test_list_reps_query_count_does_not_scale_with_rep_or_call_count():
    small_engine, small_db = _make_session()
    _seed(small_db, rep_count=1, calls_per_rep=1)
    small_count = _count_queries(small_engine, lambda: list_reps(db=small_db))

    large_engine, large_db = _make_session()
    _seed(large_db, rep_count=5, calls_per_rep=5)
    large_count = _count_queries(large_engine, lambda: list_reps(db=large_db))

    # Same query count at 1x1 as at 5x5 proves this isn't N+1 (a per-row
    # lazy load would make large_count grow with rep/call count).
    assert small_count == large_count


def test_list_calls_query_count_does_not_scale_with_call_count():
    small_engine, small_db = _make_session()
    _seed(small_db, rep_count=1, calls_per_rep=1)
    small_count = _count_queries(small_engine, lambda: list_calls(db=small_db))

    large_engine, large_db = _make_session()
    _seed(large_db, rep_count=5, calls_per_rep=5)
    large_count = _count_queries(large_engine, lambda: list_calls(db=large_db))

    assert small_count == large_count


def test_get_rep_query_count_does_not_scale_with_call_count():
    small_engine, small_db = _make_session()
    _seed(small_db, rep_count=1, calls_per_rep=1)
    small_count = _count_queries(small_engine, lambda: get_rep("rep-0", db=small_db))

    large_engine, large_db = _make_session()
    _seed(large_db, rep_count=1, calls_per_rep=20)
    large_count = _count_queries(large_engine, lambda: get_rep("rep-0", db=large_db))

    assert small_count == large_count
