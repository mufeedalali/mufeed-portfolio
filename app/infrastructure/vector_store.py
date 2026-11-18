"""
Vector store implementations for similarity search.

Provides in-memory and persistent vector storage with semantic search.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.core.exceptions import VectorStoreError
from app.domain.models import Embedding, TextChunk, RetrievalResult
from app.domain.interfaces import VectorStore
from app.core.logging import get_logger

logger = get_logger(__name__)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        float: Similarity score (0-1)
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a ** 2 for a in vec1) ** 0.5
    magnitude2 = sum(b ** 2 for b in vec2) ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


class InMemoryVectorStore(VectorStore):
    """
    In-memory vector store implementation.

    Stores embeddings and chunks in memory for fast retrieval.
    """

    def __init__(self):
        """Initialize in-memory vector store."""
        self.embeddings: Dict[str, Embedding] = {}
        self.chunks: Dict[str, TextChunk] = {}
        self.documents: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized InMemoryVectorStore")

    async def add_embedding(self, embedding: Embedding, chunk: TextChunk) -> str:
        """
        Add single embedding to store.

        Args:
            embedding: Embedding to store
            chunk: Associated text chunk

        Returns:
            str: ID of stored embedding
        """
        try:
            return await asyncio.to_thread(self._add_embedding_sync, embedding, chunk)
        except Exception as e:
            logger.error(f"Error adding embedding: {str(e)}")
            raise VectorStoreError(f"Failed to add embedding: {str(e)}")

    def _add_embedding_sync(self, embedding: Embedding, chunk: TextChunk) -> str:
        """Synchronous add embedding."""
        self.embeddings[embedding.chunk_id] = embedding
        self.chunks[chunk.id] = chunk

        # Track document
        doc_id = chunk.document_id
        if doc_id not in self.documents:
            self.documents[doc_id] = {"chunks": [], "filename": chunk.metadata.get("document_filename")}

        self.documents[doc_id]["chunks"].append(chunk.id)
        logger.debug(f"Added embedding for chunk {embedding.chunk_id}")

        return embedding.chunk_id

    async def add_embeddings(
        self, embeddings: List[Embedding], chunks: List[TextChunk]
    ) -> List[str]:
        """
        Add multiple embeddings to store.

        Args:
            embeddings: List of embeddings
            chunks: List of associated chunks

        Returns:
            List[str]: IDs of stored embeddings
        """
        try:
            return await asyncio.to_thread(
                self._add_embeddings_sync, embeddings, chunks
            )
        except Exception as e:
            logger.error(f"Error adding embeddings: {str(e)}")
            raise VectorStoreError(f"Failed to add embeddings: {str(e)}")

    def _add_embeddings_sync(
        self, embeddings: List[Embedding], chunks: List[TextChunk]
    ) -> List[str]:
        """Synchronous add embeddings."""
        ids = []
        for embedding, chunk in zip(embeddings, chunks):
            ids.append(self._add_embedding_sync(embedding, chunk))
        logger.info(f"Added {len(ids)} embeddings to store")
        return ids

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
        """
        try:
            return await asyncio.to_thread(
                self._search_sync, query_vector, top_k, threshold
            )
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise VectorStoreError(f"Failed to search: {str(e)}")

    def _search_sync(
        self, query_vector: List[float], top_k: int = 5, threshold: float = 0.0
    ) -> List[RetrievalResult]:
        """Synchronous search implementation."""
        results = []

        # Calculate similarities
        for chunk_id, embedding in self.embeddings.items():
            similarity = cosine_similarity(query_vector, embedding.vector)

            if similarity >= threshold:
                chunk = self.chunks[chunk_id]
                doc_id = chunk.document_id
                filename = self.documents[doc_id]["filename"]

                result = RetrievalResult(
                    chunk_id=chunk_id,
                    document_id=doc_id,
                    filename=filename,
                    content=chunk.content,
                    similarity_score=similarity,
                    metadata=chunk.metadata,
                )
                results.append(result)

        # Sort by similarity and return top-k
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        results = results[:top_k]

        logger.debug(f"Found {len(results)} similar results")
        return results

    async def delete(self, chunk_id: str) -> bool:
        """
        Delete embedding from store.

        Args:
            chunk_id: ID of chunk to delete

        Returns:
            bool: True if successful
        """
        try:
            return await asyncio.to_thread(self._delete_sync, chunk_id)
        except Exception as e:
            logger.error(f"Error deleting embedding: {str(e)}")
            raise VectorStoreError(f"Failed to delete embedding: {str(e)}")

    def _delete_sync(self, chunk_id: str) -> bool:
        """Synchronous delete."""
        if chunk_id in self.embeddings:
            del self.embeddings[chunk_id]
            if chunk_id in self.chunks:
                del self.chunks[chunk_id]
            logger.debug(f"Deleted embedding {chunk_id}")
            return True
        return False

    async def clear(self) -> bool:
        """Clear all embeddings from store."""
        try:
            return await asyncio.to_thread(self._clear_sync)
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            raise VectorStoreError(f"Failed to clear store: {str(e)}")

    def _clear_sync(self) -> bool:
        """Synchronous clear."""
        self.embeddings.clear()
        self.chunks.clear()
        self.documents.clear()
        logger.info("Cleared vector store")
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        return {
            "total_embeddings": len(self.embeddings),
            "total_chunks": len(self.chunks),
            "total_documents": len(self.documents),
            "store_type": "in_memory",
        }


