import json
from pathlib import Path

from data.generate_transcripts import generate_all, OUTPUT_DIR, REPS


def test_generate_all_produces_expected_call_count_range():
    calls = generate_all()
    assert 20 <= len(calls) <= 30


def test_each_call_has_required_schema_fields():
    calls = generate_all()
    required = {
        "call_id", "vertical", "rep_id", "rep_name", "customer_name",
        "date", "duration_seconds", "turns",
    }
    for call in calls:
        assert required.issubset(call.keys())
        assert len(call["turns"]) > 0
        for turn in call["turns"]:
            assert turn["speaker"] in ("rep", "customer")
            assert turn["end"] > turn["start"]


def test_all_verticals_and_reps_represented():
    calls = generate_all()
    verticals = {c["vertical"] for c in calls}
    rep_ids = {c["rep_id"] for c in calls}
    assert verticals == {"home_services", "apartment_leasing"}
    assert rep_ids == {r["id"] for r in REPS}


def test_output_files_written_to_disk():
    generate_all()
    written = list(OUTPUT_DIR.glob("*.json"))
    assert len(written) >= 20
    sample = json.loads(written[0].read_text())
    assert "call_id" in sample
