from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = ""

    # Chunking
    chunk_size: int = 900
    chunk_overlap: int = 150

    # Retrieval
    top_k: int = 4

    # LLM
    llm_model: str = "claude-sonnet-4-6"
    llm_temperature: float = 0.0

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"

    # Storage
    chroma_persist_dir: str = "./storage/chroma"
    upload_dir: str = "./storage/uploads"


settings = Settings()
