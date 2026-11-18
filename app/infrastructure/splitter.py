"""Text splitting strategies for document chunking."""

from typing import List
from app.core.interfaces import TextSplitter
from app.core.logging import get_logger

logger = get_logger(__name__)


class RecursiveCharacterTextSplitter(TextSplitter):
    """
    Recursively split text into chunks with overlapping windows.

    This splitter tries to keep sentences and paragraphs together while
    respecting character limits. It uses a sliding window approach for overlap.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None,
    ):
        """
        Initialize the text splitter.

        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to try splitting on, in order
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def split(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.

        Args:
            text: The text to split

        Returns:
            List of text chunks
        """
        return self._split_text(text, self.separators)

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using separators."""
        good_splits = []

        for separator in separators:
            if separator == "":
                splits = list(text)
            else:
                splits = text.split(separator)

            good_splits = [s for s in splits if len(s) > self.chunk_size]

            if not good_splits:
                break

        if not good_splits:
            good_splits = splits

        return self._merge_splits(good_splits, separator)

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """Merge small splits and apply overlap."""
        separator_len = len(separator)
        good_splits = []
        current_chunk = ""

        for split in splits:
            if len(current_chunk) + len(split) + separator_len <= self.chunk_size:
                current_chunk += separator + split if current_chunk else split
            else:
                if current_chunk:
                    doc = self._create_chunk_with_overlap(current_chunk, good_splits)
                    good_splits.append(doc)

                while len(split) + separator_len > self.chunk_size:
                    chunk = split[: self.chunk_size - separator_len]
                    good_splits.append(chunk)
                    split = split[self.chunk_size - self.chunk_overlap :]

                current_chunk = split

        if current_chunk:
            doc = self._create_chunk_with_overlap(current_chunk, good_splits)
            good_splits.append(doc)

        return [d for d in good_splits if d]

    def _create_chunk_with_overlap(self, chunk: str, previous_chunks: List[str]) -> str:
        """Add overlap from previous chunk if needed."""
        if previous_chunks and self.chunk_overlap > 0:
            last_chunk = previous_chunks[-1]
            overlap_text = last_chunk[-self.chunk_overlap :]
            return overlap_text + chunk

        return chunk


class SimpleCharacterSplitter(TextSplitter):
    """Simple character-based text splitter without overlap."""

    def __init__(self, chunk_size: int = 1000):
        """Initialize the splitter."""
        self.chunk_size = chunk_size

    def split(self, text: str) -> List[str]:
        """Split text into fixed-size chunks."""
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i : i + self.chunk_size])

        return [chunk for chunk in chunks if chunk.strip()]


def create_text_splitter(
    strategy: str = "recursive", chunk_size: int = 1000, chunk_overlap: int = 200
) -> TextSplitter:
    """
    Factory function to create a text splitter.

    Args:
        strategy: "recursive" or "simple"
        chunk_size: Maximum chunk size
        chunk_overlap: Overlap between chunks

    Returns:
        TextSplitter instance
    """
    if strategy == "recursive":
        return RecursiveCharacterTextSplitter(chunk_size, chunk_overlap)
    elif strategy == "simple":
        return SimpleCharacterSplitter(chunk_size)
    else:
        raise ValueError(f"Unknown splitting strategy: {strategy}")
