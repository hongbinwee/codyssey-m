from __future__ import annotations
from datetime import date as Date
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator

Category = Literal["study", "project", "meeting", "exercise", "personal", "other"]


class ScheduleBase(BaseModel):
    date: Date
    start_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    value: int = Field(gt=0, le=1440, description="일정 길이(분)")
    title: str = Field(min_length=1, max_length=100)
    category: Category = "other"
    memo: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_time_order(self):
        start_h, start_m = map(int, self.start_time.split(":"))
        end_h, end_m = map(int, self.end_time.split(":"))
        start = start_h * 60 + start_m
        end = end_h * 60 + end_m
        if end <= start:
            raise ValueError("end_time은 start_time보다 늦어야 합니다.")
        expected = end - start
        if abs(expected - self.value) > 5:
            raise ValueError("value는 start_time과 end_time의 차이(분)와 일치해야 합니다.")
        return self


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    date: Date | None = None
    start_time: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end_time: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    value: int | None = Field(default=None, gt=0, le=1440)
    title: str | None = Field(default=None, min_length=1, max_length=100)
    category: Category | None = None
    memo: str | None = Field(default=None, max_length=500)

    @field_validator("memo")
    @classmethod
    def normalize_blank_memo(cls, value):
        return value if value != "" else None


class ScheduleOut(ScheduleBase):
    id: str
