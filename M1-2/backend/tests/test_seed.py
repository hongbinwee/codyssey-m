from datetime import date
from scripts.seed_data import generate_seed_records
from app.services.analysis_service import build_schedule_summary


def test_seed_generates_at_least_100_points():
    rows = generate_seed_records(today=date(2026, 9, 24))
    assert len(rows) >= 100
    assert any(row["title"] == "최근 집중 일정" for row in rows)


def test_seed_recent_week_is_busier_than_previous_week():
    today = date(2026, 9, 26)
    summary = build_schedule_summary(generate_seed_records(today=today), today=today)
    trend = summary["recent_trend"]
    assert trend["status"] == "increase"
    assert trend["recent_7d_minutes"] > trend["previous_7d_minutes"]
