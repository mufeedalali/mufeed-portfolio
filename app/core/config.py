"""
Configuration module for RAG Pipeline application.

Handles environment-based settings for the entire application using Pydantic.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        app_name: Name of the application
        debug: Debug mode flag
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        api_host: FastAPI host address
        api_port: FastAPI port number
        api_workers: Number of worker processes
        doc_upload_dir: Directory for uploaded documents
        chunk_size: Size of text chunks for splitting
        chunk_overlap: Overlap between chunks
        embedding_model: Model identifier for embeddings
        embedding_dimension: Dimension of embedding vectors
        llm_model: LLM model identifier
        llm_temperature: Temperature for LLM generation
        llm_max_tokens: Maximum tokens for LLM response
        max_context_length: Maximum context length for RAG
        similarity_threshold: Similarity threshold for retrieval
        enable_cache: Enable caching for embeddings
        cache_ttl_seconds: Cache time-to-live in seconds
    """

    app_name: str = "RAG Pipeline - AI Document Assistant"
    debug: bool = False
    log_level: str = "INFO"

    # API Configuration
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_workers: int = 1

    # Storage Configuration
    doc_upload_dir: str = "./data/uploads"
    data_dir: str = "./data"
    sample_docs_dir: str = "./data/sample_documents"

    # Text Processing Configuration
    chunk_size: int = 512
    chunk_overlap: int = 50

    # Embedding Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # LLM Configuration
    llm_model: str = "mock"  # Using mock LLM for offline operation
    llm_temperature: float = 0.7
    llm_max_tokens: int = 512

    # RAG Configuration
    max_context_length: int = 2000
    similarity_threshold: float = 0.3
    top_k_results: int = 3

    # Caching Configuration
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600

    class Config:
        """Pydantic config for environment variable handling."""
        env_file = ".env"
        case_sensitive = False

    @property
    def upload_dir_path(self) -> Path:
        """Get upload directory as Path object."""
        path = Path(self.doc_upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def data_dir_path(self) -> Path:
        """Get data directory as Path object."""
        path = Path(self.data_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def sample_docs_path(self) -> Path:
        """Get sample documents directory as Path object."""
        path = Path(self.sample_docs_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


def get_settings() -> Settings:
    """
    Get application settings singleton.

    Returns:
        Settings: Global application settings instance
    """
    return Settings()
