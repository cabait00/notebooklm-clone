from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    llm_provider: str = "openai"

    # Chunking
    chunk_size: int = 900
    chunk_overlap: int = 150

    # Retrieval
    top_k: int = 4
    min_similarity: float = 0.25

    # LLM
    llm_model: str = "gpt-4.1-mini"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 1024

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"

    # Storage
    chroma_persist_dir: str = "./storage/chroma"
    upload_dir: str = "./storage/uploads"


settings = Settings()
