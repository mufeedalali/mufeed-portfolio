"""
Domain interfaces and abstract base classes.

Defines contracts for infrastructure components.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from app.domain.models import (
    Document,
    TextChunk,
    Embedding,
    RetrievalResult,
)


class DocumentLoader(ABC):
    """Abstract base class for document loading."""

    @abstractmethod
    async def load(self, file_path: str) -> Document:
        """
        Load a document from file.

        Args:
            file_path: Path to the document file

        Returns:
            Document: Loaded document

        Raises:
            DocumentLoadError: If loading fails
        """
        pass

    @abstractmethod
    async def supports(self, file_path: str) -> bool:
        """
        Check if loader supports the file type.

        Args:
            file_path: Path to check

        Returns:
            bool: True if supported
        """
        pass


class TextSplitter(ABC):
    """Abstract base class for text splitting."""

    @abstractmethod
    async def split(self, document: Document) -> List[TextChunk]:
        """
        Split document text into chunks.

        Args:
            document: Document to split

        Returns:
            List[TextChunk]: List of text chunks

        Raises:
            TextSplittingError: If splitting fails
        """
        pass


class EmbeddingModel(ABC):
    """Abstract base class for embedding generation."""

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            List[float]: Embedding vector

        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List[List[float]]: List of embedding vectors

        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get embedding dimension.

        Returns:
            int: Embedding dimension
        """
        pass


class VectorStore(ABC):
    """Abstract base class for vector storage and retrieval."""

    @abstractmethod
    async def add_embedding(self, embedding: Embedding, chunk: TextChunk) -> str:
        """
        Add embedding to vector store.

        Args:
            embedding: Embedding to store
            chunk: Associated text chunk

        Returns:
            str: ID of stored embedding

        Raises:
            VectorStoreError: If operation fails
        """
        pass

    @abstractmethod
    async def add_embeddings(
        self, embeddings: List[Embedding], chunks: List[TextChunk]
    ) -> List[str]:
        """
        Add multiple embeddings to vector store.

        Args:
            embeddings: List of embeddings
            chunks: List of associated chunks

        Returns:
            List[str]: IDs of stored embeddings

        Raises:
            VectorStoreError: If operation fails
        """
        pass

    @abstractmethod
    async def search(
        self, query_vector: List[float], top_k: int = 5, threshold: float = 0.0
    ) -> List[RetrievalResult]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            threshold: Similarity threshold

        Returns:
            List[RetrievalResult]: Retrieved results

        Raises:
            VectorStoreError: If search fails
        """
        pass

    @abstractmethod
    async def delete(self, chunk_id: str) -> bool:
        """
        Delete embedding from vector store.

        Args:
            chunk_id: ID of chunk to delete

        Returns:
            bool: True if successful

        Raises:
            VectorStoreError: If deletion fails
        """
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """
        Clear all embeddings from vector store.

        Returns:
            bool: True if successful

        Raises:
            VectorStoreError: If clearing fails
        """
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dict[str, Any]: Store statistics
        """
        pass


class LLMService(ABC):
    """Abstract base class for LLM operations."""

    @abstractmethod
    async def generate(
        self, prompt: str, max_tokens: int = 512, temperature: float = 0.7
    ) -> str:
        """
        Generate text using LLM.

        Args:
            prompt: Prompt text
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature

        Returns:
            str: Generated text

        Raises:
            LLMError: If generation fails
        """
        pass

    @abstractmethod
    async def generate_with_history(
        self, messages: List[Dict[str, str]], max_tokens: int = 512
    ) -> str:
        """
        Generate response with conversation history.

        Args:
            messages: List of messages in conversation
            max_tokens: Maximum tokens to generate

        Returns:
            str: Generated response

        Raises:
            LLMError: If generation fails
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM model.

        Returns:
            Dict[str, Any]: Model information
        """
        pass
