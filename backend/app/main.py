from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import chat, documents, health

app = FastAPI(title="NotebookLM Clone API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(documents.router, tags=["documents"])
app.include_router(chat.router, tags=["chat"])

# Serve the built frontend as static files. Mounted LAST so the API routes
# above take precedence. In the Docker image the build output lives at
# /app/static (see Dockerfile); locally this directory is absent, so the
# guard keeps `uvicorn app.main:app` working unchanged during development.
_frontend_dir = Path(__file__).resolve().parent.parent / "static"
if _frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
