from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class ConversationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    messages: list[Message]


class ConversationOut(ConversationCreate):
    id: str
    created_at: datetime | str
    updated_at: datetime | str
