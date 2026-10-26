from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_chat_service
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, service=Depends(get_chat_service)):
    try:
        return service.chat(payload.message, payload.conversation_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
