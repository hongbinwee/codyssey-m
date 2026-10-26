from functools import lru_cache
from fastapi import HTTPException
from google.auth.exceptions import DefaultCredentialsError
from app.repositories.firestore_repository import FirestoreRepository
from app.services.openai_service import OpenAIService
from app.services.chat_service import ChatService


@lru_cache
def get_repository():
    try:
        return FirestoreRepository()
    except (DefaultCredentialsError, FileNotFoundError, RuntimeError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Firebase 자격 증명을 확인하세요. FIREBASE_SERVICE_ACCOUNT_JSON 또는 FIREBASE_SERVICE_ACCOUNT_PATH를 설정해야 합니다.",
        ) from exc


def get_chat_service():
    try:
        ai_service = OpenAIService()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ChatService(get_repository(), ai_service)
