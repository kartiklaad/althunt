#!/bin/bash

# Run script for Altitude Huntsville Party Booking Assistant

echo "🎉 Starting Altitude Huntsville Party Booking Assistant"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Please copy .env.example to .env and fill in your API keys"
    echo ""
fi

# Start FastAPI backend in background
echo "🚀 Starting FastAPI backend..."
cd "$(dirname "$0")"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start Streamlit frontend
echo "🎨 Starting Streamlit frontend..."
streamlit run app.py

# Cleanup: kill backend when streamlit exits
kill $BACKEND_PID 2>/dev/null

