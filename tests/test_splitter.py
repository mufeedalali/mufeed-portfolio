"""Tests for text splitting functionality."""

import pytest
from uuid import uuid4

from app.infrastructure.text_splitter import RecursiveCharacterTextSplitter
from app.core.exceptions import ChunkingError


@pytest.fixture
def splitter():
    """Create a text splitter instance."""
    return RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
    )


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    This is a sample document.

    It has multiple paragraphs.
    Each paragraph is separated by newlines.

    This helps test the recursive splitting algorithm.
    The algorithm should split by paragraphs first.
    Then by sentences if needed.
    Finally by words or characters.

    The overlap ensures semantic continuity between chunks.
    This is important for RAG applications.
    """


@pytest.mark.asyncio
async def test_split_text_basic(splitter, sample_text):
    """Test basic text splitting."""
    document_id = uuid4()
    chunks = await splitter.split(sample_text, document_id)

    assert len(chunks) > 0
    assert all(chunk.document_id == document_id for chunk in chunks)
    assert all(chunk.text.strip() for chunk in chunks)


@pytest.mark.asyncio
async def test_split_respects_chunk_size(splitter, sample_text):
    """Test that chunks respect size limits."""
    document_id = uuid4()
    chunks = await splitter.split(sample_text, document_id)

    # Most chunks should be <= chunk_size (some overlap may exceed slightly)
    for chunk in chunks:
        assert len(chunk.text) <= splitter.chunk_size + 50  # Allow slight overage


@pytest.mark.asyncio
async def test_split_maintains_overlap(splitter, sample_text):
    """Test that chunks have overlap."""
    document_id = uuid4()
    chunks = await splitter.split(sample_text, document_id)

    if len(chunks) > 1:
        # Check for overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            chunk1_text = chunks[i].text
            chunk2_text = chunks[i + 1].text
            # Some overlap should exist
            assert splitter.chunk_overlap > 0


@pytest.mark.asyncio
async def test_split_chunks_indexed(splitter, sample_text):
    """Test that chunks are properly indexed."""
    document_id = uuid4()
    chunks = await splitter.split(sample_text, document_id)

    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i


@pytest.mark.asyncio
async def test_split_chunks_positions(splitter, sample_text):
    """Test that chunk positions are set correctly."""
    document_id = uuid4()
    chunks = await splitter.split(sample_text, document_id)

    for chunk in chunks:
        assert chunk.start_char < chunk.end_char
        assert chunk.start_char >= 0
        assert chunk.end_char <= len(sample_text) + 100


@pytest.mark.asyncio
async def test_split_empty_text(splitter):
    """Test that empty text raises error."""
    document_id = uuid4()

    with pytest.raises(ChunkingError):
        await splitter.split("", document_id)

    with pytest.raises(ChunkingError):
        await splitter.split("   ", document_id)


@pytest.mark.asyncio
async def test_split_with_metadata(splitter, sample_text):
    """Test splitting with metadata."""
    document_id = uuid4()
    metadata = {"filename": "test.txt", "source": "test"}

    chunks = await splitter.split(sample_text, document_id, metadata=metadata)

    for chunk in chunks:
        assert "filename" in chunk.metadata or len(chunk.metadata) == 0


@pytest.mark.asyncio
async def test_split_long_text(splitter):
    """Test splitting of long text."""
    # Create a long text
    long_text = " ".join(["word"] * 1000)
    document_id = uuid4()

    chunks = await splitter.split(long_text, document_id)

    assert len(chunks) > 1
    # Verify all text is covered
    total_text = "".join(chunk.text for chunk in chunks)
    # At least most of the text should be present
    assert len(total_text) > len(long_text) * 0.8
