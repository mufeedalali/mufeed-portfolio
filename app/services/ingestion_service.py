"""
Document ingestion service.

Orchestrates document loading, splitting, embedding, and storage.
"""

import asyncio
from typing import List, Dict, Any
from pathlib import Path
from app.core.exceptions import IngestionError
from app.domain.models import Document, TextChunk, Embedding, IngestionTask, ProcessingStatus
from app.infrastructure.document_loaders import DocumentLoaderFactory
from app.infrastructure.text_splitter import RecursiveCharacterSplitter
from app.infrastructure.embeddings import DeterministicEmbedding
from app.infrastructure.vector_store import InMemoryVectorStore
from app.core.logging import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)


class IngestionService:
    """
    Service for ingesting documents into the RAG pipeline.

    Handles document loading, chunking, embedding generation, and storage.
    """

    def __init__(
        self,
        document_loader: DocumentLoaderFactory,
        text_splitter: RecursiveCharacterSplitter,
        embedding_model: DeterministicEmbedding,
        vector_store: InMemoryVectorStore,
    ):
        """
        Initialize ingestion service.

        Args:
            document_loader: Document loader factory
            text_splitter: Text splitter implementation
            embedding_model: Embedding model
            vector_store: Vector store for embeddings
        """
        self.document_loader = document_loader
        self.text_splitter = text_splitter
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.tasks: Dict[str, IngestionTask] = {}
        logger.info("Initialized IngestionService")

    async def ingest_file(self, file_path: str) -> IngestionTask:
        """
        Ingest a single document file.

        Args:
            file_path: Path to document file

        Returns:
            IngestionTask: Task tracking ingestion progress

        Raises:
            IngestionError: If ingestion fails
        """
        task_id = str(uuid.uuid4())
        task = IngestionTask(
            id=task_id,
            document_id="",
            status=ProcessingStatus.PENDING,
            progress_percent=0,
        )
        self.tasks[task_id] = task

        try:
            logger.info(f"Starting ingestion of file: {file_path}")

            # Load document
            task.status = ProcessingStatus.PROCESSING
            task.progress_percent = 10
            document = await self.document_loader.load(file_path)
            task.document_id = document.id
            logger.info(f"Loaded document: {document.filename}")

            # Split into chunks
            task.progress_percent = 30
            chunks = await self.text_splitter.split(document)
            logger.info(f"Split document into {len(chunks)} chunks")

            # Generate embeddings
            task.progress_percent = 50
            embeddings = await self._generate_embeddings(chunks)
            logger.info(f"Generated {len(embeddings)} embeddings")

            # Store embeddings
            task.progress_percent = 80
            await self.vector_store.add_embeddings(embeddings, chunks)
            logger.info(f"Stored {len(embeddings)} embeddings in vector store")

            # Mark complete
            task.status = ProcessingStatus.COMPLETED
            task.progress_percent = 100
            task.updated_at = datetime.now()
            logger.info(f"Successfully ingested document: {document.filename}")

            return task

        except Exception as e:
            task.status = ProcessingStatus.FAILED
            task.error_message = str(e)
            task.updated_at = datetime.now()
            logger.error(f"Failed to ingest file {file_path}: {str(e)}")
            raise IngestionError(f"Failed to ingest file: {str(e)}")

    async def ingest_directory(self, directory_path: str) -> List[IngestionTask]:
        """
        Ingest all documents from a directory.

        Args:
            directory_path: Path to directory

        Returns:
            List[IngestionTask]: List of ingestion tasks

        Raises:
            IngestionError: If directory ingestion fails
        """
        try:
            logger.info(f"Starting directory ingestion: {directory_path}")
            tasks = []
            dir_path = Path(directory_path)

            if not dir_path.exists():
                raise IngestionError(f"Directory not found: {directory_path}")

            for file_path in dir_path.glob("*"):
                if file_path.is_file():
                    try:
                        task = await self.ingest_file(str(file_path))
                        tasks.append(task)
                    except Exception as e:
                        logger.warning(f"Failed to ingest {file_path.name}: {str(e)}")

            logger.info(f"Ingested {len(tasks)} documents from {directory_path}")
            return tasks

        except Exception as e:
            logger.error(f"Failed to ingest directory {directory_path}: {str(e)}")
            raise IngestionError(f"Failed to ingest directory: {str(e)}")

    async def _generate_embeddings(self, chunks: List[TextChunk]) -> List[Embedding]:
        """
        Generate embeddings for text chunks.

        Args:
            chunks: List of text chunks

        Returns:
            List[Embedding]: List of embeddings
        """
        embeddings = []

        for chunk in chunks:
            vector = await self.embedding_model.embed(chunk.content)
            embedding = Embedding(
                chunk_id=chunk.id,
                vector=vector,
                model=self.embedding_model.model_name,
                dimension=self.embedding_model.get_dimension(),
            )
            embeddings.append(embedding)

        return embeddings

    async def get_task_status(self, task_id: str) -> IngestionTask:
        """
        Get status of an ingestion task.

        Args:
            task_id: ID of task

        Returns:
            IngestionTask: Task status

        Raises:
            IngestionError: If task not found
        """
        if task_id not in self.tasks:
            raise IngestionError(f"Task not found: {task_id}")

        return self.tasks[task_id]

    async def get_all_tasks(self) -> List[IngestionTask]:
        """
        Get all ingestion tasks.

        Returns:
            List[IngestionTask]: List of all tasks
        """
        return list(self.tasks.values())

    async def clear_completed_tasks(self) -> int:
        """
        Clear completed tasks from memory.

        Returns:
            int: Number of tasks cleared
        """
        completed_ids = [
            task_id
            for task_id, task in self.tasks.items()
            if task.status == ProcessingStatus.COMPLETED
        ]

        for task_id in completed_ids:
            del self.tasks[task_id]

        logger.info(f"Cleared {len(completed_ids)} completed tasks")
        return len(completed_ids)
