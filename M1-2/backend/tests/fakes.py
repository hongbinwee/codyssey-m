from datetime import datetime, timezone
import uuid


class FakeRepository:
    def __init__(self, schedules=None):
        self.schedules = {row.get("id", str(uuid.uuid4())): {**row} for row in (schedules or [])}
        self.conversations = {}

    def create_schedule(self, payload):
        sid = str(uuid.uuid4())
        self.schedules[sid] = {**payload}
        return {"id": sid, **payload}

    def list_schedules(self):
        return [{"id": sid, **row} for sid, row in self.schedules.items()]

    def get_schedule(self, sid):
        row = self.schedules.get(sid)
        return None if row is None else {"id": sid, **row}

    def update_schedule(self, sid, payload):
        if sid not in self.schedules:
            return None
        self.schedules[sid] = {**payload}
        return {"id": sid, **payload}

    def delete_schedule(self, sid):
        return self.schedules.pop(sid, None) is not None

    def create_conversation(self, title, messages):
        cid = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        row = {"id": cid, "title": title, "messages": messages, "created_at": now, "updated_at": now}
        self.conversations[cid] = row
        return row

    def list_conversations(self):
        return list(self.conversations.values())

    def get_conversation(self, cid):
        return self.conversations.get(cid)

    def append_conversation_messages(self, cid, messages):
        row = self.conversations.get(cid)
        if not row:
            return None
        row["messages"] += messages
        return row

    def delete_conversation(self, cid):
        return self.conversations.pop(cid, None) is not None


class FakeAIService:
    def answer(self, instructions, user_message):
        assert "사용자 일정 요약" in instructions
        return f"테스트 AI 답변: {user_message}"
