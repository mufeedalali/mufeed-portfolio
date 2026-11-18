"""
CLI entry point for the RAG Pipeline.

Provides command-line interface for document ingestion and management.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import typer
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.api.dependencies import (
    get_ingestion_service,
    get_rag_service,
    get_settings_instance,
)

# Setup CLI
cli = typer.Typer(
    name="rag-cli",
    help="RAG Pipeline Command Line Interface",
)

logger = None


def init_logger():
    """Initialize logger."""
    global logger
    settings = get_settings()
    logger = setup_logging(
        log_level=settings.log_level,
        log_file="rag_cli.log",
        log_dir="./logs",
    )


@cli.command()
def ingest(
    file_path: str = typer.Argument(..., help="Path to document file to ingest"),
):
    """
    Ingest a single document file.

    Args:
        file_path: Path to document file
    """
    init_logger()
    logger.info(f"Ingesting file: {file_path}")

    async def run():
        try:
            path = Path(file_path)
            if not path.exists():
                typer.secho(f"Error: File not found: {file_path}", fg=typer.colors.RED)
                return

            ingestion_service = get_ingestion_service()
            task = await ingestion_service.ingest_file(file_path)

            typer.secho(f"✓ Document ingested successfully", fg=typer.colors.GREEN)
            typer.echo(f"Task ID: {task.id}")
            typer.echo(f"Document ID: {task.document_id}")
            typer.echo(f"Status: {task.status.value}")
            typer.echo(f"Progress: {task.progress_percent}%")

        except Exception as e:
            typer.secho(f"Error: {str(e)}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    asyncio.run(run())


@cli.command()
def ingest_dir(
    directory_path: str = typer.Argument(..., help="Path to directory with documents"),
):
    """
    Ingest all documents from a directory.

    Args:
        directory_path: Path to directory
    """
    init_logger()
    logger.info(f"Ingesting directory: {directory_path}")

    async def run():
        try:
            dir_path = Path(directory_path)
            if not dir_path.exists():
                typer.secho(
                    f"Error: Directory not found: {directory_path}",
                    fg=typer.colors.RED,
                )
                return

            ingestion_service = get_ingestion_service()
            tasks = await ingestion_service.ingest_directory(directory_path)

            typer.secho(f"✓ Ingested {len(tasks)} documents", fg=typer.colors.GREEN)

            for i, task in enumerate(tasks, 1):
                typer.echo(f"{i}. {task.document_id}: {task.status.value}")

        except Exception as e:
            typer.secho(f"Error: {str(e)}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    asyncio.run(run())


@cli.command()
def query(
    question: str = typer.Argument(..., help="Question to ask"),
    top_k: int = typer.Option(3, help="Number of results"),
):
    """
    Query the RAG pipeline.

    Args:
        question: Question to ask
        top_k: Number of results to retrieve
    """
    init_logger()
    logger.info(f"Query: {question}")

    async def run():
        try:
            rag_service = get_rag_service()
            response = await rag_service.query(question)

            typer.secho("\n=== RAG Response ===", fg=typer.colors.CYAN)
            typer.echo(f"\nQuestion: {response.query}")
            typer.echo(f"\nAnswer:\n{response.answer}")
            typer.echo(f"\nConfidence: {response.confidence_score:.2%}")
            typer.echo(f"Generation time: {response.generation_time_ms:.2f}ms")

            if response.sources:
                typer.secho("\nSources:", fg=typer.colors.YELLOW)
                for source in response.sources:
                    typer.echo(f"  - {source}")

            if response.retrieved_chunks:
                typer.secho("\nRetrieved Chunks:", fg=typer.colors.YELLOW)
                for i, chunk in enumerate(response.retrieved_chunks, 1):
                    typer.echo(f"\n{i}. {chunk.filename} ({chunk.similarity_score:.2%})")
                    typer.echo(f"   {chunk.content[:100]}...")

        except Exception as e:
            typer.secho(f"Error: {str(e)}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    asyncio.run(run())


@cli.command()
def status():
    """Get RAG pipeline status."""
    init_logger()

    async def run():
        try:
            rag_service = get_rag_service()
            stats = await rag_service.get_vector_store_stats()

            typer.secho("=== Vector Store Status ===", fg=typer.colors.CYAN)
            typer.echo(f"Total embeddings: {stats['total_embeddings']}")
            typer.echo(f"Total chunks: {stats['total_chunks']}")
            typer.echo(f"Total documents: {stats['total_documents']}")
            typer.echo(f"Store type: {stats['store_type']}")

        except Exception as e:
            typer.secho(f"Error: {str(e)}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    asyncio.run(run())


@cli.command()
def load_samples():
    """Load sample documents for testing."""
    init_logger()
    logger.info("Loading sample documents")

    async def run():
        try:
            settings = get_settings_instance()
            sample_dir = settings.sample_docs_path

            if not sample_dir.exists():
                typer.secho(f"Creating sample directory: {sample_dir}", fg=typer.colors.YELLOW)
                sample_dir.mkdir(parents=True, exist_ok=True)

                # Create sample documents
                sample_md = sample_dir / "sample_architecture.md"
                sample_md.write_text("""# System Architecture

## Overview
This document describes the architecture of the RAG Pipeline system.

## Components
1. **Document Loader**: Loads documents from various file formats
2. **Text Splitter**: Splits documents into manageable chunks
3. **Embedding Model**: Generates vector embeddings for text
4. **Vector Store**: Stores and retrieves embeddings
5. **LLM Service**: Generates responses using language models
6. **RAG Service**: Orchestrates the retrieval and generation process

## Data Flow
Documents → Loader → Splitter → Embeddings → Vector Store → RAG Service → LLM → Response
""")

                sample_txt = sample_dir / "sample_policy.txt"
                sample_txt.write_text("""Company Data Protection Policy

1. Data Classification
   - Public: Data that can be shared freely
   - Internal: Data for internal use only
   - Confidential: Sensitive business data
   - Restricted: Highly sensitive data

2. Data Handling
   - All data must be handled according to its classification
   - Access is restricted to authorized personnel only
   - Data must be encrypted in transit and at rest

3. Compliance
   - Regular audits are conducted to ensure compliance
   - Employees must complete annual training
   - Violations are subject to disciplinary action
""")

                typer.secho(
                    f"✓ Created sample documents in {sample_dir}",
                    fg=typer.colors.GREEN,
                )

            # Ingest samples
            ingestion_service = get_ingestion_service()
            tasks = await ingestion_service.ingest_directory(str(sample_dir))

            typer.secho(f"✓ Loaded {len(tasks)} sample documents", fg=typer.colors.GREEN)

        except Exception as e:
            typer.secho(f"Error: {str(e)}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    asyncio.run(run())


@cli.command()
def version():
    """Show version information."""
    settings = get_settings()
    typer.echo(f"{settings.app_name} v1.0.0")


def main():
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        typer.secho("\nInterrupted by user", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)


if __name__ == "__main__":
    main()
