# NotebookLM Clone

A RAG application where you upload documents and ask questions grounded in their content.
Answers include source citations. The system refuses to answer when the documents don't contain enough evidence.

## Tech Stack

- **Backend:** Python, FastAPI, ChromaDB, SentenceTransformers, PyMuPDF, OpenAI
- **Frontend:** React, TypeScript, Vite

## Prerequisites

- Python 3.11+
- Node.js 18+
- An OpenAI API key

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
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

> **Note:** start the backend first (port 8000) so the frontend can reach it.

## Using the frontend

1. Open http://localhost:5173 in your browser.
2. **Upload** — click the upload area or drag & drop a PDF, TXT, or Markdown file into the sidebar. The document name and chunk count appear in the list when processing finishes.
3. **Ask** — type a question in the input at the bottom and press **Enter** (or click **Ask**). Use **Shift+Enter** for a newline.
4. **Answer** — the answer appears in the main area. Each answer shows the source chunks used (filename, chunk index, similarity score, and a text snippet).
5. **Refusal** — if the uploaded documents don't contain enough evidence, the answer card is highlighted amber with an "Insufficient evidence" badge.

### Run backend tests

```bash
cd backend
source .venv/bin/activate
pytest
```

## Testing document upload

With the backend running, upload a file via curl:

```bash
# Upload a text file
curl -X POST http://localhost:8000/documents \
  -F "file=@/path/to/your/document.txt"

# Upload a PDF
curl -X POST http://localhost:8000/documents \
  -F "file=@/path/to/your/document.pdf"

# List uploaded documents
curl http://localhost:8000/documents
```

Or open http://localhost:8000/docs and use the interactive Swagger UI.

## Asking questions (POST /chat)

With at least one document uploaded, ask a grounded question:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

The response contains an `answer`, a list of `sources` (each with document_id,
filename, file_type, chunk_index, source label, snippet, and similarity), and a
`refused` flag.

The system refuses when the uploaded documents don't contain enough evidence.
Refusal is decided first by a retrieval gate (no chunks, or the best similarity
is below `min_similarity`, default 0.25) — in that case the LLM is not called at
all. A second prompt-level check lets the model itself refuse. On refusal,
`refused` is `true`, `sources` is empty, and the answer is exactly:

> I could not find enough evidence in the uploaded documents to answer this question.

## LLM provider

The app uses OpenAI for answer generation (default model: `gpt-4.1-mini`).
Set `OPENAI_API_KEY` in `backend/.env`. The model can be changed via the `LLM_MODEL`
environment variable.

## Local embeddings

The app uses [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
via SentenceTransformers for embeddings. The model (~90 MB) is downloaded from HuggingFace
automatically on first use and cached locally. No embedding API key needed.

ChromaDB persists the vector store to `backend/storage/chroma/` (gitignored).

## Project Structure

```
notebooklm-clone/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app, CORS, router registration
│   │   ├── config.py             # Settings via pydantic-settings
│   │   ├── api/
│   │   │   ├── health.py         # GET /health
│   │   │   ├── documents.py      # POST /documents, GET /documents
│   │   │   └── chat.py           # POST /chat
│   │   ├── core/
│   │   │   └── llm_client.py     # OpenAI client wrapper
│   │   ├── models/
│   │   │   └── schemas.py        # Pydantic request/response models
│   │   └── services/
│   │       ├── extraction.py     # Text extraction (PDF, TXT, Markdown)
│   │       ├── chunking.py       # Overlapping character chunking
│   │       ├── embeddings.py     # SentenceTransformers wrapper
│   │       ├── vector_store.py   # ChromaDB wrapper (add, query, delete)
│   │       ├── retrieval.py      # Question -> embedding -> top-k chunks
│   │       └── rag.py            # Source-grounded prompt, refusal, answer
│   ├── storage/                  # uploads/ and chroma/ (gitignored)
│   └── tests/
├── frontend/
│   └── src/
│       ├── types.ts              # Shared TypeScript types
│       ├── App.tsx               # Root layout (sidebar + chat area)
│       ├── App.css               # App layout and component styles
│       ├── index.css             # Global reset and CSS variables
│       ├── api/
│       │   └── client.ts         # fetch wrappers for backend API
│       └── components/
│           ├── UploadArea.tsx    # Drag & drop / click file upload
│           ├── DocumentList.tsx  # Uploaded document list in sidebar
│           ├── ChatPanel.tsx     # Chat history + question input
│           ├── AnswerView.tsx    # Single answer card with refused state
│           └── SourceList.tsx    # Source citation cards
└── docs/
    ├── architecture.md
    ├── demo-script.md
    └── prompts.md
```
