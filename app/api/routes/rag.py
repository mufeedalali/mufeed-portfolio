"""
RAG query routes for the API.

Provides endpoints for querying documents using retrieval-augmented generation.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.schemas import QueryRequest, RAGResponseSchema, RetrievalResultResponse
from app.api.dependencies import get_rag_service
from app.core.logging import get_logger
from app.core.exceptions import RetrievalError, LLMError

logger = get_logger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/query", response_model=RAGResponseSchema)
async def query_documents(
    request: QueryRequest,
    rag_service=Depends(get_rag_service),
):
    """
    Query documents using RAG pipeline.

    Args:
        request: Query request with parameters
        rag_service: RAG service instance

    Returns:
        RAGResponseSchema: Generated response with sources

    Raises:
        HTTPException: If query processing fails
    """
    try:
        logger.info(f"Processing query: {request.query}")

        # Process query through RAG pipeline
        response = await rag_service.query(request.query)

        # Convert to response schema
        retrieved_chunks = [
            RetrievalResultResponse(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                filename=chunk.filename,
                content=chunk.content,
                similarity_score=chunk.similarity_score,
                metadata=chunk.metadata,
            )
            for chunk in response.retrieved_chunks
        ]

        return RAGResponseSchema(
            query=response.query,
            answer=response.answer,
            retrieved_chunks=retrieved_chunks,
            sources=response.sources,
            confidence_score=response.confidence_score,
            generation_time_ms=response.generation_time_ms,
        )

    except (RetrievalError, LLMError) as e:
        logger.error(f"RAG error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/similar", response_model=List[RetrievalResultResponse])
async def find_similar(
    query: str,
    top_k: int = 5,
    rag_service=Depends(get_rag_service),
):
    """
    Find similar documents without generating response.

    Args:
        query: Query string
        top_k: Number of results to return
        rag_service: RAG service instance

    Returns:
        List[RetrievalResultResponse]: Similar documents

    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(f"Finding similar documents for: {query}")

        results = await rag_service.get_similar_documents(query, top_k=top_k)

        return [
            RetrievalResultResponse(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                filename=result.filename,
                content=result.content,
                similarity_score=result.similarity_score,
                metadata=result.metadata,
            )
            for result in results
        ]

    except RetrievalError as e:
        logger.error(f"Retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
