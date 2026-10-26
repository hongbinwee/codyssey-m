from app.core.config import get_settings
from openai import OpenAIError


class OpenAIService:
    def __init__(self, client=None):
        settings = get_settings()
        self.model = settings.openai_model
        self.max_completion_tokens = getattr(settings, "openai_max_completion_tokens", 2048)
        if client is not None:
            self.client = client
            return
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY가 설정되어 있지 않습니다.")
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    def answer(self, instructions: str, user_message: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=self.max_completion_tokens,
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": user_message},
                ],
            )
        except OpenAIError as exc:
            raise RuntimeError("AI 서비스 요청에 실패했습니다. 잠시 후 다시 시도해 주세요.") from exc
        text = (response.choices[0].message.content or "").strip() if response.choices else ""
        if not text:
            raise RuntimeError("OpenAI 응답에서 텍스트를 찾지 못했습니다.")
        return text
