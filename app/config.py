from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str

    # LangSmith
    langchain_tracing_v2: bool = True
    langchain_api_key: str

    # Chatwoot
    chatwoot_base_url: str
    chatwoot_api_token: str
    chatwoot_webhook_secret: str

    # Google Drive
    google_credentials_path: str  # Path to OAuth/Service Account JSON file

    # Postgres
    postgres_url: str

    # Agent behavior
    message_debounce_seconds: int = 3
    escalation_resume_hours: int = 2  # Hours of human inactivity before bot resumes

    class Config:
        env_file = ".env"


settings = Settings()
