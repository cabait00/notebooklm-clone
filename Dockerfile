# syntax=docker/dockerfile:1

# ---- Stage 1: build the React frontend ----
FROM node:20-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# VITE_API_BASE is intentionally unset -> the app calls the API same-origin.
RUN npm run build

# ---- Stage 2: backend + bundled frontend ----
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies first for better layer caching.
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model so the first request is fast and the
# container does not need network access to Hugging Face at runtime.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Backend source -> /app/app, requirements already copied above.
COPY backend/ ./

# Built frontend -> /app/static (matches _frontend_dir in app/main.py).
COPY --from=frontend /app/frontend/dist ./static

# Hugging Face Spaces routes traffic to port 7860 by default.
ENV PORT=7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
