from datetime import date
from app.services.analysis_service import build_schedule_summary


def test_summary_calculates_metrics_and_trend():
    rows = [
        {"date": "2026-09-10", "value": 60, "category": "study"},
        {"date": "2026-09-18", "value": 120, "category": "study"},
        {"date": "2026-09-19", "value": 180, "category": "project"},
    ]
    summary = build_schedule_summary(rows, today=date(2026, 9, 19))
    assert summary["count"] == 3
    assert summary["metrics"]["total_minutes"] == 360
    assert summary["busiest_day"]["date"] == "2026-09-19"
    assert summary["recent_trend"]["status"] == "increase"
