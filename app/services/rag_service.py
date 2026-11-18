"""
RAG service for retrieval-augmented generation.

Coordinates retrieval and LLM generation for question answering.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from app.core.exceptions import RetrievalError, LLMError
from app.domain.models import RAGResponse, RetrievalResult
from app.infrastructure.embeddings import DeterministicEmbedding
from app.infrastructure.vector_store import InMemoryVectorStore
from app.infrastructure.llm_service import MockLLMService
from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


class RAGService:
    """
    Service for retrieval-augmented generation.

    Retrieves relevant documents and generates answers using LLM.
    """

    def __init__(
        self,
        embedding_model: DeterministicEmbedding,
        vector_store: InMemoryVectorStore,
        llm_service: MockLLMService,
        settings: Optional[Any] = None,
    ):
        """
        Initialize RAG service.

        Args:
            embedding_model: Embedding model for query encoding
            vector_store: Vector store for retrieval
            llm_service: LLM service for generation
            settings: Application settings
        """
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.settings = settings or get_settings()
        logger.info("Initialized RAGService")

    async def query(self, query: str) -> RAGResponse:
        """
        Process a query through the RAG pipeline.

        Args:
            query: User query string

        Returns:
            RAGResponse: Generated response with retrieved context

        Raises:
            RetrievalError: If retrieval fails
            LLMError: If generation fails
        """
        start_time = time.time()

        try:
            logger.info(f"Processing query: {query}")

            # Step 1: Embed query
            query_vector = await self.embedding_model.embed(query)
            logger.debug("Generated query embedding")

            # Step 2: Retrieve relevant chunks
            retrieved_chunks = await self.vector_store.search(
                query_vector=query_vector,
                top_k=self.settings.top_k_results,
                threshold=self.settings.similarity_threshold,
            )
            logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")

            # Step 3: Build context
            context = self._build_context(retrieved_chunks)
            logger.debug(f"Built context of length {len(context)}")

            # Step 4: Generate answer
            prompt = self._build_prompt(query, context, retrieved_chunks)
            answer = await self.llm_service.generate(
                prompt=prompt,
                max_tokens=self.settings.llm_max_tokens,
                temperature=self.settings.llm_temperature,
            )
            logger.info("Generated answer using LLM")

            # Step 5: Calculate confidence
            confidence = self._calculate_confidence(retrieved_chunks)

            # Build response
            generation_time = (time.time() - start_time) * 1000  # ms

            sources = list(set(chunk.filename for chunk in retrieved_chunks))
            response = RAGResponse(
                query=query,
                answer=answer,
                retrieved_chunks=retrieved_chunks,
                sources=sources,
                confidence_score=confidence,
                generation_time_ms=generation_time,
            )

            logger.info(f"Query processed in {generation_time:.2f}ms")
            return response

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    def _build_context(self, retrieved_chunks: List[RetrievalResult]) -> str:
        """
        Build context string from retrieved chunks.

        Args:
            retrieved_chunks: Retrieved text chunks

        Returns:
            str: Context string
        """
        context_parts = []

        for i, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(f"[Source {i}: {chunk.filename}]\n{chunk.content}")

        return "\n\n".join(context_parts)

    def _build_prompt(
        self, query: str, context: str, retrieved_chunks: List[RetrievalResult]
    ) -> str:
        """
        Build prompt for LLM.

        Args:
            query: User query
            context: Retrieved context
            retrieved_chunks: Retrieved chunks

        Returns:
            str: Formatted prompt
        """
        prompt = f"""You are a helpful assistant answering questions based on provided documents.

Context:
{context}

Question: {query}

Based on the context above, provide a clear and comprehensive answer to the question."""

        return prompt

    def _calculate_confidence(self, retrieved_chunks: List[RetrievalResult]) -> float:
        """
        Calculate confidence score based on retrieval results.

        Args:
            retrieved_chunks: Retrieved chunks

        Returns:
            float: Confidence score (0-1)
        """
        if not retrieved_chunks:
            return 0.0

        # Average similarity score with boost for multiple results
        avg_similarity = sum(c.similarity_score for c in retrieved_chunks) / len(
            retrieved_chunks
        )

        # Boost if multiple results
        result_boost = min(len(retrieved_chunks) / self.settings.top_k_results, 1.0)

        confidence = (avg_similarity + result_boost) / 2
        return min(confidence, 1.0)

    async def get_similar_documents(
        self, query: str, top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Find similar documents without generating response.

        Args:
            query: Query string
            top_k: Number of results to return

        Returns:
            List[RetrievalResult]: Similar documents
        """
        try:
            query_vector = await self.embedding_model.embed(query)
            results = await self.vector_store.search(
                query_vector=query_vector,
                top_k=top_k,
                threshold=self.settings.similarity_threshold,
            )
            logger.info(f"Found {len(results)} similar documents")
            return results
        except Exception as e:
            logger.error(f"Error finding similar documents: {str(e)}")
            raise RetrievalError(f"Failed to find similar documents: {str(e)}")

    async def get_vector_store_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.

        Returns:
            Dict[str, Any]: Vector store statistics
        """
        return await self.vector_store.get_stats()
