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
    chatwoot_account_id: int = 1

    # Google Drive (OAuth)
    google_credentials_path: str = "credentials/credentials.json"  # OAuth client JSON from Google Cloud
    google_token_path: str = "credentials/token.json"  # Generated after running auth_google.py

    # Postgres
    postgres_url: str

    # Agent behavior
    message_debounce_seconds: int = 3
    escalation_resume_hours: int = 2  # Hours of human inactivity before bot resumes

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
