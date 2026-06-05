You are my senior software architect and Claude Code pair programmer.

We are building a professional but focused NotebookLM-style clone for an interview assignment.

Context:
I already have VS Code, WSL, and Claude Code set up. The goal is not to build the biggest possible application, but to build a clean, explainable, demo-ready MVP that shows strong software engineering, RAG understanding, source-grounded answering, and professional use of Claude Code.

Project Goal:
Build a small NotebookLM-style RAG application where users can upload documents and ask questions about them.

The application must:

* allow users to upload PDF, TXT, and Markdown documents
* extract text from uploaded documents
* split documents into meaningful overlapping chunks
* create embeddings for chunks
* store chunks and metadata in a local vector database
* retrieve relevant chunks for a user question
* answer only using the retrieved document context
* show sources/citations for each answer
* refuse to answer when the uploaded documents do not contain enough evidence
* provide a clean and simple React frontend
* provide a FastAPI backend
* be easy to present in a 5–8 minute interview video

Preferred Tech Stack:

* Backend: Python, FastAPI
* Frontend: React, TypeScript, Vite
* Vector store: ChromaDB
* RAG pipeline: lightweight custom pipeline, using LangChain only where it clearly helps
* PDF parsing: pypdf or pymupdf
* Testing: pytest for backend
* Code quality: clear structure, simple modules, no over-engineering
* Documentation: README.md, docs/architecture.md, docs/demo-script.md, docs/prompts.md

Important Engineering Principles:

* Keep the MVP small but high quality
* Prefer clear and maintainable code over clever abstractions
* Separate responsibilities clearly
* Keep API routes thin
* Put business logic into services/modules
* Never commit secrets or API keys
* Use .env and .env.example
* Add tests for critical logic
* Include source metadata with every retrieved chunk
* The system must not answer from general world knowledge
* If evidence is insufficient, it must clearly say that the uploaded documents do not provide enough information
* The final project must be easy to explain in an interview

Interview Focus:
The project should demonstrate:

* RAG architecture
* source-grounded answering
* anti-hallucination strategy
* clean software architecture
* practical MVP scoping
* testability
* professional documentation
* responsible use of AI coding tools
* ability to guide Claude Code with structured prompts instead of blindly generating code

Non-Goals:
Do not plan for:

* user login/authentication
* multi-user system
* cloud deployment as a required MVP feature
* payment features
* complex notebook management
* audio overview generation
* advanced UI animations
* many file formats beyond PDF/TXT/Markdown
* enterprise-grade permissions
* over-engineered microservices

Your task now:
Create a detailed implementation plan before writing any code.

The plan must include:

1. MVP Scope

* What exactly will be included?
* What will be intentionally excluded?

2. Architecture

* Explain the backend, frontend, RAG pipeline, storage, and data flow.
* Keep it simple and professional.

3. Recommended Folder Structure

* Propose a clear project folder structure.
* Include backend, frontend, docs, sample documents, and config files.

4. Backend Design

* List the FastAPI routes.
* List the backend modules.
* Explain responsibilities of each module.

5. Frontend Design

* Explain the main UI layout.
* Include document upload area, document list, chat area, answer area, and source display.

6. RAG Pipeline
   Explain the complete flow:

* upload
* text extraction
* chunking
* embedding
* vector storage
* retrieval
* prompt construction
* answer generation
* source display

7. Anti-Hallucination Strategy
   Explain exactly how the system will reduce hallucinations:

* source-grounded prompt
* retrieved-only context
* citations
* refusal behavior
* insufficient evidence handling
* metadata tracking

8. Testing Strategy
   Define focused tests for:

* text extraction
* chunking
* metadata preservation
* retrieval
* refusal when evidence is insufficient
* API routes where useful

9. Demo and Video Strategy
   Define:

* what sample document should be used
* what demo questions should be asked
* one question that should be answered
* one question that should be refused
* how to explain the architecture in a 5–8 minute Loom video

10. Risks and Tradeoffs
    Identify risks such as:

* PDF parsing quality
* weak retrieval
* too much scope
* LLM hallucination
* API key handling
* demo instability

For each risk, propose a simple mitigation.

11. Implementation Milestones
    Break the work into small milestones:

* Milestone 1: project setup and backend health endpoint
* Milestone 2: document upload and text extraction
* Milestone 3: chunking and vector store
* Milestone 4: retrieval and source-grounded answer service
* Milestone 5: frontend MVP
* Milestone 6: tests and quality pass
* Milestone 7: documentation and demo preparation

12. Claude Code Workflow
    Explain how I should use Claude Code professionally:

* when to use planning mode
* when to approve changes
* how to keep tasks small
* how to ask for review
* when to use a stronger model for reasoning
* when a faster model is enough for implementation

Rules:

* Do not write code yet.
* Do not create files yet.
* Do not implement anything yet.
* First produce only the implementation plan.
* Explain the plan in German.
* Future code, filenames, comments, tests, documentation, and commit messages should be written in English.
* Keep the plan practical and focused on finishing a strong MVP for an interview.
* If something seems too large for the MVP, explicitly mark it as out of scope.

## Fixed MVP Decisions

Use these decisions for the implementation unless I explicitly say otherwise:

- Use local SentenceTransformers embeddings for the MVP.
- Use the embedding model: all-MiniLM-L6-v2.
- Use PyMuPDF for PDF text extraction.
- Use chunk_size = 900 characters.
- Use chunk_overlap = 150 characters.
- Use top_k = 4 for retrieval.
- Use Claude Sonnet for answer generation in the app.
- Use stronger reasoning models only for planning, architecture review, RAG review, and final code review.
- Use low temperature for answer generation to make responses more deterministic and less creative.
- Keep the MVP small, reliable, and demo-ready.
- Do not implement features outside the defined MVP unless I explicitly approve them.