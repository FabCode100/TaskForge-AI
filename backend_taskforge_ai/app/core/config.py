from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "TaskForge-AI Backend"
    debug: bool = True
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "sqlite:///./taskforge.db"
    storage_path: str = "./storage"

    # Hugging Face / LLM settings
    huggingfacehub_api_token: Optional[str] = None
    hf_model: Optional[str] = None

    # Gemini / Google Generative Language settings
    gemini_api_key: Optional[str] = None
    gemini_model: str = "text-bison-001"

    class Config:
        env_file = ".env"


settings = Settings()
