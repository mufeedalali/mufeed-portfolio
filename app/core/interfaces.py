"""Abstract interfaces for pluggable components."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator


class EmbeddingProvider(ABC):
    """Abstract interface for embedding providers."""

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for a single text."""
        pass

    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, context: str = "") -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    async def stream_generate(
        self, prompt: str, context: str = ""
    ) -> AsyncGenerator[str, None]:
        """Stream a response from the LLM."""
        pass


class VectorStore(ABC):
    """Abstract interface for vector store operations."""

    @abstractmethod
    async def add_documents(
        self, documents: List[Dict[str, Any]], embeddings: List[List[float]]
    ) -> None:
        """Add documents with their embeddings to the store."""
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using embedding."""
        pass

    @abstractmethod
    async def delete_collection(self, collection_name: str) -> None:
        """Delete a collection from the vector store."""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        pass


class DocumentLoader(ABC):
    """Abstract interface for document loaders."""

    @abstractmethod
    async def load(self, file_path: str) -> str:
        """Load document content from file."""
        pass

    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        pass


class TextSplitter(ABC):
    """Abstract interface for text splitting strategies."""

    @abstractmethod
    def split(self, text: str) -> List[str]:
        """Split text into chunks."""
        pass
