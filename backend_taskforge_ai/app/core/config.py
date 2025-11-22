from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = "TaskForge-AI Backend"
    debug: bool = True
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "sqlite:///./taskforge.db"
    storage_path: str = "./storage"

    class Config:
        env_file = ".env"


settings = Settings()