class PersistentVectorStore(VectorStore):
    """
    Persistent vector store with file-based storage.

    Stores embeddings to disk for persistence across sessions.
    """

    def __init__(self, storage_path: str = "./data/vectors"):
        """
        Initialize persistent vector store.

        Args:
            storage_path: Path to store vector data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.embeddings_file = self.storage_path / "embeddings.json"
        self.chunks_file = self.storage_path / "chunks.json"
        self.documents_file = self.storage_path / "documents.json"
        self._load_from_disk()
        logger.info(f"Initialized PersistentVectorStore at {storage_path}")

    def _load_from_disk(self) -> None:
        """Load embeddings and chunks from disk."""
        self.embeddings: Dict[str, Embedding] = {}
        self.chunks: Dict[str, TextChunk] = {}
        self.documents: Dict[str, Dict[str, Any]] = {}

        try:
            if self.embeddings_file.exists():
                with open(self.embeddings_file, "r") as f:
                    data = json.load(f)
                    self.embeddings = data
            logger.debug(f"Loaded {len(self.embeddings)} embeddings from disk")
        except Exception as e:
            logger.warning(f"Could not load embeddings from disk: {str(e)}")

    def _save_to_disk(self) -> None:
        """Save embeddings and chunks to disk."""
        try:
            with open(self.embeddings_file, "w") as f:
                json.dump(self.embeddings, f, indent=2)
            logger.debug("Saved embeddings to disk")
        except Exception as e:
            logger.error(f"Error saving to disk: {str(e)}")

    async def add_embedding(self, embedding: Embedding, chunk: TextChunk) -> str:
        """Add single embedding to store."""
        try:
            return await asyncio.to_thread(self._add_embedding_sync, embedding, chunk)
        except Exception as e:
            logger.error(f"Error adding embedding: {str(e)}")
            raise VectorStoreError(f"Failed to add embedding: {str(e)}")

    def _add_embedding_sync(self, embedding: Embedding, chunk: TextChunk) -> str:
        """Synchronous add embedding."""
        self.embeddings[embedding.chunk_id] = {
            "chunk_id": embedding.chunk_id,
            "vector": embedding.vector,
            "model": embedding.model,
            "dimension": embedding.dimension,
        }
        self.chunks[chunk.id] = {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "content": chunk.content,
            "chunk_index": chunk.chunk_index,
            "metadata": chunk.metadata,
        }

        doc_id = chunk.document_id
        if doc_id not in self.documents:
            self.documents[doc_id] = {"chunks": [], "filename": chunk.metadata.get("document_filename")}

        self.documents[doc_id]["chunks"].append(chunk.id)
        self._save_to_disk()
        return embedding.chunk_id

    async def add_embeddings(
        self, embeddings: List[Embedding], chunks: List[TextChunk]
    ) -> List[str]:
        """Add multiple embeddings to store."""
        try:
            return await asyncio.to_thread(
                self._add_embeddings_sync, embeddings, chunks
            )
        except Exception as e:
            logger.error(f"Error adding embeddings: {str(e)}")
            raise VectorStoreError(f"Failed to add embeddings: {str(e)}")

    def _add_embeddings_sync(
        self, embeddings: List[Embedding], chunks: List[TextChunk]
    ) -> List[str]:
        """Synchronous add embeddings."""
        ids = []
        for embedding, chunk in zip(embeddings, chunks):
            ids.append(self._add_embedding_sync(embedding, chunk))
        return ids

    async def search(
        self, query_vector: List[float], top_k: int = 5, threshold: float = 0.0
    ) -> List[RetrievalResult]:
        """Search for similar vectors."""
        try:
            return await asyncio.to_thread(
                self._search_sync, query_vector, top_k, threshold
            )
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            raise VectorStoreError(f"Failed to search: {str(e)}")

    def _search_sync(
        self, query_vector: List[float], top_k: int = 5, threshold: float = 0.0
    ) -> List[RetrievalResult]:
        """Synchronous search."""
        results = []

        for chunk_id, embedding_data in self.embeddings.items():
            vector = embedding_data["vector"]
            similarity = cosine_similarity(query_vector, vector)

            if similarity >= threshold:
                chunk_data = self.chunks[chunk_id]
                doc_id = chunk_data["document_id"]
                filename = self.documents[doc_id]["filename"]

                result = RetrievalResult(
                    chunk_id=chunk_id,
                    document_id=doc_id,
                    filename=filename,
                    content=chunk_data["content"],
                    similarity_score=similarity,
                    metadata=chunk_data["metadata"],
                )
                results.append(result)

        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]

    async def delete(self, chunk_id: str) -> bool:
        """Delete embedding from store."""
        try:
            return await asyncio.to_thread(self._delete_sync, chunk_id)
        except Exception as e:
            logger.error(f"Error deleting: {str(e)}")
            raise VectorStoreError(f"Failed to delete: {str(e)}")

    def _delete_sync(self, chunk_id: str) -> bool:
        """Synchronous delete."""
        if chunk_id in self.embeddings:
            del self.embeddings[chunk_id]
            if chunk_id in self.chunks:
                del self.chunks[chunk_id]
            self._save_to_disk()
            return True
        return False

    async def clear(self) -> bool:
        """Clear all embeddings."""
        try:
            return await asyncio.to_thread(self._clear_sync)
        except Exception as e:
            logger.error(f"Error clearing: {str(e)}")
            raise VectorStoreError(f"Failed to clear: {str(e)}")

    def _clear_sync(self) -> bool:
        """Synchronous clear."""
        self.embeddings.clear()
        self.chunks.clear()
        self.documents.clear()
        self._save_to_disk()
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        return {
            "total_embeddings": len(self.embeddings),
            "total_chunks": len(self.chunks),
            "total_documents": len(self.documents),
            "store_type": "persistent",
            "storage_path": str(self.storage_path),
        }
