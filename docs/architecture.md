# Architecture

## Overview

NotebookLM Clone is a source-grounded RAG (Retrieval-Augmented Generation) application.
Users upload documents, the system indexes them locally, and answers questions using only
the content of the uploaded documents — with explicit source citations and a hard refusal
when the evidence is insufficient.

```
┌─────────────────────────────────────────────────────┐
│                     Browser                         │
│   React + TypeScript + Vite  (localhost:5173)       │
│                                                     │
│  ┌─────────────┐   ┌───────────────────────────┐   │
│  │  Sidebar    │   │       Chat Panel           │   │
│  │  ─────────  │   │  ─────────────────────────│   │
│  │  Upload     │   │  Question bubble           │   │
│  │  Doc list   │   │  Answer card               │   │
│  │  (delete)   │   │  Source cards              │   │
│  └─────────────┘   └───────────────────────────┘   │
└───────────────────────────┬─────────────────────────┘
                            │ fetch (JSON / multipart)
                            ▼
┌─────────────────────────────────────────────────────┐
│               FastAPI Backend  (localhost:8000)      │
│                                                     │
│   POST /documents   GET /documents   DELETE /docs   │
│   POST /chat        GET /health                     │
│                                                     │
│  api/ (thin routes) → services/ (business logic)   │
└──────────┬──────────────────────────┬───────────────┘
           │                          │
  ┌────────▼─────────┐    ┌──────────▼──────────────┐
  │  Local Disk      │    │  ChromaDB (cosine)       │
  │  ─────────────── │    │  ──────────────────────  │
  │  storage/uploads │    │  storage/chroma/         │
  │  *.meta.json     │    │  document_chunks         │
  └──────────────────┘    │  (text + embedding +     │
                          │   metadata per chunk)    │
                          └─────────────────────────-┘
```

---

## Component Responsibilities

### Frontend (`frontend/src/`)

| File | Responsibility |
|---|---|
| `App.tsx` | Root layout, global state (documents, chat history, loading flags) |
| `api/client.ts` | `fetch` wrappers for all three backend endpoints |
| `components/UploadArea.tsx` | Drag-&-drop / click upload, loading + error state |
| `components/DocumentList.tsx` | Sidebar document list with per-item delete |
| `components/ChatPanel.tsx` | Chat history (scrollable), question input, Enter-to-send |
| `components/AnswerView.tsx` | Answer card, refused/normal state |
| `components/SourceList.tsx` | Source citation cards (filename, chunk, similarity, snippet) |

### Backend (`backend/app/`)

| Layer | Module | Responsibility |
|---|---|---|
| `api/` | `documents.py` | Route logic for upload, list, delete |
| `api/` | `chat.py` | Route logic for chat; translates LLM errors to HTTP 503 |
| `api/` | `health.py` | `GET /health` heartbeat |
| `services/` | `extraction.py` | Text extraction from PDF (PyMuPDF), TXT, Markdown |
| `services/` | `chunking.py` | Overlapping character-based chunking with metadata |
| `services/` | `embeddings.py` | SentenceTransformers wrapper (lazy-loaded, cached) |
| `services/` | `vector_store.py` | ChromaDB wrapper: add, query, delete |
| `services/` | `retrieval.py` | Question → embedding → top-k chunks from ChromaDB |
| `services/` | `rag.py` | Source-grounded prompt, two-stage refusal, answer |
| `core/` | `llm_client.py` | OpenAI SDK wrapper (lazy-loaded) |
| `models/` | `schemas.py` | Pydantic request/response models |
| `config.py` | — | Centralised settings via `pydantic-settings` |

---

## Upload Flow

```
User selects file
       │
       ▼
POST /documents (multipart/form-data)
       │
       ▼
Validate extension (.pdf / .txt / .md / .markdown)
       │
       ▼
Save raw file → storage/uploads/{uuid}.{ext}
       │
       ▼
extraction.py → plain text string
       │
  ┌────┴────────────────────────────────┐
  │  If empty or unreadable → 422       │
  └────────────────────────────────────┘
       │
       ▼
chunking.py
  chunk_size = 900 chars, overlap = 150 chars
  Each chunk carries: document_id, filename, file_type,
                      chunk_index, source label
       │
       ▼
embeddings.py  →  SentenceTransformers all-MiniLM-L6-v2
  Produces 384-dimensional float vectors (local, no API key)
       │
       ▼
vector_store.py  →  ChromaDB PersistentClient
  Stores: text, embedding, metadata per chunk
       │
       ▼
Write {uuid}.meta.json  →  DocumentResponse persisted
       │
       ▼
Return DocumentResponse (201)
```

