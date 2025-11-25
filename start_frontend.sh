#!/bin/bash

# Start the frontend
echo "Starting QA Test Agent Frontend..."
echo "Frontend will be available at http://localhost:8501"
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

# Start the frontend
streamlit run frontend/app.py
