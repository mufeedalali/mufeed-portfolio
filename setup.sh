#!/bin/bash
# Setup script for RAG Pipeline

set -e

echo "Setting up RAG Pipeline..."

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data/uploads
mkdir -p data/vector_db
mkdir -p logs

# Create .env file from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ".env file created. Please update with your settings if needed."
fi

echo "Setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  uvicorn app.api.main:app --reload"
echo ""
echo "To run the CLI:"
echo "  python -m cli.main --help"
echo ""
echo "To run tests:"
echo "  pytest"
