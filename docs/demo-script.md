# Demo Script — 5–8 Minute Loom Video

## Pre-Demo Checklist

- [ ] Backend running: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] Browser open at http://localhost:5173
- [ ] `sample_docs/everlast_ai_test.txt` ready to upload (drag-and-drop)
- [ ] Browser dev tools closed (clean screen)
- [ ] Terminal visible but not distracting

---

## Video Structure (7 minutes)

### 0:00 – 0:30 · Introduction (30 sec)

Say:
> "I built a NotebookLM-style RAG application as a coding assignment. I'll walk you through
> the product, the architecture, and how I used Claude Code to build it professionally."

Show: browser tab at http://localhost:5173 — clean empty state.

---

### 0:30 – 1:30 · Document Upload (60 sec)

**Action:** Drag `everlast_ai_test.txt` into the upload area.

Say:
> "The sidebar has a drag-and-drop upload area. I'm uploading a text document about
> Everlast AI — a German AI consulting company. When the upload finishes you can see the
> document name, the number of chunks it was split into, and the character count."

Point out:
- Document appears in the list with chunk count
- Upload was instant (local embedding, no API call for indexing)

**Optional:** Show `GET /documents` at http://localhost:8000/docs to demonstrate the API.

Say:
> "Under the hood, the backend extracted text, split it into 900-character overlapping chunks,
> generated embeddings locally using SentenceTransformers, and stored everything in ChromaDB."

---

### 1:30 – 3:30 · Asking a Question — Answered (2 min)

**Question 1 (ask in the chat input):**
> "Wer ist Chief AI Officer von Everlast AI?"

Expected answer: Leonard Schmedding is named as Co-Founder and Chief AI Officer.
Expected sources: 1–2 source cards, similarity scores visible.

Say:
> "The system retrieves the 4 most relevant chunks, constructs a source-grounded prompt,
> and asks OpenAI to answer strictly from that context. Here you can see the answer with
> its source citations — filename, chunk index, similarity score, and a text snippet."

**Question 2:**
> "Welche Business-Tools integriert Everlast AI?"

Expected answer: Google Analytics, HubSpot, Shopify, Stripe, Slack, Salesforce, etc.

Say:
> "Notice the sources below the answer. Each citation shows exactly which chunk of the
> document grounded that statement. This is the key demo point: the answer is never from
> the model's world knowledge — it is always traced back to the uploaded document."

---

### 3:30 – 4:30 · Refusal Behavior (60 sec)

**Refusal question:**
> "Wie hoch ist der aktuelle Aktienkurs von Apple?"

Expected: Amber-highlighted card with "Insufficient evidence" badge.
Expected: `refused: true` in the response.

Say:
> "Now I ask something that is not in the document. The system has two safety layers.
> First, a retrieval gate: if the best similarity score is below 0.25, the LLM is never
> called at all. Second, the system prompt instructs the model to use the exact refusal
> sentence if the context is insufficient. Either way, the response is the same clean
> refusal — and the UI makes it visually distinct."

**Second refusal question (optional):**
> "Was ist das Rezept für Tiramisu?"

This should also refuse — reinforcing the point.

---

### 4:30 – 5:30 · Architecture Walkthrough (60 sec)

Switch to `docs/architecture.md` or draw/narrate verbally.

Say:
> "The architecture is a clean two-service setup. The React frontend talks to a FastAPI
> backend over HTTP. The backend has a layered design: thin API routes delegate to service
> modules — extraction, chunking, embeddings, vector store, retrieval, and RAG."

Key points to mention:
- **No external embedding service** — all-MiniLM-L6-v2 runs locally on CPU
- **ChromaDB** persists vectors to disk — zero infrastructure
- **Two-stage refusal** — retrieval gate + prompt-level check
- **Temperature = 0** — deterministic, less creative, less hallucination risk

---

### 5:30 – 6:30 · Code Quality (60 sec)

Show briefly in VS Code or the terminal:
- `backend/app/services/rag.py` — highlight the refusal gate and LLMUnavailableError
- `backend/tests/` — mention 36 tests covering extraction, chunking, retrieval, RAG refusal
- `pytest` output in terminal

Say:
> "I wrote tests for the critical paths: text extraction, chunking correctness, metadata
> preservation, both refusal mechanisms, the API routes, and error handling when the LLM
> is unavailable. The test suite runs in under a second because expensive dependencies
> — torch, chromadb, openai — are lazy-loaded and mocked in tests."

---

### 6:30 – 7:00 · Claude Code Workflow (30 sec)

Say:
> "I used Claude Code as my pair programming assistant. The key was treating it as a
> senior colleague, not a code generator: I wrote a structured planning prompt first,
> approved the architecture, then implemented milestone by milestone. I used Opus for
> planning and reviews, Sonnet for implementation. Every output was reviewed before
> committing."

Point to `docs/prompts.md` if asked for details.

---

## Demo Questions Reference

### Questions that should be answered (with `everlast_ai_test.txt`)

| Question | Expected topic in answer |
|---|---|
| Wer ist Chief AI Officer von Everlast AI? | Leonard Schmedding |
| Was sind die wichtigsten Arbeitsbereiche? | KI-Strategie, Voice Agents, RAG-Pipelines, etc. |
| Welche Business-Tools werden integriert? | HubSpot, Shopify, Slack, Salesforce, etc. |
| Was betont Everlast AI beim Datenschutz? | DSGVO, EU AI Act, deutsche Rechenzentren |
| Welche Anwendungsfälle nennt Everlast AI? | Umsatzprognosen, Vertragsprüfung, etc. |

### Questions that should be refused

| Question | Reason |
|---|---|
| Wie hoch ist der Aktienkurs von Apple? | Nicht im Dokument |
| Was ist das Rezept für Tiramisu? | Völlig unrelated |
| Wer ist der CEO von Google? | Nicht im Dokument |
| Wie heißt die Hauptstadt von Frankreich? | Allgemeinwissen, nicht im Dokument |

---

## Tips for a Smooth Recording

- Upload the document first, wait for it to appear in the list before asking questions.
- Keep the browser window large so source cards are readable.
- After asking a question, briefly pause to let the answer load before speaking.
- If the LLM is slow, say: "It's calling the OpenAI API — in production this would be streamed."
- Don't rush the refusal demo — the amber card is visually distinctive and worth pausing on.
