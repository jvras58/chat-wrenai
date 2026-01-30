"""
Configurações da aplicação usando Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas do .env
    """

    groq_api_key: str

    # Modelo padrão
    default_model: str = "llama-3.3-70b-versatile"

    # Configurações do Vector DB
    vector_db_url: str = "http://localhost:6333"
    vector_db_collection: str = "agno-rag-api"
    embedder_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # Modelos (https://qdrant.github.io/fastembed/examples/Supported_Models/)
    embedder_dimensions: int = 384

    # Configurações do Agent
    debug_mode: bool = True

    # Configurações de chunking para JSON
    json_chunk_size: int = 500
    json_overlap: int = 50

    sample_db_url: str = "sqlite+aiosqlite:///wren_sample.db"

    wren_url: str = "http://localhost:8081"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )


settings = Settings()
