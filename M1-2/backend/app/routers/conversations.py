from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.dependencies import get_repository
from app.models.conversation import ConversationCreate

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_conversation(payload: ConversationCreate, repo=Depends(get_repository)):
    return repo.create_conversation(payload.title, [m.model_dump() for m in payload.messages])


@router.get("")
def list_conversations(repo=Depends(get_repository)):
    return repo.list_conversations()


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str, repo=Depends(get_repository)):
    conversation = repo.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: str, repo=Depends(get_repository)):
    if not repo.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
