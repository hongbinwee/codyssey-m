from datetime import datetime, timezone
from app.core.firebase import get_firestore_client


class FirestoreRepository:
    DATA_COLLECTION = "data"
    CONVERSATIONS_COLLECTION = "conversations"

    def __init__(self, db=None):
        self.db = db or get_firestore_client()

    def create_schedule(self, payload: dict) -> dict:
        doc = self.db.collection(self.DATA_COLLECTION).document()
        now = datetime.now(timezone.utc)
        stored = {**payload, "created_at": now, "updated_at": now}
        doc.set(stored)
        return {"id": doc.id, **payload}

    def list_schedules(self) -> list[dict]:
        docs = self.db.collection(self.DATA_COLLECTION).stream()
        rows = []
        for doc in docs:
            row = doc.to_dict() or {}
            row.pop("created_at", None)
            row.pop("updated_at", None)
            rows.append({"id": doc.id, **row})
        rows.sort(key=lambda item: (item.get("date", ""), item.get("start_time", "")))
        return rows

    def get_schedule(self, schedule_id: str) -> dict | None:
        doc = self.db.collection(self.DATA_COLLECTION).document(schedule_id).get()
        if not doc.exists:
            return None
        row = doc.to_dict() or {}
        row.pop("created_at", None)
        row.pop("updated_at", None)
        return {"id": doc.id, **row}

    def update_schedule(self, schedule_id: str, payload: dict) -> dict | None:
        ref = self.db.collection(self.DATA_COLLECTION).document(schedule_id)
        snapshot = ref.get()
        if not snapshot.exists:
            return None
        ref.update({**payload, "updated_at": datetime.now(timezone.utc)})
        updated = ref.get().to_dict() or {}
        updated.pop("created_at", None)
        updated.pop("updated_at", None)
        return {"id": schedule_id, **updated}

    def delete_schedule(self, schedule_id: str) -> bool:
        ref = self.db.collection(self.DATA_COLLECTION).document(schedule_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True

    def create_conversation(self, title: str, messages: list[dict]) -> dict:
        doc = self.db.collection(self.CONVERSATIONS_COLLECTION).document()
        now = datetime.now(timezone.utc)
        payload = {"title": title, "messages": messages, "created_at": now, "updated_at": now}
        doc.set(payload)
        return {"id": doc.id, **payload}

    def list_conversations(self) -> list[dict]:
        docs = self.db.collection(self.CONVERSATIONS_COLLECTION).stream()
        rows = [{"id": doc.id, **(doc.to_dict() or {})} for doc in docs]
        rows.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
        return rows

    def get_conversation(self, conversation_id: str) -> dict | None:
        doc = self.db.collection(self.CONVERSATIONS_COLLECTION).document(conversation_id).get()
        if not doc.exists:
            return None
        return {"id": doc.id, **(doc.to_dict() or {})}

    def append_conversation_messages(self, conversation_id: str, messages: list[dict]) -> dict | None:
        ref = self.db.collection(self.CONVERSATIONS_COLLECTION).document(conversation_id)
        snapshot = ref.get()
        if not snapshot.exists:
            return None
        existing = snapshot.to_dict() or {}
        merged = [*(existing.get("messages") or []), *messages]
        ref.update({"messages": merged, "updated_at": datetime.now(timezone.utc)})
        return self.get_conversation(conversation_id)

    def delete_conversation(self, conversation_id: str) -> bool:
        ref = self.db.collection(self.CONVERSATIONS_COLLECTION).document(conversation_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True
