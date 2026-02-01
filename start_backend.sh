#!/bin/bash

# Start the backend API
echo "Starting QA Test Agent Backend..."
echo "API will be available at http://localhost:8000"
echo ""

# Check if virtual environment exists or is already active
if [ ! -d "ocenai" ] && [ ! -d "venv" ] && [ ! -d ".venv" ] && [ -z "$VIRTUAL_ENV" ] && [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "❌ No virtual environment or active environment detected."
    echo ""
    echo "Setup instructions:"
    echo "  1. Create environment: python -m venv venv"
    echo "  2. Activate:           source venv/bin/activate"
    echo "  3. Install:            pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "ocenai" ]; then
    source ocenai/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found."
    echo "Please create a .env file and add your OPENAI_API_KEY."
    exit 1
fi

# Check for placeholder key
if grep -q "OPENAI_API_KEY=youopenaikey" .env; then
    echo "⚠️ Warning: OPENAI_API_KEY is using the placeholder 'youopenaikey'."
    echo "Please edit your .env file and add your real OpenAI API key to use AI features."
    echo ""
fi

# Start the backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
