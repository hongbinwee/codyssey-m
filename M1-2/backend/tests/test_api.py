from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_repository, get_chat_service
from app.services.chat_service import ChatService
from tests.fakes import FakeRepository, FakeAIService

repo = FakeRepository()


def override_repo():
    return repo


def override_chat():
    return ChatService(repo, FakeAIService())

app.dependency_overrides[get_repository] = override_repo
app.dependency_overrides[get_chat_service] = override_chat
client = TestClient(app)


def test_health():
    assert client.get("/health").status_code == 200


def test_data_crud_summary_chat_and_conversation_load():
    payload = {
        "date": "2026-09-24",
        "start_time": "09:00",
        "end_time": "11:00",
        "value": 120,
        "title": "AI Agent 수업",
        "category": "study",
        "memo": "FastAPI"
    }
    created = client.post("/api/data", json=payload)
    assert created.status_code == 201
    sid = created.json()["id"]

    listed = client.get("/api/data")
    assert listed.status_code == 200 and len(listed.json()) == 1

    summary = client.get("/api/data/summary")
    assert summary.status_code == 200
    assert summary.json()["metrics"]["total_minutes"] == 120

    updated_payload = {**payload, "end_time": "12:00", "value": 180}
    updated = client.put(f"/api/data/{sid}", json=updated_payload)
    assert updated.status_code == 200
    assert updated.json()["value"] == 180

    chat = client.post("/api/chat", json={"message": "이번 주 바빴어?"})
    assert chat.status_code == 200
    cid = chat.json()["conversation_id"]

    loaded = client.get(f"/api/conversations/{cid}")
    assert loaded.status_code == 200
    assert len(loaded.json()["messages"]) == 2

    deleted = client.delete(f"/api/data/{sid}")
    assert deleted.status_code == 204


def test_partial_update_can_clear_schedule_memo():
    created = client.post("/api/data", json={
        "date": "2026-09-26",
        "start_time": "09:00",
        "end_time": "10:00",
        "value": 60,
        "title": "메모가 있는 일정",
        "category": "study",
        "memo": "지울 내용",
    })
    assert created.status_code == 201
    sid = created.json()["id"]

    updated = client.put(f"/api/data/{sid}", json={"memo": None})

    assert updated.status_code == 200
    assert updated.json()["memo"] is None
    assert repo.get_schedule(sid)["memo"] is None
