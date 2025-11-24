#!/bin/bash

# Development server başlatma scripti

echo "🚀 Google Search Bot başlatılıyor..."

# Backend'i arka planda başlat
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Frontend'i başlat
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Backend: http://localhost:8000"
echo "✅ Frontend: http://localhost:3000"
echo "✅ API Docs: http://localhost:8000/docs"
echo ""
echo "Durdurmak için Ctrl+C"

# Process'leri temizle
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

# Bekle
wait

