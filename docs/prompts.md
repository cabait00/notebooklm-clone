# Claude Code Usage — Prompts and Workflow

This document records how Claude Code was used as a development tool throughout this
project. The goal was to demonstrate responsible, professional use of AI coding assistance:
structured prompts, staged approvals, and critical review at every step.

---

## Guiding Principle

Claude Code was used as a **senior pair programmer**, not a code generator.
Every output was reviewed before committing. Prompts were scoped to one milestone at a time.
No code was accepted blindly — architecture was approved before implementation began.

---

## Model Strategy

| Task | Model used | Reason |
|---|---|---|
| Initial planning prompt | Claude Opus | Complex architectural reasoning across 12 dimensions |
| Milestone implementation | Claude Sonnet | Fast, reliable for well-scoped coding tasks |
| Quality review (Milestone 6) | Claude Opus | Critical analysis, cross-file reasoning |
| Code changes after review | Claude Sonnet | Surgical, well-defined changes |

---

## Key Prompts

### 1 · Initial Architecture Planning Prompt

The session started with a highly structured prompt that asked Claude to produce a
complete implementation plan **before writing any code**. Key elements:

- Explicit role definition: "You are my senior software architect and Claude Code pair programmer."
- 12 required sections: MVP scope, architecture, folder structure, backend design, frontend
  design, RAG pipeline, anti-hallucination strategy, testing strategy, demo strategy,
  risks and tradeoffs, implementation milestones, Claude Code workflow.
- Hard constraint: "Do not write code yet. Do not create files yet. Do not implement anything."
- Language instruction: "Explain the plan in German. Future code in English."

**Why this worked:** Forcing a plan first prevented premature implementation. The structured
sections ensured nothing important was skipped. Reviewing the plan in German created
natural distance between planning and implementation, reducing the temptation to accept
vague reasoning.

---

### 2 · Milestone Implementation Prompts

Each milestone was implemented with a dedicated prompt that contained:

- **Context:** "Milestones 1–N are complete and committed."
- **Scope:** Exactly what this milestone should build (no more, no less).
- **Technical constraints:** Specific file names, function signatures, API contracts.
- **Quality constraints:** "TypeScript must compile. pytest must pass. npm run build must pass."
- **Boundary clause:** "Do not continue to Milestone N+1 until I approve."

Example structure (Milestone 5 — Frontend):
```
Current backend endpoints: GET /health, POST /documents, GET /documents, POST /chat
Frontend requirements:
- Keep the UI simple, clean, and demo-friendly.
- Create a NotebookLM-inspired layout: left sidebar / main chat area.
- frontend/src/api/client.ts for backend API calls
- frontend/src/types.ts for shared frontend types
[... specific component list ...]
Quality requirements:
- TypeScript should compile.
- npm run build should pass.
[...]
After implementation:
- Explain changes in German.
- Show changed files.
- Do not continue with Milestone 6 until I approve.
```

**Why this worked:** Small, scoped milestones made each output reviewable in full.
The "do not continue" boundary clause prevented runaway implementation. Requiring a German
explanation after each milestone forced Claude to surface its reasoning for review.

---

### 3 · Cleanup / Feature Extension Prompts

Minor features (e.g., document deletion) were added with explicit scope boundaries:

```
Milestone 5 cleanup: delete uploaded documents from the UI.
[...]
Do not implement authentication.
Do not implement streaming.
Do not change the RAG/chat behavior.
Do not change the OpenAI provider.
Do not start Milestone 6.
```

Negative constraints ("do not X") were as important as positive requirements.
They prevented scope creep and kept the diff small and reviewable.

---

### 4 · Quality Review Prompt (Milestone 6)

Before implementing any fixes, a **review-only** prompt was used:

```
First, do a review only. Do not modify files yet.

Please review the project for:
1. Architecture quality
2. Separation of concerns
3. RAG correctness
[... 11 dimensions ...]

Then produce a prioritized action plan with:
- Critical fixes, if any
- Important improvements
- Nice-to-have improvements
- What should remain out of scope

Important:
- Do not implement anything yet.
- Do not modify files yet.
```

**Why this worked:** Separating review from implementation prevented Claude from
fixing things that didn't need fixing. The prioritised action plan allowed human
judgment to decide what to implement before any file was changed.

---

### 5 · Scoped Milestone 6A Implementation Prompt

After approving the review findings, only a subset was implemented:

```
Now implement Milestone 6A only: stability and demo documentation polish.

Scope:
1. Chat error handling [specific requirements]
2. Documentation [specific files and content requirements]
3. Provider consistency [specific changes]
4. CORS polish [specific change]
5. Demo polish only

Out of scope:
- No authentication.
- No streaming.
- No Docker.
[...]
```

**Why this worked:** The review identified 11 findings. Only 5 were implemented.
The explicit out-of-scope list prevented over-engineering. The MVP remained focused.

---

## Key Lessons from This Workflow

1. **Plan before code.** A structured planning prompt with an explicit "no code yet"
   constraint produced a better architecture than iterative generation would have.

2. **Review before merge.** Every generated diff was read in full. Several small
   improvements were caught this way (unused imports, wrong comments, missing tests).

3. **Scope constraints beat general instructions.** "Do not implement authentication"
   is more reliable than "keep the MVP small."

4. **Parallel tool calls improve efficiency.** When reading multiple files before
   making changes, grouping reads into one message cuts round-trips significantly.

5. **German explanations after English code.** Requiring post-implementation summaries
   in a different language forced Claude to reason about what it had done, not just
   describe the code. This surfaced non-obvious decisions.

6. **Smaller models for implementation, larger for reasoning.** Claude Sonnet for
   well-defined coding tasks; Claude Opus for architectural review and ambiguous
   cross-file analysis. This saved cost without sacrificing quality where it mattered.
