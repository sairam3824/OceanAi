#!/bin/bash

# Start the backend API
echo "Starting QA Test Agent Backend..."
echo "API will be available at http://localhost:8000"
echo ""

# Check if virtual environment exists
if [ ! -d "ocenai" ]; then
    echo "Virtual environment not found. Please run setup first:"
    echo "  python -m venv ocenai"
    echo "  source ocenai/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source ocenai/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your OPENAI_API_KEY"
    exit 1
fi

# Start the backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
