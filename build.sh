#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=========================================================="
echo "  AEGIS DEFENSE PLATFORM - RENDER DEPLOYMENT BUILD SCRIPT "
echo "=========================================================="

echo "==> Step 1: Building Frontend React SPA Bundle..."
cd frontend
npm install --include=dev
npm run build
cd ..

echo "==> Step 2: Upgrading pip and installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

echo "==> Step 3: Verifying Database Seed & Pre-trained Artifacts..."
cd backend
python -c "import os; print('Checking model paths...'); from app.infrastructure.configuration.config import settings; print('TFIDF:', os.path.exists(settings.TFIDF_MODEL_PATH)); print('GNN:', os.path.exists(settings.GNN_MODEL_PATH))"
cd ..

echo "=========================================================="
echo "  BUILD SUCCEEDED! READY FOR UVICORN PRODUCTION START     "
echo "=========================================================="
