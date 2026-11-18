"""Dependency injection container with singleton instances."""

from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.domain.interfaces import (
    IEmbeddingProvider,
    ILLMProvider,
    ITextSplitter,
    IVectorStore,
)
from app.infrastructure.document_loaders import DocumentLoaderFactory
from app.infrastructure.embeddings import (
    MockEmbeddingProvider,
    OpenAIEmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
)
from app.infrastructure.llm_service import LLMProviderFactory
from app.infrastructure.text_splitter import RecursiveCharacterTextSplitter
from app.infrastructure.vector_store import ChromaVectorStore

logger = get_logger(__name__)
settings = get_settings()


class DIContainer:
    """Dependency Injection container for singleton instances."""

    _embedding_provider: Optional[IEmbeddingProvider] = None
    _vector_store: Optional[IVectorStore] = None
    _text_splitter: Optional[ITextSplitter] = None
    _llm_provider: Optional[ILLMProvider] = None
    _loader_factory: Optional[DocumentLoaderFactory] = None

    @classmethod
    def get_embedding_provider(cls) -> IEmbeddingProvider:
        """Get singleton embedding provider."""
        if cls._embedding_provider is None:
            logger.info(
                "initializing_embedding_provider",
                model=settings.embedding_model
            )

            if settings.embedding_model == "mock":
                cls._embedding_provider = MockEmbeddingProvider(
                    dimension=settings.embedding_dimension
                )
            elif settings.embedding_model == "openai":
                if not settings.openai_api_key:
                    raise ValueError(
                        "OpenAI API key required when embedding_model is 'openai'"
                    )
                cls._embedding_provider = OpenAIEmbeddingProvider(
                    api_key=settings.openai_api_key,
                    model=settings.sentence_transformer_model,
                    dimension=settings.embedding_dimension
                )
            elif settings.embedding_model == "sentence-transformers":
                cls._embedding_provider = SentenceTransformerEmbeddingProvider(
                    model_name=settings.sentence_transformer_model
                )
            else:
                raise ValueError(
                    f"Unknown embedding model: {settings.embedding_model}"
                )

        return cls._embedding_provider

    @classmethod
    def get_vector_store(cls) -> IVectorStore:
        """Get singleton vector store."""
        if cls._vector_store is None:
            logger.info(
                "initializing_vector_store",
                collection=settings.vector_db_collection
            )

            cls._vector_store = ChromaVectorStore(
                persist_directory=settings.vector_db_dir,
                collection_name=settings.vector_db_collection,
                embedding_dimension=settings.embedding_dimension
            )

        return cls._vector_store

    @classmethod
    def get_text_splitter(cls) -> ITextSplitter:
        """Get singleton text splitter."""
        if cls._text_splitter is None:
            logger.info(
                "initializing_text_splitter",
                chunk_size=settings.chunk_size,
                overlap=settings.chunk_overlap
            )

            cls._text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap
            )

        return cls._text_splitter

    @classmethod
    def get_llm_provider(cls) -> ILLMProvider:
        """Get singleton LLM provider."""
        if cls._llm_provider is None:
            logger.info(
                "initializing_llm_provider",
                provider=settings.llm_provider,
                model=settings.llm_model
            )

            config = {
                "api_key": settings.openai_api_key,
                "model": settings.llm_model,
                "temperature": settings.llm_temperature,
                "max_tokens": settings.llm_max_tokens,
            }

            cls._llm_provider = LLMProviderFactory.create_provider(
                provider_type=settings.llm_provider,
                **{k: v for k, v in config.items() if v is not None}
            )

        return cls._llm_provider

    @classmethod
    def get_loader_factory(cls) -> DocumentLoaderFactory:
        """Get singleton document loader factory."""
        if cls._loader_factory is None:
            logger.info("initializing_loader_factory")
            cls._loader_factory = DocumentLoaderFactory()

        return cls._loader_factory

    @classmethod
    def reset(cls):
        """Reset all singletons (for testing)."""
        cls._embedding_provider = None
        cls._vector_store = None
        cls._text_splitter = None
        cls._llm_provider = None
        cls._loader_factory = None
        logger.info("di_container_reset")


def get_dependencies():
    """Get all dependencies as a dictionary."""
    return {
        "embedding_provider": DIContainer.get_embedding_provider(),
        "vector_store": DIContainer.get_vector_store(),
        "text_splitter": DIContainer.get_text_splitter(),
        "llm_provider": DIContainer.get_llm_provider(),
        "loader_factory": DIContainer.get_loader_factory(),
    }