---

## RAG / Chat Flow

```
User types question
       │
       ▼
POST /chat  { "question": "..." }
       │
       ▼
retrieval.py
  Embed question with all-MiniLM-L6-v2
  Query ChromaDB  →  top_k = 4 chunks (cosine similarity)
  similarity = 1 − cosine_distance
       │
  ┌────┴─────────────────────────────────────────────┐
  │  PRIMARY REFUSAL GATE                             │
  │  if no chunks  OR  chunks[0].similarity < 0.25:  │
  │      refused = True, LLM is NOT called           │
  └──────────────────────────────────────────────────┘
       │ (evidence is sufficient)
       ▼
rag.py  →  build prompt:
  system: strict rules — answer only from context,
          refuse with exact sentence if insufficient
  user:   [Source 1: filename [chunk N]]
          <chunk text>

          [Source 2: …]
          …

          Question: <user question>
       │
       ▼
llm_client.py  →  OpenAI gpt-4.1-mini
  temperature = 0.0  (deterministic)
  max_tokens  = 1024
       │
  ┌────┴─────────────────────────────────────────────┐
  │  SECONDARY REFUSAL CHECK                         │
  │  if answer == REFUSAL_MESSAGE:                   │
  │      refused = True, sources = []                │
  └──────────────────────────────────────────────────┘
       │
  ┌────┴─────────────────────────────────────────────┐
  │  LLM ERROR HANDLING                              │
  │  if OpenAI call raises exception:                │
  │      HTTP 503 with human-readable message        │
  └──────────────────────────────────────────────────┘
       │
       ▼
Return ChatResponse { answer, sources, refused }
  Each source: document_id, filename, chunk_index,
               similarity, snippet (first 200 chars)
```

---

## Anti-Hallucination Strategy

The system uses three complementary mechanisms to prevent hallucinated answers:

**1. Retrieval gate (no LLM call when evidence is weak)**
Before the LLM is called, the best similarity score is checked against `min_similarity`
(default 0.25). If no chunks are found, or the top chunk falls below this threshold,
the system returns a fixed refusal message without ever invoking the LLM.
This is the primary and most reliable safety net.

**2. Source-grounded system prompt**
The system prompt instructs the model to answer *only* from the provided context blocks
and explicitly forbids using prior or world knowledge. If the context is insufficient,
the model must respond with exactly the refusal sentence — and nothing else.

**3. Prompt-level refusal detection**
If the LLM returns the exact refusal sentence, the system recognises this as a
model-initiated refusal: `refused` is set to `true`, sources are cleared, and the
UI highlights the card in amber.

**4. Source citations in every answer**
Every non-refused answer includes the source chunks (filename, chunk index, similarity
score, text snippet) that grounded the answer. The user can inspect exactly what the
model read.

---

## Data Storage

| Location | Contents | Git status |
|---|---|---|
| `backend/storage/uploads/` | Raw uploaded files + `.meta.json` per document | gitignored |
| `backend/storage/chroma/` | ChromaDB persistent vector store | gitignored |
| `backend/.env` | `OPENAI_API_KEY` | gitignored |
| `sample_docs/` | Demo documents for testing | committed |

---

## Technology Choices and Rationale

| Choice | Why |
|---|---|
| **FastAPI** | Fast to build, auto-generates OpenAPI docs, async-capable |
| **ChromaDB** | Zero-config local vector store, no external service needed |
| **all-MiniLM-L6-v2** | 384-dim, fast, ~90 MB, runs on CPU, no API key needed |
| **PyMuPDF** | Reliable PDF text extraction, faster than pypdf |
| **OpenAI gpt-4.1-mini** | Strong instruction-following, low cost, deterministic at temp=0 |
| **Character-based chunking** | Simple, predictable, no tokeniser dependency |
| **pydantic-settings** | Centralised, type-safe config with `.env` support |
| **Lazy imports** | Avoids loading torch/chromadb/openai in tests — keeps suite fast |
