"""Pytest configuration for the RAG Pipeline test suite."""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Provide mock settings for testing."""
    from app.core.config import Settings

    return Settings(
        app_name="Test RAG",
        debug=True,
        chunk_size=100,
        chunk_overlap=20,
        embedding_dimension=128,
        embedding_model="mock",
        llm_provider="mock",
        log_level="DEBUG",
    )


@pytest.fixture
def sample_document_text():
    """Provide sample document text for testing."""
    return """
    Introduction to RAG Systems

    Retrieval-Augmented Generation (RAG) combines two key components:
    retrieval and generation. This hybrid approach improves AI system accuracy
    and reliability by grounding responses in actual document content.

    How RAG Works:
    1. A user submits a query
    2. The retrieval component finds relevant documents
    3. The generation component synthesizes an answer
    4. Citations link the answer to source documents

    Benefits:
    - More accurate responses
    - Traceable citations
    - Reduced hallucination
    - Domain-specific knowledge

    Applications:
    - Customer support
    - Internal knowledge bases
    - Legal document review
    - Medical research
    """


@pytest.fixture
def sample_chunks(sample_document_text):
    """Provide sample chunks for testing."""
    from app.domain.models import Chunk
    from uuid import uuid4

    doc_id = uuid4()
    return [
        Chunk(
            document_id=doc_id,
            text="Introduction to RAG Systems",
            chunk_index=0,
            start_char=0,
            end_char=28,
        ),
        Chunk(
            document_id=doc_id,
            text="Retrieval-Augmented Generation combines retrieval and generation components",
            chunk_index=1,
            start_char=28,
            end_char=108,
        ),
        Chunk(
            document_id=doc_id,
            text="The retrieval component finds relevant documents and the generation component synthesizes answers",
            chunk_index=2,
            start_char=108,
            end_char=210,
        ),
    ]
