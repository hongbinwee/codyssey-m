from app.services.analysis_service import build_schedule_summary
from app.services.prompt_service import build_schedule_instructions


class ChatService:
    def __init__(self, repository, ai_service):
        self.repository = repository
        self.ai_service = ai_service

    def chat(self, message: str, conversation_id: str | None = None) -> dict:
        rows = self.repository.list_schedules()
        summary = build_schedule_summary(rows)
        instructions = build_schedule_instructions(summary)
        answer = self.ai_service.answer(instructions, message)

        new_messages = [
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer},
        ]

        if conversation_id:
            conversation = self.repository.append_conversation_messages(conversation_id, new_messages)
            if conversation is None:
                conversation = self.repository.create_conversation(message[:40], new_messages)
        else:
            conversation = self.repository.create_conversation(message[:40], new_messages)

        return {"conversation_id": conversation["id"], "answer": answer}
