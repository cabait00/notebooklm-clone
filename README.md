# NotebookLM Clone

A RAG application where you upload documents and ask questions grounded in their content.
Answers include source citations. The system refuses to answer when the documents don't contain enough evidence.

## Tech Stack

- **Backend:** Python, FastAPI, ChromaDB, SentenceTransformers, PyMuPDF, Anthropic Claude
- **Frontend:** React, TypeScript, Vite

## Prerequisites

- Python 3.11+
- Node.js 18+
- An Anthropic API key

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.
Interactive docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173.

### Run backend tests

```bash
cd backend
source .venv/bin/activate
pytest
```

## Project Structure

```
notebooklm-clone/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, router registration
│   │   ├── config.py        # Settings via pydantic-settings
│   │   └── api/
│   │       └── health.py    # GET /health
│   └── tests/
├── frontend/
│   └── src/
│       └── App.tsx
└── docs/
    ├── architecture.md
    ├── demo-script.md
    └── prompts.md
```
