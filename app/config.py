"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    app_name: str = "Policy Intelligence API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Model Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    
    # LLM Settings (Open Source)
    llm_model: str = "microsoft/phi-2"
    llm_device: str = "cpu"
    max_new_tokens: int = 256
    
    # ChromaDB Settings
    chroma_db_path: str = "./.chromadb"
    chroma_collection_name: str = "policy_clauses"
    
    # API Settings
    api_prefix: str = "/api/v1"
    max_results: int = 10
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
