from functools import lru_cache
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    app_name: str = "MySchedule AI"
    openai_api_key: str = Field(default="", repr=False)
    openai_model: str = "gpt-5-mini"
    openai_base_url: str = "https://copa.codyssey.kr/v1"
    firebase_service_account_json: str = Field(default="", repr=False)
    firebase_service_account_path: str = Field(default="", repr=False)
    allowed_origins: list[str] = ["http://localhost:5500", "http://127.0.0.1:5500"]


@lru_cache
def get_settings() -> Settings:
    origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500")
    origins = [origin.strip() for origin in origins_raw.split(",") if origin.strip()]
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://copa.codyssey.kr/v1"),
        firebase_service_account_json=os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", ""),
        firebase_service_account_path=os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", ""),
        allowed_origins=origins,
    )
