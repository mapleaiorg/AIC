#!/bin/bash

echo "🍁 Starting Maple AI Companion Backend v2.0..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before running!"
    exit 1
fi

# Run database migrations
echo "🗄️  Initializing database..."
python -c "
import asyncio
from app.database import init_db
asyncio.run(init_db())
"

# Start the server
echo "🚀 Starting server..."
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
