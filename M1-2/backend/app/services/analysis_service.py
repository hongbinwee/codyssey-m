from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from statistics import mean

WEEKDAY_KO = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]


def _to_date(value) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return date.fromisoformat(str(value)[:10])


def build_schedule_summary(rows: list[dict], today: date | None = None) -> dict:
    today = today or date.today()
    if not rows:
        return {
            "period": None,
            "count": 0,
            "metrics": {"total_minutes": 0, "total_hours": 0, "average_daily_minutes": 0, "max_daily_minutes": 0, "min_daily_minutes": 0},
            "busiest_day": None,
            "busiest_weekday": None,
            "top_category": None,
            "category_distribution": {},
            "weekday_distribution": {},
            "recent_trend": {"status": "no_data", "change_percent": None, "recent_7d_minutes": 0, "previous_7d_minutes": 0},
        }

    normalized = []
    for row in rows:
        normalized.append({**row, "_date": _to_date(row["date"]), "value": int(row["value"])})

    dates = [row["_date"] for row in normalized]
    daily_minutes = defaultdict(int)
    category_minutes = Counter()
    weekday_minutes = Counter()

    for row in normalized:
        daily_minutes[row["_date"]] += row["value"]
        category_minutes[row.get("category", "other")] += row["value"]
        weekday_minutes[WEEKDAY_KO[row["_date"].weekday()]] += row["value"]

    all_daily_values = list(daily_minutes.values())
    busiest_date, busiest_minutes = max(daily_minutes.items(), key=lambda item: item[1])
    top_category, top_category_minutes = category_minutes.most_common(1)[0]
    busiest_weekday, busiest_weekday_minutes = weekday_minutes.most_common(1)[0]

    recent_start = today - timedelta(days=6)
    previous_start = today - timedelta(days=13)
    previous_end = today - timedelta(days=7)

    recent = sum(row["value"] for row in normalized if recent_start <= row["_date"] <= today)
    previous = sum(row["value"] for row in normalized if previous_start <= row["_date"] <= previous_end)

    if previous == 0 and recent == 0:
        trend_status, change = "maintain", 0.0
    elif previous == 0:
        trend_status, change = "increase", None
    else:
        change = round((recent - previous) / previous * 100, 1)
        trend_status = "increase" if change > 5 else "decrease" if change < -5 else "maintain"

    total_minutes = sum(row["value"] for row in normalized)
    return {
        "period": {"start": min(dates).isoformat(), "end": max(dates).isoformat()},
        "count": len(normalized),
        "metrics": {
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 1),
            "average_daily_minutes": round(mean(all_daily_values), 1),
            "max_daily_minutes": max(all_daily_values),
            "min_daily_minutes": min(all_daily_values),
        },
        "busiest_day": {"date": busiest_date.isoformat(), "minutes": busiest_minutes},
        "busiest_weekday": {"weekday": busiest_weekday, "minutes": busiest_weekday_minutes},
        "top_category": {"category": top_category, "minutes": top_category_minutes},
        "category_distribution": dict(category_minutes),
        "weekday_distribution": dict(weekday_minutes),
        "recent_trend": {
            "status": trend_status,
            "change_percent": change,
            "recent_7d_minutes": recent,
            "previous_7d_minutes": previous,
        },
    }
