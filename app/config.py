from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    llm_provider: str = "anthropic"  # "anthropic" o "ollama" (dev)
    anthropic_api_key: str | None = None
    ollama_model: str = "llama3.1"
    ollama_base_url: str = "http://localhost:11434"

    free_plan_monthly_query_limit: int = 50
    free_plan_monthly_quiz_limit: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
