from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Zentra — Assistant"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://sasis:sasis@localhost:5432/sasis"

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480  # 8 hours

    # Internal LLM API
    llm_api_url: str = ""
    llm_api_key: str = ""
    llm_model: str = "mimo/mimo-v2.5-pro"
    embedding_dimension: int = 1536

    # File upload
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
