"""
Tests for embedding models.

Tests deterministic and mock embedding implementations.
"""

import pytest
from app.infrastructure.embeddings import DeterministicEmbedding, MockEmbedding, EmbeddingFactory


class TestDeterministicEmbedding:
    """Tests for DeterministicEmbedding."""

    @pytest.mark.asyncio
    async def test_embed_basic(self):
        """Test basic embedding generation."""
        model = DeterministicEmbedding(dimension=384)
        text = "This is a test sentence."

        embedding = await model.embed(text)

        assert len(embedding) == 384
        assert all(isinstance(v, float) for v in embedding)
        assert all(-1.0 <= v <= 1.0 for v in embedding)

    @pytest.mark.asyncio
    async def test_embed_deterministic(self):
        """Test that embeddings are deterministic."""
        model = DeterministicEmbedding(dimension=384)
        text = "This is a test sentence."

        embedding1 = await model.embed(text)
        embedding2 = await model.embed(text)

        assert embedding1 == embedding2

    @pytest.mark.asyncio
    async def test_embed_different_texts(self):
        """Test that different texts produce different embeddings."""
        model = DeterministicEmbedding(dimension=384)

        embedding1 = await model.embed("First text")
        embedding2 = await model.embed("Second text")

        assert embedding1 != embedding2

    @pytest.mark.asyncio
    async def test_embed_batch(self):
        """Test batch embedding generation."""
        model = DeterministicEmbedding(dimension=384)
        texts = ["First text", "Second text", "Third text"]

        embeddings = await model.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)

    @pytest.mark.asyncio
    async def test_embed_normalization(self):
        """Test that embeddings are normalized."""
        model = DeterministicEmbedding(dimension=384)
        text = "Test normalization"

        embedding = await model.embed(text)

        # Calculate magnitude
        magnitude = sum(v ** 2 for v in embedding) ** 0.5

        # Should be approximately 1 (unit vector)
        assert 0.99 <= magnitude <= 1.01

    def test_get_dimension(self):
        """Test dimension getter."""
        model = DeterministicEmbedding(dimension=512)
        assert model.get_dimension() == 512


class TestMockEmbedding:
    """Tests for MockEmbedding."""

    @pytest.mark.asyncio
    async def test_embed_basic(self):
        """Test basic mock embedding generation."""
        model = MockEmbedding(dimension=384)
        text = "This is a test sentence."

        embedding = await model.embed(text)

        assert len(embedding) == 384
        assert all(isinstance(v, float) for v in embedding)

    @pytest.mark.asyncio
    async def test_embed_deterministic(self):
        """Test that mock embeddings are deterministic."""
        model = MockEmbedding(dimension=384)
        text = "This is a test sentence."

        embedding1 = await model.embed(text)
        embedding2 = await model.embed(text)

        assert embedding1 == embedding2

    @pytest.mark.asyncio
    async def test_embed_batch(self):
        """Test batch mock embedding generation."""
        model = MockEmbedding(dimension=384)
        texts = ["First", "Second", "Third"]

        embeddings = await model.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)


class TestEmbeddingFactory:
    """Tests for EmbeddingFactory."""

    def test_create_deterministic(self):
        """Test creating deterministic embedding model."""
        model = EmbeddingFactory.create("deterministic", dimension=384)
        assert isinstance(model, DeterministicEmbedding)
        assert model.get_dimension() == 384

    def test_create_mock(self):
        """Test creating mock embedding model."""
        model = EmbeddingFactory.create("mock", dimension=512)
        assert isinstance(model, MockEmbedding)
        assert model.get_dimension() == 512

    def test_create_unknown(self):
        """Test creating unknown model type."""
        with pytest.raises(Exception):
            EmbeddingFactory.create("unknown")
