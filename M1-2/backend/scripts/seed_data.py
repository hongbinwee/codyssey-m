"""패턴이 있는 일정 데이터를 생성해 Firestore에 저장합니다.

실제 저장: python scripts/seed_data.py
생성 개수만 확인: python scripts/seed_data.py --dry-run
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
from random import Random

# `python scripts/seed_data.py` 실행 시 backend 루트를 import path에 추가
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def generate_seed_records(today: date | None = None, days: int = 120) -> list[dict]:
    rng = Random(42)
    today = today or date.today()
    start = today - timedelta(days=days - 1)
    records: list[dict] = []

    for offset in range(days):
        day = start + timedelta(days=offset)
        weekday = day.weekday()
        recent_boost = day >= today - timedelta(days=6)

        templates = []
        if weekday in (0, 2, 4):
            templates.append(("09:00", "11:00", 120, "AI 학습", "study"))
        if weekday in (1, 3):
            templates.append(("19:00", "21:00", 120, "팀 프로젝트", "project"))
        if weekday == 5:
            templates.append(("10:00", "11:30", 90, "운동", "exercise"))
        if rng.random() < 0.45:
            templates.append(("14:00", "15:00", 60, "개인 일정", "personal"))
        if recent_boost and weekday < 5:
            templates.append(("16:00", "17:30", 90, "최근 집중 일정", "study"))

        for start_time, end_time, minutes, title, category in templates:
            records.append({
                "date": day.isoformat(),
                "start_time": start_time,
                "end_time": end_time,
                "value": minutes,
                "title": title,
                "category": category,
                "memo": "seed 데이터",
            })
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Firestore에 저장하지 않고 생성 개수만 확인")
    args = parser.parse_args()

    records = generate_seed_records()
    if args.dry_run:
        print(f"생성 예정: {len(records)}개")
        return

    from app.repositories.firestore_repository import FirestoreRepository
    repo = FirestoreRepository()
    for record in records:
        repo.create_schedule(record)
    print(f"생성 완료: {len(records)}개")


if __name__ == "__main__":
    main()
