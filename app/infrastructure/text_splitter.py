"""
Text splitting implementations for chunking documents.

Provides various strategies for splitting documents into manageable chunks.
"""

import asyncio
from typing import List
from app.core.exceptions import TextSplittingError
from app.domain.models import Document, TextChunk
from app.domain.interfaces import TextSplitter
from app.core.logging import get_logger
import uuid

logger = get_logger(__name__)


class RecursiveCharacterSplitter(TextSplitter):
    """
    Splits text recursively to maintain semantic boundaries.

    Tries to split on paragraph, sentence, word, then character boundaries.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize splitter.

        Args:
            chunk_size: Target size of chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def split(self, document: Document) -> List[TextChunk]:
        """
        Split document into chunks using recursive strategy.

        Args:
            document: Document to split

        Returns:
            List[TextChunk]: List of text chunks

        Raises:
            TextSplittingError: If splitting fails
        """
        try:
            return await asyncio.to_thread(self._split_sync, document)
        except Exception as e:
            logger.error(f"Error splitting document {document.id}: {str(e)}")
            raise TextSplittingError(f"Failed to split document: {str(e)}")

    def _split_sync(self, document: Document) -> List[TextChunk]:
        """Synchronous text splitting implementation."""
        chunks = []
        text = document.content

        # Try splitting on paragraphs first
        separators = ["\n\n", "\n", ". ", " ", ""]
        good_splits = []

        for separator in separators:
            if separator in text:
                splits = text.split(separator)
                # Filter empty strings
                good_splits = [s for s in splits if s.strip()]
                break

        if not good_splits:
            good_splits = [text]

        # Merge splits into chunks
        current_chunk = ""
        current_start = 0
        chunk_index = 0

        for i, split in enumerate(good_splits):
            if len(current_chunk) + len(split) <= self.chunk_size:
                if current_chunk:
                    current_chunk += " "
                current_chunk += split
            else:
                if current_chunk:
                    start_pos = text.find(current_chunk, current_start)
                    end_pos = start_pos + len(current_chunk)

                    chunk = TextChunk(
                        id=str(uuid.uuid4()),
                        document_id=document.id,
                        content=current_chunk.strip(),
                        chunk_index=chunk_index,
                        start_char=start_pos,
                        end_char=end_pos,
                        metadata={
                            "document_filename": document.filename,
                            "document_type": document.document_type.value,
                        },
                    )
                    chunks.append(chunk)
                    chunk_index += 1

                    # Start new chunk with overlap
                    if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                        overlap_text = current_chunk[-self.chunk_overlap :]
                        current_chunk = overlap_text + " " + split
                        current_start = end_pos - self.chunk_overlap
                    else:
                        current_chunk = split
                        current_start = end_pos
                else:
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            start_pos = text.rfind(current_chunk)
            end_pos = start_pos + len(current_chunk)

            chunk = TextChunk(
                id=str(uuid.uuid4()),
                document_id=document.id,
                content=current_chunk.strip(),
                chunk_index=chunk_index,
                start_char=start_pos,
                end_char=end_pos,
                metadata={
                    "document_filename": document.filename,
                    "document_type": document.document_type.value,
                },
            )
            chunks.append(chunk)

        logger.info(
            f"Split document {document.filename} into {len(chunks)} chunks"
        )
        return chunks


class SimpleSplitter(TextSplitter):
    """Simple splitter that splits on sentence boundaries."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize splitter.

        Args:
            chunk_size: Target size of chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def split(self, document: Document) -> List[TextChunk]:
        """
        Split document into chunks.

        Args:
            document: Document to split

        Returns:
            List[TextChunk]: List of text chunks

        Raises:
            TextSplittingError: If splitting fails
        """
        try:
            return await asyncio.to_thread(self._split_sync, document)
        except Exception as e:
            logger.error(f"Error splitting document {document.id}: {str(e)}")
            raise TextSplittingError(f"Failed to split document: {str(e)}")

    def _split_sync(self, document: Document) -> List[TextChunk]:
        """Synchronous text splitting implementation."""
        chunks = []
        text = document.content
        current_pos = 0
        chunk_index = 0

        while current_pos < len(text):
            # Calculate chunk end position
            chunk_end = min(current_pos + self.chunk_size, len(text))

            # Try to find a sentence boundary
            if chunk_end < len(text):
                # Look backwards for sentence end
                search_end = chunk_end
                found_boundary = False

                for boundary_char in [".", "!", "?", "\n"]:
                    pos = text.rfind(boundary_char, current_pos, chunk_end)
                    if pos != -1:
                        chunk_end = pos + 1
                        found_boundary = True
                        break

                if not found_boundary:
                    # Look for space
                    pos = text.rfind(" ", current_pos, chunk_end)
                    if pos != -1:
                        chunk_end = pos

            chunk_text = text[current_pos:chunk_end].strip()

            if chunk_text:
                chunk = TextChunk(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    content=chunk_text,
                    chunk_index=chunk_index,
                    start_char=current_pos,
                    end_char=chunk_end,
                    metadata={
                        "document_filename": document.filename,
                        "document_type": document.document_type.value,
                    },
                )
                chunks.append(chunk)
                chunk_index += 1

            # Move position with overlap
            if self.chunk_overlap > 0:
                current_pos = chunk_end - self.chunk_overlap
            else:
                current_pos = chunk_end

        logger.info(
            f"Split document {document.filename} into {len(chunks)} chunks"
        )
        return chunks
