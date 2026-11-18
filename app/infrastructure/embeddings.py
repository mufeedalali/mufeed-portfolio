"""
Embedding model implementations for text vectorization.

Provides offline-capable deterministic embeddings for RAG pipeline.
"""

import asyncio
import hashlib
import struct
from typing import List
from app.core.exceptions import EmbeddingError
from app.domain.interfaces import EmbeddingModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class DeterministicEmbedding(EmbeddingModel):
    """
    Deterministic embedding model that works 100% offline.

    Uses SHA-256 hash to generate consistent embeddings from text.
    Perfect for testing and offline RAG pipelines.
    """

    def __init__(self, dimension: int = 384):
        """
        Initialize deterministic embedding model.

        Args:
            dimension: Dimension of embeddings (default 384)
        """
        self.dimension = dimension
        self.model_name = "deterministic"
        logger.info(
            f"Initialized DeterministicEmbedding with dimension {dimension}"
        )

    async def embed(self, text: str) -> List[float]:
        """
        Generate deterministic embedding for text.

        Args:
            text: Text to embed

        Returns:
            List[float]: Embedding vector

        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            return await asyncio.to_thread(self._embed_sync, text)
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise EmbeddingError(f"Failed to generate embedding: {str(e)}")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List[List[float]]: List of embedding vectors

        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            embeddings = []
            for text in texts:
                embedding = await self.embed(text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise EmbeddingError(f"Failed to generate batch embeddings: {str(e)}")

    def _embed_sync(self, text: str) -> List[float]:
        """
        Synchronous embedding generation.

        Uses text hash to seed deterministic pseudo-random values.
        """
        # Normalize text
        normalized = text.lower().strip()

        # Generate hash
        hash_bytes = hashlib.sha256(normalized.encode()).digest()

        # Convert hash bytes to embedding values
        embedding = []
        for i in range(self.dimension):
            # Use sliding window of hash bytes
            byte_idx = (i * 4) % len(hash_bytes)
            chunk = hash_bytes[byte_idx : byte_idx + 4]

            # Pad if necessary
            while len(chunk) < 4:
                chunk += b"\x00"

            # Convert to float [-1, 1]
            value = struct.unpack("f", chunk[:4])[0]
            # Normalize to [-1, 1]
            normalized_value = max(-1.0, min(1.0, value / 1e6))
            embedding.append(normalized_value)

        # Normalize to unit length
        magnitude = sum(v ** 2 for v in embedding) ** 0.5
        if magnitude > 0:
            embedding = [v / magnitude for v in embedding]

        return embedding

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension

    def get_model_info(self) -> dict:
        """Get model information."""
        return {
            "model": self.model_name,
            "dimension": self.dimension,
            "type": "deterministic",
            "offline": True,
        }


class MockEmbedding(EmbeddingModel):
    """
    Mock embedding model for testing.

    Generates random embeddings with consistent dimension.
    """

    def __init__(self, dimension: int = 384):
        """
        Initialize mock embedding model.

        Args:
            dimension: Dimension of embeddings (default 384)
        """
        self.dimension = dimension
        self.model_name = "mock"
        logger.info(f"Initialized MockEmbedding with dimension {dimension}")

    async def embed(self, text: str) -> List[float]:
        """
        Generate mock embedding for text.

        Args:
            text: Text to embed

        Returns:
            List[float]: Mock embedding vector
        """
        try:
            return await asyncio.to_thread(self._embed_sync, text)
        except Exception as e:
            logger.error(f"Error generating mock embedding: {str(e)}")
            raise EmbeddingError(f"Failed to generate embedding: {str(e)}")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate mock embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List[List[float]]: List of mock embeddings
        """
        try:
            embeddings = []
            for text in texts:
                embedding = await self.embed(text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch mock embeddings: {str(e)}")
            raise EmbeddingError(f"Failed to generate batch embeddings: {str(e)}")

    def _embed_sync(self, text: str) -> List[float]:
        """
        Synchronous mock embedding generation.

        Uses text hash for pseudo-random but deterministic values.
        """
        # Use hash for determinism
        hash_value = hash(text)
        import random

        random.seed(hash_value)
        embedding = [random.uniform(-1.0, 1.0) for _ in range(self.dimension)]

        # Normalize
        magnitude = sum(v ** 2 for v in embedding) ** 0.5
        if magnitude > 0:
            embedding = [v / magnitude for v in embedding]

        return embedding

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension

    def get_model_info(self) -> dict:
        """Get model information."""
        return {
            "model": self.model_name,
            "dimension": self.dimension,
            "type": "mock",
            "offline": True,
        }


class EmbeddingFactory:
    """Factory for creating embedding models."""

    @staticmethod
    def create(model_name: str = "deterministic", dimension: int = 384) -> EmbeddingModel:
        """
        Create embedding model instance.

        Args:
            model_name: Model type (deterministic, mock)
            dimension: Embedding dimension

        Returns:
            EmbeddingModel: Embedding model instance

        Raises:
            EmbeddingError: If model is not supported
        """
        if model_name == "deterministic":
            return DeterministicEmbedding(dimension)
        elif model_name == "mock":
            return MockEmbedding(dimension)
        else:
            raise EmbeddingError(f"Unknown embedding model: {model_name}")
