# Frontend — NotebookLM Clone

React + TypeScript + Vite frontend for the NotebookLM Clone RAG application.

## Stack

- React 19, TypeScript, Vite
- No UI component library — plain CSS with custom design system
- Fetch API for all backend calls (no axios or React Query)

## Development

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # production build + TypeScript check
```

The backend must be running at `http://localhost:8000` before using the frontend.
See the root `README.md` for backend setup instructions.

## Structure

```
src/
├── types.ts              # Shared TypeScript types (DocumentResponse, Source, ChatEntry)
├── App.tsx               # Root layout and global state
├── App.css               # All component and layout styles
├── index.css             # Global reset and CSS variables (light + dark mode)
├── api/
│   └── client.ts         # fetch wrappers: uploadDocument, listDocuments,
│                         #                deleteDocument, askQuestion
└── components/
    ├── UploadArea.tsx     # Drag-&-drop / click file upload
    ├── DocumentList.tsx   # Uploaded document list with delete button
    ├── ChatPanel.tsx      # Chat history + question input
    ├── AnswerView.tsx     # Answer card, refused state highlighted in amber
    └── SourceList.tsx     # Source citation cards
```
