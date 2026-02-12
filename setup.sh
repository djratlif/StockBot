#!/bin/bash

# StockBot Setup Script
# This script recreates the development environment after cleanup

echo "🚀 Setting up StockBot development environment..."

# Backend setup
echo "📦 Setting up Python backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Backend dependencies installed"
cd ..

# Frontend setup
echo "📦 Setting up React frontend..."
cd frontend
npm install
echo "✅ Frontend dependencies installed"
cd ..

echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload --port 8000"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "Or use the provided start scripts:"
echo "- ./start.sh (Linux/Mac)"
echo "- start.bat (Windows)"