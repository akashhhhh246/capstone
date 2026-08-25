# ==============================================================================
# Multi-stage Dockerfile for Unified Full-Stack Deployment on Render
# Stage 1: Build React Frontend with Vite
# Stage 2: Production Python Runtime with Pre-trained Models & FastAPI Server
# ==============================================================================

# Stage 1: Frontend Build
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend source, data, and models
COPY backend/ /app/backend/
COPY models/ /app/models/

# Copy built frontend dist bundle into /app/frontend/dist so FastAPI serves it
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=9207 \
    ENVIRONMENT=production

WORKDIR /app/backend

# Initialize and seed database if necessary
RUN python -c "import seed_db; seed_db.seed_database(force_reseed=False)"

EXPOSE 9207

# Render will provide the PORT env var; start with uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-9207}"]
