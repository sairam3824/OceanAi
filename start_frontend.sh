#!/bin/bash

# Start the frontend
echo "Starting QA Test Agent Frontend..."
echo "Frontend will be available at http://localhost:8501"
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

# Start the frontend
streamlit run frontend/app.py
