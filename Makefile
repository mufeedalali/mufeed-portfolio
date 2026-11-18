"""Makefile for RAG Pipeline development tasks."""

.PHONY: help setup install test run dev clean lint format type-check

help:
	@echo "RAG Pipeline Development Tasks"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup       - Full setup with venv and dependencies"
	@echo "  make install     - Install Python dependencies"
	@echo "  make test        - Run test suite"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo "  make run         - Run production server"
	@echo "  make dev         - Run development server with reload"
	@echo "  make cli         - Run interactive CLI"
	@echo "  make lint        - Run linters (ruff, mypy)"
	@echo "  make format      - Format code with black"
	@echo "  make clean       - Remove build artifacts and cache"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run  - Run Docker container"

setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	mkdir -p data/uploads data/vector_db logs
	cp .env.example .env

install:
	pip install -r requirements.txt

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html tests/
	@echo "Coverage report generated in htmlcov/index.html"

run:
	uvicorn app.api.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

cli:
	python -m cli.main

lint:
	ruff check app cli tests
	mypy app

format:
	black app cli tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build dist

docker-build:
	docker build -t rag-pipeline:latest .

docker-run:
	docker-compose up
