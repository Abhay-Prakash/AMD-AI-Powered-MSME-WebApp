from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SubsidyDesk"
    app_env: str = "local"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    api_v1_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/subsidydesk"
    )

    fireworks_api_key: str | None = None
    fireworks_base_url: str = "https://api.fireworks.ai/inference/v1"
    fireworks_reasoning_model: str = "accounts/fireworks/models/gemma-4-31b-it"
    fireworks_document_model: str = "accounts/fireworks/models/qwen3p7-plus"
    fireworks_embedding_model: str = "accounts/fireworks/models/qwen3-embedding-8b"
    fireworks_reranker_model: str = "accounts/fireworks/models/qwen3-reranker-8b"

    kimi_enabled: bool = False
    kimi_chat_model: str | None = None
    ai_gateway_max_retries: int = 2
    
    # Retrieval Configuration
    retrieval_top_k: int = 10
    retrieval_similarity_threshold: float = 0.5
    retrieval_distance_metric: str = "cosine"  # cosine, l2, inner_product
    retrieval_strategy: str = "standard"  # standard, mmr

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
