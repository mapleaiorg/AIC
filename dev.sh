#!/bin/bash

echo "🛠️  Starting Maple AI in development mode..."

# Install development dependencies
pip install pytest pytest-asyncio httpx black flake8 mypy

# Run linting
echo "🔍 Running code quality checks..."
black . --check
flake8 . --max-line-length=100
mypy . --ignore-missing-imports

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v

# Start with hot reload
echo "🚀 Starting development server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
