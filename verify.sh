#!/bin/bash

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run Unit Tests
echo "Running Mathematical Validation Tests..."
python3 -m unittest tests/test_math.py

# Check for .env
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found. Please copy .env.example to .env and add your API keys."
    echo "GITHUB_TOKEN=..." > .env.example
    echo "GEMINI_API_KEY=..." >> .env.example
    echo "Created .env.example"
fi
